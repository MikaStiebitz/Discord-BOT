import os
import discord
from config import Auth
from discord.ext import commands
from modules import BankFunctions, ItemsFunctions, PrefixFunctions, AutoChannelFunctions, ReactionRoleFunctions

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=self.get_guild_prefix,
            intents=discord.Intents.all(),
            case_insensitive=True)
        
    async def get_guild_prefix(self, bot, message) -> str:
        guild_id = message.guild.id
        await PrefixFunctions.add_prefix(guild_id)
        prefix = await PrefixFunctions.get_prefix(guild_id)
        return prefix
    
    async def on_ready(self):
        await ItemsFunctions.DB.connect()
        print("Database connected")
        if not ItemsFunctions.DB.is_connected:
            raise RuntimeError("Database access denied")

        await BankFunctions.create_table()
        await ItemsFunctions.create_table()
        await PrefixFunctions.create_table()
        await AutoChannelFunctions.create_table()
        await ReactionRoleFunctions.create_table()
        print("Database loaded")
        
        await super().change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"/help | {len(self.guilds)} Servers"))
        print(f"Logged in as {self.user}")
        await self.tree.sync()



    async def setup_hook(self) -> None:
        print("Loading commands...")
        for filename in os.listdir("bot/cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"bot.cogs.{filename[:-3]}")
                except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                    pass
                print(f"{filename[:-3]} command loaded")

    async def on_guild_remove(self, guild):
        await PrefixFunctions.delete_prefix(guild.id)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found.")

    def run(self) -> None:
        super().run(Auth.TOKEN)