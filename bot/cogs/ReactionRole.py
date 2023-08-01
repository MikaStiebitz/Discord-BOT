import discord
from discord.ext import commands
from modules.ReactionRoleFunctions import add_reaction, get_all_reactions, delete_reaction, get_all_records


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command()
    async def reactionrole_remove(self, ctx, message_id: str, emoji: str):
        message_id = int(message_id)
        message = await ctx.fetch_message(message_id)
        delete_confirm = await delete_reaction(message_id, emoji)
        if delete_confirm is not None:
            embed = discord.Embed(
                title=f"A reaction role has been removed",
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed)
            await message.clear_reaction(emoji)
        else:
            embed = discord.Embed(
                title=f"Message or Emoji not found",
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed)

    @commands.hybrid_command(description="Add a reaction role to a message")
    async def reactionrole_add(self, ctx, message_id: str, emoji: str, role: discord.Role, channel: discord.TextChannel = None):
        message_id = int(message_id)
        message = await ctx.fetch_message(message_id)
        await add_reaction(message_id, emoji, role.id)
     
        if channel is not None:
            channel = self.bot.get_channel(channel.id)
            embed = discord.Embed(
                title=f"A reaction role has been added",
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title=f"A reaction role has been added",
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed)
        print("Reaction role added")
        
        await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            WATCHED_MESSAGE_IDS = await get_all_reactions(payload.message_id)
            if WATCHED_MESSAGE_IDS is not None:
                for message_id in WATCHED_MESSAGE_IDS:
                    db_emoji = message_id[1]
                    db_role = message_id[2]
                    if str(payload.emoji) == db_emoji:
                        guild = self.bot.get_guild(payload.guild_id)
                        role = guild.get_role(db_role)
                        member = guild.get_member(payload.user_id)
                        if role not in member.roles:
                            await member.add_roles(role)
                        else:
                            await member.remove_roles(role)
                            await member.send(f"You have removed the {role.name} role.")
            await self.remove_reaction(payload)

    async def remove_reaction(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji, discord.Object(payload.user_id))

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
