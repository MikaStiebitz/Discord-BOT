import re
import discord
import wavelink
from config import Auth
from discord.ext import commands
from wavelink.player import TrackEventPayload
from discord.ui import Select, View
import asyncio

class MusicButtonView(discord.ui.View):
    def __init__(self, vc):
        super().__init__()
        self.vc = vc
        self.is_playing = True

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
        track = self.vc.player.queue.get()
        await self.vc.player.play(track)
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
        self.now_playing_message = None
        self.index = None
        self.seen_titles = set()
        self.unique_tracks = []
        self.wavelink_nodes = [
            wavelink.Node(uri=f"http://{Auth.LAVALINK_HOST}:{Auth.LAVALINK_PORT}", password=f"{Auth.LAVALINK_PASSWORD}")
        ]
        self.bot.loop.create_task(self.connect_nodes())
        self.queue = wavelink.Queue()

    async def connect_nodes(self):
        try:
            await self.bot.wait_until_ready()
            await wavelink.NodePool.connect(client=self.bot, nodes=self.wavelink_nodes)
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEventPayload):
        try:
            track = payload.player.queue.get()
            await payload.player.play(track)
            if self.now_playing_message:
                await self.now_playing_message.delete()
                message = await self.ctx.send(f"Now playing: {track.title} ({track.author})", view=MusicButtonView(payload.player))
                self.now_playing_message = message
        except:
            print("end")

            await payload.player.disconnect()
            if self.now_playing_message:
                await self.now_playing_message.delete()

    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, *, music: str):
        self.ctx = ctx
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
            
            
            for track in tracks:
                if track.title in self.seen_titles:
                    continue
                    
                self.unique_tracks.append(track)
                
                self.seen_titles.add(track.title)

            embed = discord.Embed(title="Search Results", color=discord.Color.blurple())
            for i, track in enumerate(self.unique_tracks[:5]):
                embed.add_field(name=f"{i+1}. {track.title}", value=track.author, inline=False)

            options = [discord.SelectOption(label=track.title) for track in self.unique_tracks[:5]]

            select = Select(
                placeholder="Choose a Song!",
                options=options
            )
            
            async def my_callback(interaction):
                self.index = select.values[0]
                await interaction.response.defer()
                event.set()

            viewSel = View()
            viewSel.add_item(select)

            select.callback = my_callback
            message = await ctx.send(embed=embed, view=viewSel)

            event = asyncio.Event()
            await event.wait()

            for i, item in enumerate(self.unique_tracks[:5]):
                if item.title == self.index:
                    track = self.unique_tracks[i]
                    await message.delete()
                break

        if vc.is_playing():
            print("queue")
            embed = discord.Embed(
                title=track.title,
                url=track.uri,
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed)

            await vc.queue.put_wait(track)


        else:
            await vc.play(track)
            message = await ctx.send(f"Now playing: {track.title} ({track.author})", view=MusicButtonView(vc))
            self.now_playing_message = message

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