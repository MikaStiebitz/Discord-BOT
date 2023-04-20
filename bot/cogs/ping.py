import discord
from discord.ext import commands
from discord import app_commands

class Pong(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(
        name="ping",
        description="Pong!")
    async def ping_slash(self, interaction: discord.Interaction):
        embed=discord.Embed(title=f"My ping is {self.client.latency} :ping_pong: ", color=0xf21c1c)
        await interaction.response.send_message(embed=embed)



    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            title=f'{self.client.user.name} latency',
            color=0x00FFFF)
        embed.add_field(name="🤖BOT Latency",
                        value=f"{str(round(self.client.latency * 1000))}ms", inline=False)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def emoji(self, ctx):
        emojis = ctx.guild.emojis
        emoji_ids = [str(emoji) for emoji in emojis]
        await ctx.send("\n".join(emoji_ids))


async def setup(client):
    await client.add_cog(Pong(client))