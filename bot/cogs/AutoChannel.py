from discord.ext import commands
import discord
from modules.AutoChannelFunctions import get_all_channels, add_channel, delete_channel

class VoiceChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="autochannel", description="Setup Autochannels")
    async def autochannel(self, ctx, channel: discord.VoiceChannel):
        await add_channel(channel.id)
        embed = discord.Embed(
            title=f"Added Channel: {channel}",
            color=discord.Color.blurple())
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        WATCHED_CHANNEL_IDS = await get_all_channels()
        if WATCHED_CHANNEL_IDS is not None:
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
