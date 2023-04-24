from discord.ext import commands
from time import sleep

class Clear(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(name="clear", description="all or <number>")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, arg: str):
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
