import discord
from discord.ext import commands
from modules.BankFunctions import *
from modules.PrefixFunctions import *

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="prefix", description="Set custom Prefix")
    @commands.is_owner()
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

    @commands.hybrid_command(usage="<member*: @member> <amount*: integer>")
    @commands.is_owner()
    @commands.cooldown(3, 2 * 30, commands.BucketType.user)
    async def addmoney(self, ctx, member: discord.Member, amount: str):
        if member.bot:
            return await ctx.reply("You can't add money to a bot", mention_author=False)
        if not amount.isdigit() or int(amount) <= 0:
            return await ctx.reply("Please enter a valid amount")

        limit = 100_000
        amount = int(amount)
        if amount > limit:
            return await ctx.reply(f"You cannot add money more than {limit:,}")

        await open_bank(member)
        await update_bank(member, +amount)
        await ctx.reply(f"You added {amount:,} in {member.mention}'s", mention_author=False)

    @commands.hybrid_command(usage="<member*: @member> <amount*: integer>")
    @commands.is_owner()
    @commands.cooldown(3, 2 * 30, commands.BucketType.user)
    async def remoney(self, ctx, member: discord.Member, amount: str):
        if member.bot:
            return await ctx.reply("You can't remove money from a bot", mention_author=False)
        if not amount.isdigit() or int(amount) <= 0:
            return await ctx.reply("Please enter a valid amount")

        amount = int(amount)
        await open_bank(member)

        user_amt = await get_bank_data(member)
        if user_amt < amount:
            return await ctx.reply(
                f"You can only remove {user_amt:,} from {member.mention}'s"
            )

        await update_bank(member, -amount)
        await ctx.reply(f"You removed {amount:,} from {member.mention}'s", mention_author=False)

async def setup(client):
    await client.add_cog(Admin(client))