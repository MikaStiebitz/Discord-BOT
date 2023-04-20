import discord
from discord.ext import commands
from discord import app_commands
from time import sleep

class Clear(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def hasPermission(interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You do not have permission to use this command.")
        return True


    @app_commands.check(hasPermission)
    @app_commands.command(
        name="clear",
        description="all or <number>")

    async def clear_interaction(self, interaction: discord.Interaction, num: str):
        channel = interaction.channel
        try:
            if num.isdigit():
                num_messages = int(num)
                await interaction.response.send_message(f"Deleting {num_messages} messages.")
                sleep(0.3)
                await channel.purge(limit=num_messages+1)
            elif num == "all":
                await interaction.response.send_message("Deleting All messages.")
                sleep(0.3)
                await channel.purge()
            else:
                await interaction.response.send_message("Invalid argument. Please provide a number or 'all'.")
        except Exception as e:
            pass

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, arg):
        channel = ctx.channel
        if arg.isdigit():
            num_messages = int(arg)
            await ctx.send(f"Deleting {num_messages} messages.")
            sleep(0.3)
            await channel.purge(limit=num_messages+1)
            
        elif arg == "all":
            await ctx.send("Deleting All messages.")
            sleep(0.3)
            await channel.purge()
        else:
            await ctx.send("Invalid argument. Please provide a number or 'all'.")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have permission to use this command.")

async def setup(client):
    await client.add_cog(Clear(client))
