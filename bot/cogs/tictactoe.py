import asyncio
import random
import discord
from discord.ext import commands
import typing
import csv

class TicTacToe:
    # Emotes Section
    white_page = ":white_large_square:"
    X_Emoji = "❌"
    O_Emoji = "⭕"

    top_left = '↖️'
    top = '⬆️'
    top_right = '↗️'
    left = '⬅️'
    mid = '🔵'
    right = '➡️'
    bottom_left = '↙️'
    bottom = '⬇️'
    bottom_right = '↘️'

    # Generates A embed for Tic Tac Toe Game
    @staticmethod
    def get_ttt_embed(player1, player2, data, move_of, final=False, tie=False):
        embed = discord.Embed(title=f"Match of {player1} vs {player2}")
        embed.colour = move_of.colour if not final else player1.colour if move_of == player2 else player2.colour
        data_ = data.copy()
        for i in range(1, 10):
            if data[i] == 0:
                data_[i] = TicTacToe.white_page
            elif data[i] == 1:
                data_[i] = TicTacToe.X_Emoji
            elif data[i] == 2:
                data_[i] = TicTacToe.O_Emoji
        description = (
            f"{data_[1]}{data_[2]}{data_[3]}\n"
            f"{data_[4]}{data_[5]}{data_[6]}\n"
            f"{data_[7]}{data_[8]}{data_[9]}")
        if tie:
            description += f'\nMatch Draw!'
        elif not final:
            description += f'\n\n{move_of.name}\'s Turn'
            description += ' **(X)**' if move_of == player1 else ' **(O)**'
        else:
            if move_of == player1:
                description += f'\n\n{player2.name}#{player2.discriminator} is Winner.'
            else:
                description += f'\n\n{player1.name}#{player1.discriminator} is Winner.'

        embed.description = description
        return embed

    # Declares Winner if no one is winner, it Returns False
    @staticmethod
    def declare_winner(data):
        game = []
        for i in [1, 4, 7]:
            row = []
            for j in range(i, i + 3):
                row.append(data[j])
            game.append(row)

        def declare(game_1):
            # horizontal
            for row_1 in game_1:
                if row_1.count(row_1[0]) == len(row_1) and row_1[0] != 0:
                    return row_1[0]
            # vertical
            for col in range(len(game[0])):
                check = []
                for row_2 in game:
                    check.append(row_2[col])
                if check.count(check[0]) == len(check) and check[0] != 0:
                    return check[0]

            # / diagonal
            diagonals = []
            for idx, reverse_idx in enumerate(reversed(range(len(game)))):
                diagonals.append(game[idx][reverse_idx])

            if diagonals.count(diagonals[0]) == len(diagonals) and diagonals[0] != 0:
                return diagonals[0]

            # \ diagonal
            diagonals_reverse = []
            for ix in range(len(game)):
                diagonals_reverse.append(game[ix][ix])

            if diagonals_reverse.count(diagonals_reverse[0]) == len(diagonals_reverse) and diagonals_reverse[0] != 0:
                return diagonals_reverse[0]
            return None

        winner = declare(game)
        return winner


class TicTacToeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(usage='[Member]')
    async def ttt(self, ctx, member: discord.Member, bet: typing.Optional[int] = None):
        """A tic tac toe command with reactions. When you will use your move the reaction will be removed.
        Invite your friend to play.."""

        try:
            # Exceptions
            if member.bot:
                await ctx.send('You can\'t play with bots now.')
                return
            if member == ctx.author:
                await ctx.send("You can't play with yourself.")
                return
            
            if bet:
                self.save_data()
                if bet > self.get_balance(ctx.author):
                    await ctx.send("Not enough Money on your account :C")
                    return             
                if bet > self.get_balance(member):
                    await ctx.send(f"{member.mention} has not enough Money on his account :C")
                    return     
            if bet:
                message = await ctx.send(f"{member.mention} {ctx.author} wants to play 'Tic Tac Toe' with You. Accept/Deny by reacting on below buttons. Bet Pool: {bet}€")
            else:
                message = await ctx.send(f"{member.mention} {ctx.author} wants to play 'Tic Tac Toe' with You. Accept/Deny by reacting on below buttons.")

            for r in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
                await message.add_reaction(r)
            # Wait for Confirmation..
            confirmation = None

            def check(payload):
                nonlocal confirmation
                if payload.message_id != message.id or payload.user_id != member.id:
                    return False

                codeblock = str(payload.emoji)

                if codeblock not in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
                    return False

                if codeblock == '\N{WHITE HEAVY CHECK MARK}':
                    confirmation = True
                    return True

                elif codeblock == '\N{CROSS MARK}':
                    confirmation = False
                    return True

            try:
                await self.bot.wait_for('raw_reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                confirmation = None

            if confirmation is None:
                return await ctx.send(f"{member} failed to accept your tic tac toe game challenge.")

            elif confirmation is False:
                return await ctx.send(f"{member} declined your tic tac toe game challenge.")

            # Choice of First Turn
            players_ = [ctx.author, member]
            player1, player1_move = random.choice(players_), 1
            player2, player2_move = players_[0] if players_.index(
                player1) == 1 else players_[1], 2
            data = {}
            for i in range(1, 10):
                data[i] = 0

            # Remaining Moves Dictionary
            remaining_moves = {
                TicTacToe.top_left: 1, TicTacToe.top: 2, TicTacToe.top_right: 3,
                TicTacToe.left: 4, TicTacToe.mid: 5, TicTacToe.right: 6,
                TicTacToe.bottom_left: 7, TicTacToe.bottom: 8, TicTacToe.bottom_right: 9
            }

            move_of, move_name = player1, player1_move
            initial_embed = TicTacToe.get_ttt_embed(
                player1, player2, data, move_of)
            initial_embed = await ctx.send(embed=initial_embed)

            # Add Emotes To Message (initial_embed)
            for emoji in remaining_moves.keys():
                await initial_embed.add_reaction(emoji)
            while True:

                # A Check to take in moves..
                def check(reaction_, user):
                    return user.id == move_of.id and initial_embed.id == reaction_.message.id

                # Wait for Reaction
                if bet:
                    reaction = await self.bot.wait_for('reaction_add', check=check)
                else:
                    try:
                        reaction = await self.bot.wait_for('reaction_add', check=check, timeout=60)
                    except asyncio.TimeoutError:
                        await ctx.send('Timed Out..{} failed to use moves.'.format(move_of.mention))
                        return

                # Converted Emoji Object to '<:UpLeftArrow:710733351991902258>'
                str_reaction = str(reaction[0])
                if str_reaction in remaining_moves.keys():
                    data[remaining_moves[str_reaction]] = move_name

                # Swap Turn
                move_of, move_name = (player1, player1_move) if move_of == player2 else (
                    player2, player2_move)

                # Generates Embed
                new_embed = TicTacToe.get_ttt_embed(
                    player1, player2, data, move_of)

                # Removes current reaction from remaining moves dictionary.
                del remaining_moves[str_reaction]
                await initial_embed.edit(embed=new_embed)
                # Declaration of winner (Returns None if no one is Winner)
                winner = TicTacToe.declare_winner(data)
                if winner is None:
                    # If moves still remaining
                    if len(remaining_moves.keys()) != 0:
                        await initial_embed.clear_reaction(str_reaction)
                    # Else Generates a Tie Embed
                    else:
                        await initial_embed.clear_reaction(str_reaction)
                        new_embed = TicTacToe.get_ttt_embed(
                            player1, player2, data, move_of, tie=True)
                        await initial_embed.edit(embed=new_embed)
                        await ctx.send('Match Draw!')
                        return
                else:
                    # Generates a winner Embed
                    new_embed = TicTacToe.get_ttt_embed(
                        player1, player2, data, move_of, final=True)
                    await initial_embed.edit(embed=new_embed)
                    if winner == 1:
                        if bet:
                            self.add_balance(player1, bet*2)
                            self.subtract_balance(player2, bet)
                            await ctx.send(f'{player1.mention} is Winner and Won {bet*2}€')
                        else:
                            await ctx.send(f'{player1.mention} is Winner.')
                    else:
                        if bet:
                            self.add_balance(player2, bet*2)
                            self.subtract_balance(player1, bet)
                            await ctx.send(f'{player2.mention} is Winner and Won {bet*2}€')
                        else:
                            await ctx.send(f'{player2.mention} is Winner.')
                    await initial_embed.clear_reactions()
                    return
        except discord.NotFound:
            return


async def setup(client):
    await client.add_cog(TicTacToeBot(client))