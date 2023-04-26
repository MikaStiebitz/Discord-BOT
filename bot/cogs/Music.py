import discord
import wavelink
from discord.ext import commands
import re
import asyncio
from urllib.parse import urlparse, parse_qs


class MusicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.wavelink_nodes = [
            wavelink.Node(uri='http://narco.buses.rocks:2269', password='glasshost1984')
        ]
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.connect(client=self.bot, nodes=self.wavelink_nodes)

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        # Check if the input is a valid YouTube link
        video_id = None
        if re.match(r'^(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+', search):
            video_id = parse_qs(urlparse(search).query)['v'][0]
            track = await wavelink.YouTubeTrack(video_id)
        else:
            tracks = await wavelink.YouTubeTrack.search(search)
            if not tracks:
                await ctx.send("No search results found.")
                return

            # Send a message with the search results
            embed = discord.Embed(title="Search Results", color=discord.Color.blurple())
            for i, track in enumerate(tracks[:5]):
                embed.add_field(name=f"{i+1}. {track.title}", value=track.author, inline=False)

            message = await ctx.send(embed=embed)

            # Add reactions to the message and wait for user input
            reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            for reaction in reactions[:len(tracks)]:
                await message.add_reaction(reaction)

            def check(reaction, user):
                print(user == ctx.author and str(reaction.emoji) in reactions[:len(tracks)])
                return user == ctx.author and str(reaction.emoji) in reactions

            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=lambda r, u: r.message.id == message.id and u.id == ctx.author.id and str(r.emoji) in reactions)
            track = tracks[reactions.index(str(reaction.emoji))]
            await message.delete()

        # Play the selected video
        
        await vc.play(track)

        message = await ctx.channel.send(f"Now playing: {track.title} ({track.author})")
        await message.add_reaction("⏸️")
        await message.add_reaction("▶️")
        await message.add_reaction("⏹️")

        def check(reaction, user):
            return str(reaction.emoji) in ["⏸️", "▶️", "⏹️"] and user == ctx.author

        while vc.is_playing():
            print("playing")
            reaction, user = await self.bot.wait_for("reaction_add", check=check)


            await message.remove_reaction(reaction, user)
            print(str(reaction.emoji))
            if str(reaction.emoji) == "⏸️":
                print("pause")
                await vc.pause()
            elif str(reaction.emoji) == "▶️":
                print("play")
                await vc.resume()
            elif str(reaction.emoji) == "⏹️":
                await vc.stop()
                await message.edit(content="Song stopped.")

        await ctx.send("Playback ended.")
        await vc.disconnect()



    @commands.command()
    async def disconnect(self, ctx: commands.Context) -> None:
        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()

async def setup(client):
    await client.add_cog(MusicCog(client))