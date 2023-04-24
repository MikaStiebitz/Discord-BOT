import discord
from discord.ext import commands
import psutil

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="ping", description="Pong!")
    async def ping(self, ctx):
        embed = discord.Embed(
            title=f"{self.client.user.name} latency",
            color=discord.Color.blurple())
        embed.add_field(name="🤖BOT Latency",
                        value=f"{str(round(self.client.latency * 1000))}ms", inline=False)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def serverinfo(self, ctx):
        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = "Server Information"
        data = ""
        data += str(psutil.cpu_count()) + " total threads \n"
        data += f"{psutil.virtual_memory().total / 2**30:.2f}" + \
            " GB Total Memory \n"
        data += f"{psutil.virtual_memory().available / 2**30:.2f}" + \
            " GB Available Currently \n"
        
        embed.description = data
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def cpu(self, ctx):
        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = "CPU Information"
        embed.description = str(psutil.cpu_percent(
            interval=1)) + "% CPU Usage \n"
        embed.description += str(psutil.getloadavg()
                                 [1]) + " average load over the last 5 minutes"
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def server(self, ctx):
        embed = discord.Embed(title = f"{ctx.guild.name} Info", description = "Information of this Server", color = discord.Color.blurple())
        embed.add_field(name = "📆Created On", value = ctx.guild.created_at.strftime("%b %d %Y"), inline = True)
        embed.add_field(name = "👑Owner", value = f"{ctx.guild.owner}", inline = True)
        embed.add_field(name = "👥Members", value = f"{ctx.guild.member_count} Members", inline = True)
        embed.add_field(name = "💬Channels", value = f"{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice", inline = True)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Info(client))