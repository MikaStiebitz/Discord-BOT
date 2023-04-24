from modules.BankFunctions import *
import discord
from datetime import datetime
from discord.ext import commands

class MainBank(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(aliases=["bal", "money"], usage=f"")
    @commands.guild_only()
    async def balance(self, ctx):
        user = ctx.author
        user_av = user.display_avatar or user.default_avatar
        if user.bot:
            return await ctx.reply("Bots don't have accounts", mention_author=False)
        await open_bank(user)

        users = await get_bank_data(user)
        wallet_amt = users[1]

        em = discord.Embed(
            description=f"Wallet: {wallet_amt}",
            color=0x00ff00
        )
        em.set_author(name=f"{user.name}'s Balance", icon_url=user_av.url)
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(usage="<member: @member> <amount: integer>")
    @commands.guild_only()
    async def send(self, ctx, member: discord.Member, amount: int):
        if member.bot:
            return await ctx.reply("Bots don't have accounts", mention_author=False)

        await open_bank(ctx.author)
        await open_bank(member)

        sender_data = await get_bank_data(ctx.author)
        receiver_data = await get_bank_data(member)
        sender_wallet_amt = sender_data["wallet"]
        sender_bank_amt = sender_data["bank"]
        if amount <= 0:
            return await ctx.reply("Enter a valid amount!", mention_author=False)
        if amount > sender_wallet_amt + sender_bank_amt:
            return await ctx.reply("You don't have enough amount", mention_author=False)

        if amount > sender_wallet_amt:
            await update_bank(ctx.author, sender_wallet_amt - amount)
            await update_bank(ctx.author, sender_bank_amt - (amount - sender_wallet_amt))
        else:
            await update_bank(ctx.author, sender_wallet_amt - amount)
        await update_bank(member, amount)
        await ctx.reply(f"You sent {amount:,} to {member.mention}", mention_author=False)


    @commands.hybrid_command(aliases=["lb"])
    @commands.guild_only()
    async def leaderboard(self, ctx):
        users = await get_networth_lb()
        data = []
        index = 1
        for member in users:
            if index > 10:
                break
            member_name = self.client.get_user(member[0])
            member_amt = member[1]

            if index == 1:
                msg1 = f"**🥇 `{member_name}` -- {member_amt}**"
                data.append(msg1)
            if index == 2:
                msg2 = f"**🥈 `{member_name}` -- {member_amt}**"
                data.append(msg2)
            if index == 3:
                msg3 = f"**🥉 `{member_name}` -- {member_amt}**\n"
                data.append(msg3)
            if index >= 4:
                members = f"**{index} `{member_name}` -- {member_amt}**"
                data.append(members)
            index += 1

        msg = "\n".join(data)
        em = discord.Embed(
            title="Leaderboard",
            description=f"**Top {index - 1} Richest Users**\n\n{msg}",
            color=discord.Color(0x00ff00),
            timestamp=datetime.utcnow()
        )
        em.set_footer(text=f"GLOBAL - {ctx.guild.name}")
        await ctx.reply(embed=em, mention_author=False)

    @commands.hybrid_command(name="daily", description="Get your daily bonus")
    @commands.cooldown(1, 60*60*24, commands.BucketType.user)
    async def daily(self, ctx):
        await open_bank(ctx.author)
        await update_bank(ctx.author, +1000)

        await ctx.send("They were successfully transferred **1.000€** to their account")

    @commands.hybrid_command(name="work", description="Work bonus, every 3 hours")
    @commands.cooldown(1, 60*60*3, commands.BucketType.user)
    async def work(self, ctx):
        await open_bank(ctx.author)
        await update_bank(ctx.author, +250)

        await ctx.send("You successfully scammed 3 people with the Microsoft call center and earned **100€**.")

    @daily.error
    async def command_name_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            total_seconds = error.retry_after
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            em = discord.Embed(title=f"Slow it down bro!",description=f"Try again in {hours} hours and {minutes} minutes.", color=15471379)
            await ctx.send(embed=em)

    @work.error
    async def command_name_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            total_seconds = error.retry_after
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            em = discord.Embed(title=f"Slow it down bro!",description=f"Try again in {hours} hours and {minutes} minutes.", color=15471379)
            await ctx.send(embed=em)
            
async def setup(client):
    await client.add_cog(MainBank(client))
