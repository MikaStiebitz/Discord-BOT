import re
import discord
import wavelink
from config import Auth
from discord.ext import commands
from wavelink.player import TrackEventPayload
from discord.ui import Select, View
import asyncio

class MusicButtonView(discord.ui.View):
    def __init__(self, vc, history, prevent_skip):
        super().__init__()
        self.vc = vc
        self.history = history
        self.prevent_skip = prevent_skip
        self.is_playing = True

    @discord.ui.button(emoji="⏮️", row=0, style=discord.ButtonStyle.gray)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc.current == self.history[-1]:
            self.history.pop()

        last_song = self.history.pop()
        self.prevent_skip = True
        
        await self.vc.play(last_song)
        
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
        if self.vc.queue.is_empty:
            await interaction.response.send_message("There are no more tracks!")
            return 
        
        self.clear_items()
        await interaction.response.edit_message(view=self)

        next_song = self.vc.queue.get()
        await self.vc.play(next_song)
        await interaction.followup.send(f"Now playing: {next_song.title} ({next_song.author})", view=MusicButtonView(self.vc, self.history, self.prevent_skip))


    @discord.ui.button(emoji="🔇", row=1, style=discord.ButtonStyle.gray)
    async def mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.vc.set_volume(0)
        await interaction.response.defer()

    @discord.ui.button(emoji="🔉", row=1, style=discord.ButtonStyle.gray)
    async def lower(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.vc.set_volume(self.vc.volume - 10)
        await interaction.response.defer()

    @discord.ui.button(emoji="🔊", row=1, style=discord.ButtonStyle.gray)
    async def higher(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.vc.set_volume(self.vc.volume + 10)
        await interaction.response.defer()

    @discord.ui.button(emoji="🔀", row=2, style=discord.ButtonStyle.gray)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(self.vc.queue.get())
        self.vc.queue.shuffle()
        print(self.vc.queue.get())
        await interaction.response.defer()

    @discord.ui.button(emoji="⏹️", row=2, style=discord.ButtonStyle.gray)
    async def stopbtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.vc.disconnect()
        await interaction.response.defer()

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.gray, row=2)
    async def loop(self, interaction: discord.Interaction,  button: discord.Button):
        
        try:

            vc = self.vc

            if vc.is_playing() is False: return await interaction.response.send_message("h5i")

            if not hasattr(vc, "loop"):
                setattr(vc, "loop", False)

            if vc.loop == False:
                vc.loop = True
                return await interaction.response.send_message("hi4")

            else:
                vc.loop = False
                await interaction.response.send_message("hi")
                
            await interaction.response.defer()

        except Exception as error:
            print(error)


class MusicCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.now_playing_message = None
        self.index = None
        self.history = list()
        self.seen_titles = set()
        self.unique_tracks = []
        self.prevent_skip = False
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

            print(payload.player.current)
            print("Track end")
            
            if hasattr(self, 'last_ctx'):
                await self.last_ctx.send("Track ended")

                if not payload.player.queue.is_empty:
                    tracks = payload.player.queue.get()
                    
                    await payload.player.play(tracks)


                    if self.now_playing_message:
                        await self.now_playing_message.delete()
                        
                        message = await self.last_ctx.send(f"Now playing: {tracks.title} ({tracks.author})", view=MusicButtonView(payload.player, self.history, self.prevent_skip))
                        self.now_playing_message = message
                else:
                    await asyncio.sleep(10)
                    if payload.player.queue.is_empty and not payload.player.is_playing():
                        await payload.player.disconnect()
                        if self.now_playing_message:
                            await self.now_playing_message.delete()

        

    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, *, music: str, nr: int = None):
        self.last_ctx = ctx
        if music is None:
            return await ctx.replay("Please provide a song name or link to search for.")
        
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
            
        

        if re.match(r"^(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+", music):
            track = await wavelink.YouTubeTrack.search(music)
            track = track[0]
        else:
            
                tracks = await wavelink.YouTubeTrack.search(music)
                
                if not tracks:
                    await ctx.send("No search results found.")
                    return
                
                self.unique_tracks.clear()
                self.seen_titles.clear()
                for track in tracks:
                    if track.title in self.seen_titles:
                        continue
                        
                    self.unique_tracks.append(track)
                    
                    self.seen_titles.add(track.title)
                if not nr:
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
                else:
                    track = self.unique_tracks[nr]

        if vc.is_playing():
            self.history.append(track)
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
            print("play")
            self.history.append(track)
            await vc.play(track)
            message = await ctx.send(f"Now playing: {track.title} ({track.author})", view=MusicButtonView(vc, self.history, self.prevent_skip))
            self.now_playing_message = message

    @commands.hybrid_command()
    async def stop(self, ctx: commands.Context):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()
        

    @commands.hybrid_command()
    async def skip(self, ctx):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            await ctx.reply("There are no more tracks!")
            return 
        self.current_track = vc.queue.get()
        self.prevent_skip = True
        await vc.play(self.current_track)

    @commands.hybrid_command()
    async def prev(self, ctx):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        if not self.history:
            await ctx.send("There are no previous songs.")
            return
        
        if vc.current == self.history[-1]:
            self.history.pop()

        last_song = self.history.pop()
        
        await vc.play(last_song)
        
        await ctx.send(f"Now playing the previous song: {last_song}")
    
    @commands.hybrid_command()
    async def shuffle(self, ctx):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            await ctx.reply("There are no more tracks!")
            return 
        vc.queue.shuffle()
        await ctx.send("Queue shuffled!")

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