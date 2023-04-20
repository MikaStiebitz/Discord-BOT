import os
import discord
from dotenv import load_dotenv
import wavelink
from discord.ext.commands import Bot

class Bot(Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            case_insensitive=True)
        load_dotenv()

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def setup_hook(self) -> None:
        print("Loading commands...")
        for filename in os.listdir("bot/cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"bot.cogs.{filename[:-3]}")
                except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                    pass
                print(f"{filename[:-3]} command loaded")
                
    def run(self) -> None:
        super().run(os.getenv("BOT_TOKEN"))