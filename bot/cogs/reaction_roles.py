import discord
from discord.ext import commands


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = {
            "👍": 1098243045754933248,
            "👎": 1098243146338549850
        }

    @commands.command()
    async def reactionroles(self, ctx):
        message = await ctx.send("React to this message to get a role!")
        for emoji in self.reaction_roles:
            await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 1098245552451362956:
            if str(payload.emoji) in self.reaction_roles:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(self.reaction_roles[str(payload.emoji)])
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
