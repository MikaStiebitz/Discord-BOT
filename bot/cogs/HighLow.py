import discord
from discord.ext import commands
import csv
import random
import datetime
import typing
from modules.BankFunctions import *
from modules.PrefixFunctions import *

class Highlow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.hybrid_command(name="highlow", description="Guess if Higher or Lower")
    async def highlow(self, ctx, bet: int, choice: typing.Optional[str] = None):
        prefix = await get_prefix(ctx.message.guild.id)
        game = self.games.get(ctx.author.id)
        user = ctx.author
        money = await get_bank_data(user)
        if not game:
            await open_bank(user)
            if bet <= 0:
                await ctx.send("Please enter a valid bet.")
                return
            
            if money[1] < bet:
                return await ctx.reply("Not enough Money on your account :C")
            
            game = {
                "player": ctx.author,
                "bet": bet,
                "multiplier": 1,
                "min_number": 1,
                "max_number": 10
            }
            self.games[ctx.author.id] = game
            if choice:
                if choice.lower() == "low":
                    await self.low(ctx)
                elif choice.lower() == "high":
                    await self.high(ctx)
            else:
                await ctx.send(f"Guess if number is high or low. **{prefix}low** or **{prefix}high**")
        else:
            await ctx.send("You are already playing Highlow")

    @commands.command()
    async def low(self, ctx):
        game = self.games.get(ctx.author.id)
        if not game:
            no_game_embed = discord.Embed(title=f"Not in game!", color=15471379)
            await ctx.send(embed=no_game_embed)
            return
        number = random.randint(game["min_number"], game["max_number"])
        if number < 5:
            game["last_number"] = number
            await self.win(ctx, game)
        else:
            game["last_number"] = number
            await self.lose(ctx, game)

    @commands.command()
    async def high(self, ctx):
        game = self.games.get(ctx.author.id)
        if not game:
            no_game_embed = discord.Embed(title=f"Not in game!", color=15471379)
            await ctx.send(embed=no_game_embed)
            return
        number = random.randint(game["min_number"], game["max_number"])
        if number > 5:
            game["last_number"] = number
            await self.win(ctx, game)
        else:
            game["last_number"] = number
            await self.lose(ctx, game)

    async def win(self, ctx, game):
        prefix = await get_prefix(ctx.message.guild.id)
        last_num = game["last_number"]
        game["multiplier"] = game["multiplier"] * 2
        val_multiplier = game["multiplier"]

        user_name = ctx.author.display_name

        embed = discord.Embed(title=f"Highlow - User: {user_name}", color=3274303)
        embed.add_field(name="Correct!", value=f"Number was **{last_num}**\n**Continue**\nUse {prefix}low or {prefix}high", inline=True)
        embed.add_field(name="Multiplier", value=f"**{val_multiplier}x**", inline=True)

        embed.set_footer(text=f"Use {prefix}stop to stop the Game.")
        await ctx.send(embed=embed)

    async def lose(self, ctx, game):
        bet = game["bet"]
        last_num = game["last_number"]
        user = ctx.author
        user_name = ctx.author.display_name
        balance = await get_bank_data(user)

        await update_bank(user, -bet)
    
        embed = discord.Embed(title=f"Highlow - User: {user_name}", color=15471379)
        embed.add_field(name="Incorrect!", value=f"Number was **{last_num}**\n**Money**\nYou have {balance[1]}€", inline=True)
        embed.add_field(name="Profit", value=f"**-{bet}**€", inline=True)

        await ctx.send(embed=embed)
        del self.games[game["player"].id]

    @commands.command()
    async def stopGame(self, ctx):
        game = self.games.get(ctx.author.id)
        user = ctx.author
        balance = await get_bank_data(user)
        user_name = ctx.author.display_name
        val_multiplier = game["multiplier"]
        bet = game["bet"]
        winnings = bet * val_multiplier
        bet = game["bet"]

        if not game:
            no_game_embed = discord.Embed(title=f"Not in game!", color=15471379)
            await ctx.send(embed=no_game_embed)
            return

        await update_bank(user, +winnings)
        del self.games[game["player"].id]

        embed = discord.Embed(title=f"Highlow - User: {user_name}", color=3274303)
        embed.add_field(name="Stopped at", value=f"**{val_multiplier}x**\n**Money**\nYou have {balance[1]}€", inline=True)
        embed.add_field(name="Profit", value=f"**{winnings}**€", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Highlow(bot))