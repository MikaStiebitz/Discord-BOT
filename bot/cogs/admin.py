import discord
from discord.ext import commands
from modules.BankFunctions import *
from modules.PrefixFunctions import *

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="prefix", description="Set custom Prefix")
    async def prefix(self, ctx, prefix: str):
        if len(prefix) <= 10:
            await update_prefix(ctx.message.guild.id, prefix)
            embed = discord.Embed(
                title=f"New Prefix: '{prefix}'",
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Prefix Error!",
                description="Prefix should be less than 10 characters",
                color=15471379)
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
async def setup(client):
    await client.add_cog(Admin(client))