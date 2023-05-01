import re
import discord
import wavelink
from config import Auth
from discord.ext import commands


class MusicButtonView(discord.ui.View):
    def __init__(self, vc, message):
        super().__init__()
        self.vc = vc
        self.is_playing = True
        self.message = message

    @discord.ui.button(emoji="⏮️", row=0, style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji="⏯️", row=0, style=discord.ButtonStyle.gray)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_playing:
            await self.vc.pause()
            self.is_playing = False
            await interaction.response.defer()
        else:
            await self.vc.resume()
            self.is_playing = True
            await interaction.response.defer()

    @discord.ui.button(emoji="⏭️", row=0, style=discord.ButtonStyle.gray)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji="🔇", row=1, style=discord.ButtonStyle.gray)
    async def mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji="🔉", row=1, style=discord.ButtonStyle.gray)
    async def lower(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji="🔊", row=1, style=discord.ButtonStyle.gray)
    async def higher(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji="🔀", row=2, style=discord.ButtonStyle.gray)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji="⏹️", row=2,
                       style=discord.ButtonStyle.gray)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.vc.disconnect()
        await interaction.response.defer()

    @discord.ui.button(emoji="🔁", row=2, style=discord.ButtonStyle.gray)
    async def repeat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = wavelink.Queue()
        self.wavelink_nodes = [
            wavelink.Node(uri=f"http://{Auth.LAVALINK_HOST}:{Auth.LAVALINK_PORT}", password=f"{Auth.LAVALINK_PASSWORD}")
        ]
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.connect(client=self.bot, nodes=self.wavelink_nodes)

    @wavelink.WavelinkMixin
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track):
        ctx = player.ctx
        vc: player = ctx.voice_client
        if vc.loop:
            return await vc.play(track)
        
        next_song = vc.queue.get()
        await vc.play(next_song)
        await ctx.send(f"Now playing {next_song.title}")

    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, *, music: str):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        if re.match(r"^(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+", music):
            track = await wavelink.YouTubeTrack.search(music, return_first=True)
        else:
            tracks = await wavelink.YouTubeTrack.search(music)
            if not tracks:
                await ctx.send("No search results found.")
                return

            embed = discord.Embed(title="Search Results", color=discord.Color.blurple())
            for i, track in enumerate(tracks[:5]):
                embed.add_field(name=f"{i+1}. {track.title}", value=track.author, inline=False)

            message = await ctx.send(embed=embed)

            reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            for reaction in reactions[:len(tracks)]:
                await message.add_reaction(reaction)

            def check(reaction, user):
                print(user == ctx.author and str(reaction.emoji) in reactions[:len(tracks)])
                return user == ctx.author and str(reaction.emoji) in reactions

            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=lambda r, u: r.message.id == message.id and u.id == ctx.author.id and str(r.emoji) in reactions)
            track = tracks[reactions.index(str(reaction.emoji))]
            await message.delete()

        if vc.is_playing():
            print("queue")

            vc.queue.put(item=track)

            await ctx.send(embed=discord.Embed(
                title=track.title,
                url=track.uri,
                author=ctx.author,
                description=f"Queued {track.title} in {vc.channel}"
            ))
        else:
            await vc.play(track)
            message = await ctx.send(f"Now playing: {track.title} ({track.author})")
            view = MusicButtonView(vc, message)
            message = await ctx.send(view=view)

    @commands.command()
    async def stopMusic(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()

    @commands.command()
    async def skip(self, ctx):
        print("skip")
        vc = ctx.voice_client
        if vc:
            if not vc.is_playing():
                return await ctx.send("Nothing is playing.")
            if vc.queue.is_empty:
                return await vc.stop()

            await vc.seek(vc.track.length * 1000)
            if vc.is_paused():
                await vc.resume()
        else:
            await ctx.send("The bot is not connected to a voice channel.")


    @commands.command()
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc:
            if vc.is_playing() and not vc.is_paused():
                await vc.pause()
            else:
                await ctx.send("Nothing is playing.")
        else:
            await ctx.send("The bot is not connected to a voice channel")


    @commands.command()
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                await vc.resume()
            else:
                await ctx.send("Nothing is paused.")
        else:
            await ctx.send("The bot is not connected to a voice channel")

async def setup(client):
    await client.add_cog(MusicCog(client))