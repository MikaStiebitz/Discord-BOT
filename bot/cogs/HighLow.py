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
            game["last_number"] = number # store the number in the game dictionary
            await self.win(ctx, game)
        else:
            game["last_number"] = number # store the number in the game dictionary
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
            game["last_number"] = number # store the number in the game dictionary
            await self.win(ctx, game)
        else:
            game["last_number"] = number # store the number in the game dictionary
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
        await ctx.send(f"You have {balance} money.")

    @commands.command()
    async def work(self, ctx):
        last_work_time = None
        with open("last_work.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(ctx.author.id):
                    last_work_time = datetime.datetime.fromisoformat(row[1])
                    break
        
        time_since_last_work = datetime.datetime.now() - last_work_time if last_work_time else datetime.timedelta(seconds=999999)
        if time_since_last_work < datetime.timedelta(hours=3):
            remaining_time = datetime.timedelta(hours=3) - time_since_last_work
            await ctx.send(f"You will not be able to work at Microsoft support for another {remaining_time.seconds // 3600} hours and {(remaining_time.seconds % 3600) // 60} minutes.")
            return

        self.add_balance(ctx.author, 100)

        # Write the new last work time to last_work.csv file
        with open("last_work.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([ctx.author.id, datetime.datetime.now().isoformat()])

        await ctx.send("You successfully scammed 3 people with the Microsoft call center and earned 100€.")

    @commands.command()
    async def daily(self, ctx):
        last_daily_time = None
        with open("last_daily.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(ctx.author.id):
                    last_daily_time = datetime.datetime.fromisoformat(row[1])
                    break
        
        time_since_last_daily = datetime.datetime.now() - last_daily_time if last_daily_time else datetime.timedelta(seconds=999999)
        if time_since_last_daily < datetime.timedelta(hours=24):
            remaining_time = datetime.timedelta(hours=24) - time_since_last_daily
            await ctx.send(f"Your daily bonus is ready in {remaining_time.seconds // 3600} hours and {(remaining_time.seconds % 3600) // 60} minutes.")
            return

        self.add_balance(ctx.author, 1000)

        with open("last_daily.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([ctx.author.id, datetime.datetime.now().isoformat()])

        await ctx.send("They were successfully transferred 1.000€ to their account")

    def get_last_daily_time(self, user):
        with open("last_daily.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    return float(row[1])
        return None

    def set_last_daily_time(self, user, time):
        times = []
        with open("last_daily.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    times.append([user.id, time])
                else:
                    times.append(row)
        with open("last_daily.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(times)

    def get_last_work_time(self, user):
        with open("last_work.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    return float(row[1])
        return None

    def set_last_work_time(self, user, time):
        times = []
        with open("last_work.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    times.append([user.id, time])
                else:
                    times.append(row)
        with open("last_work.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(times)

    def get_balance(self, user):
        with open("balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    return int(row[1])
        self.add_balance(user, 250)
        return 250

    def add_balance(self, user, amount):
        balances = []
        with open("balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    balances.append([user.id, int(row[1]) + amount])
                else:
                    balances.append(row)
        with open("balances.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(balances)

    def subtract_balance(self, user, amount):
        balances = []
        with open("balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == str(user.id):
                    balances.append([user.id, int(row[1]) - amount])
                else:
                    balances.append(row)
        with open("balances.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(balances)

    def save_data(self):
        data = []
        with open("balances.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != "id":
                    data.append(row)
        for user in self.bot.get_all_members():
            balance = self.get_balance(user)
            if [str(user.id), balance] not in data:
                data.append([str(user.id), balance])
        with open("balances.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows([["id", "balance"]] + data)

async def setup(bot):
    await bot.add_cog(Highlow(bot))