import discord
import wavelink
from discord.ext import commands

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
        """Simple play command."""

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        await vc.play(track)

    @commands.command()
    async def disconnect(self, ctx: commands.Context) -> None:
        """Simple disconnect command.

        This command assumes there is a currently connected Player.
        """
        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()

async def setup(client):
    await client.add_cog(MusicCog(client))