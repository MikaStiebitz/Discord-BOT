import discord
from discord.ext import commands
import csv
import random
import datetime

class Highlow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command()
    async def highlow(self, ctx, bet: int):
        game = self.games.get(ctx.author.id)
        if not game:
            if bet <= 0:
                await ctx.send("Please enter a valid bet.")
                return
            if bet > self.get_balance(ctx.author):
                await ctx.send("Not enough Money on your account :C")
                return
            game = {
                "player": ctx.author,
                "bet": bet,
                "multiplier": 1,
                "min_number": 1,
                "max_number": 10
            }
            self.games[ctx.author.id] = game
            await ctx.send("Guess if number is high or low. **!low** or **!high**")
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
        bet = game["bet"]
        last_num = game["last_number"]
        multiplier = game["multiplier"]
        winnings = bet * multiplier
        self.add_balance(game["player"], winnings)
        game["multiplier"] = game["multiplier"] * 2
        val_multiplier = game["multiplier"]

        user_name = ctx.author.display_name

        embed = discord.Embed(title=f"Highlow - User: {user_name}", color=3274303)
        embed.add_field(name="Correct!", value=f"Number was **{last_num}**\n**Continue**\nUse !low or !high", inline=True)
        embed.add_field(name="Multiplier", value=f"**{val_multiplier}x**", inline=True)

        embed.set_footer(text="Use !stop to stop the Game.")
        await ctx.send(embed=embed)
        
        game["min_number"] = max(game["min_number"] - 1, 1)
        game["max_number"] = min(game["max_number"] + 1, 10)

    async def lose(self, ctx, game):
        bet = game["bet"]
        last_num = game["last_number"]
        user_name = ctx.author.display_name
        balance = self.get_balance(ctx.author)

        self.subtract_balance(game["player"], bet)
    
        embed = discord.Embed(title=f"Highlow - User: {user_name}", color=15471379)
        embed.add_field(name="Incorrect!", value=f"Number was **{last_num}**\n**Money**\nYou have {balance}€", inline=True)
        embed.add_field(name="Profit", value=f"**-{bet}**€", inline=True)

        await ctx.send(embed=embed)
        del self.games[game["player"].id]

    @commands.command()
    async def stop(self, ctx):
        game = self.games.get(ctx.author.id)
        balance = self.get_balance(ctx.author)
        user_name = ctx.author.display_name
        val_multiplier = game["multiplier"]
        bet = game["bet"]
        winnings = bet * val_multiplier
        bet = game["bet"]

        if not game:
            no_game_embed = discord.Embed(title=f"Not in game!", color=15471379)
            await ctx.send(embed=no_game_embed)
            return
        self.save_data()
        del self.games[game["player"].id]

        embed = discord.Embed(title=f"Highlow - User: {user_name}", color=3274303)
        embed.add_field(name="Stopped at", value=f"**{val_multiplier}x**\n**Money**\nYou have {balance}€", inline=True)
        embed.add_field(name="Profit", value=f"**{winnings}**€", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def money(self, ctx):
        balance = self.get_balance(ctx.author)
        await ctx.send(f"You have **{balance}€**.")

    @commands.command()
    async def work(self, ctx):
        user_id = str(ctx.author.id)
        now = datetime.datetime.now()

        with open("data/last_work.csv", "r") as file:
            reader = csv.reader(file)
            rows = [row for row in reader]

        index = -1
        for i, row in enumerate(rows):
            if row[0] == user_id:
                index = i
                break

        if index != -1:
            last_work_time = datetime.datetime.fromisoformat(rows[index][1])
            time_since_last_work = now - last_work_time

            if time_since_last_work < datetime.timedelta(hours=3):
                time_until_next_work = datetime.timedelta(hours=3) - time_since_last_work
                hours = time_until_next_work.seconds // 3600
                minutes = (time_until_next_work.seconds // 60) % 60
                await ctx.send(f"You will not be able to work at Microsoft support for another **{hours}** hours and **{minutes}** minutes.")
            else:
                self.add_balance(ctx.author, 100)
                rows[index][1] = now.isoformat()
                with open("data/last_work.csv", "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)
                await ctx.send("You successfully scammed 3 people with the Microsoft call center and earned **100€**.")
        else:
            self.add_balance(ctx.author, 100)
            with open("data/last_work.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([user_id, now.isoformat()])
            await ctx.send("You successfully scammed 3 people with the Microsoft call center and earned **100€**.")

    @commands.command()
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        now = datetime.datetime.now()

        with open("data/last_daily.csv", "r") as file:
            reader = csv.reader(file)
            rows = [row for row in reader]

        index = -1
        for i, row in enumerate(rows):
            if row[0] == user_id:
                index = i
                break

        if index != -1:
            last_daily_time = datetime.datetime.fromisoformat(rows[index][1])
            time_since_last_daily = now - last_daily_time

            if time_since_last_daily < datetime.timedelta(hours=24):
                time_until_next_daily = datetime.timedelta(hours=24) - time_since_last_daily
                hours = time_until_next_daily.seconds // 3600
                minutes = (time_until_next_daily.seconds // 60) % 60
                await ctx.send(f"Your daily bonus is ready in **{hours}** hours and **{minutes}** minutes.")
            else:
                self.add_balance(ctx.author, 1000)
                rows[index][1] = now.isoformat()
                with open("data/last_daily.csv", "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)
                await ctx.send("They were successfully transferred **1.000€** to their account")
        else:
            self.add_balance(ctx.author, 1000)
            with open("data/last_daily.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([user_id, now.isoformat()])
            await ctx.send("They were successfully transferred **1.000€** to their account")

    def get_balance(self, user):
        with open("data/balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    return int(row[1])
        self.add_balance(user, 250)
        return 250

    def add_balance(self, user, amount):
        balances = []
        with open("data/balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    balances.append([user.id, int(row[1]) + amount])
                else:
                    balances.append(row)
        with open("data/balances.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(balances)

    def subtract_balance(self, user, amount):
        balances = []
        with open("data/balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    balances.append([user.id, int(row[1]) - amount])
                else:
                    balances.append(row)
        with open("data/balances.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(balances)

    def save_data(self):
        data = []
        with open("data/balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != "id":
                    data.append(row)

            # Add missing members to the data list
            for member in self.bot.get_all_members():
                if not any(row[0] == str(member.id) for row in data):
                    data.append([str(member.id), 250])

        with open("data/balances.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows([["id", "balance"]] + data)



async def setup(bot):
    await bot.add_cog(Highlow(bot))