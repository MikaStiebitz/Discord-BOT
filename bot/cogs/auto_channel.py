from discord.ext import commands

WATCHED_CHANNEL_IDS = [1096823779231019168, 1096837134381490226]

class VoiceChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id in WATCHED_CHANNEL_IDS:
            watched_channel = after.channel
            new_channel_name = f"{member.name}'s Channel"
            new_channel = await watched_channel.category.create_voice_channel(
                name=new_channel_name,
                user_limit=watched_channel.user_limit,
                position=watched_channel.position+1,
                reason=f"{member.name} created a new channel"
            )

            await new_channel.set_permissions(member, manage_channels=True)
            await member.move_to(new_channel)

            def check(member, before, after):
                return len(new_channel.members) == 0

            try:
                await self.bot.wait_for("voice_state_update", timeout=300, check=check)
            except TimeoutError:
                pass

            await new_channel.delete()

def setup(bot):
    return bot.add_cog(VoiceChannelCog(bot))
