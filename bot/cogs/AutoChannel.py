from discord.ext import commands
import discord
from modules.AutoChannelFunctions import get_all_channels, add_channel, delete_channel, get_all_autochannels, add_autochannel, delete_autochannel

class VoiceChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        WATCHED_CHANNEL_IDS = await get_all_autochannels()
        WATCHED_CHANNEL_IDS = list(filter(None, WATCHED_CHANNEL_IDS))
        if WATCHED_CHANNEL_IDS is not None:
            for channel_id in WATCHED_CHANNEL_IDS:
                print(channel_id)
                channel = self.bot.get_channel(channel_id)
                await delete_autochannel(channel_id)
                await channel.delete()
                
        CHECK_CHANNEL_IDS = await get_all_channels()
        if CHECK_CHANNEL_IDS is not None:
            for channel_id in CHECK_CHANNEL_IDS:
                channel = self.bot.get_channel(channel_id)
                if channel is None:
                    await delete_channel(channel_id)


    @commands.hybrid_command(name="autochannel", description="Setup Autochannels")
    async def autochannel(self, ctx, add: discord.VoiceChannel = None, delete: discord.VoiceChannel = None):
        CHECK_CHANNEL_IDS = await get_all_channels()
        if add is not None:
            if add.id in CHECK_CHANNEL_IDS:
                embed = discord.Embed(
                    title=f"Channel is already in AutoChannels: {add}",
                    color=discord.Color.blurple())
                embed.set_footer(
                    text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
                return
            
            await add_channel(add.id)
            embed = discord.Embed(
                title=f"Added Channel to AutoChannels: {add}",
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            
        elif delete is not None:
            if delete.id not in CHECK_CHANNEL_IDS:
                embed = discord.Embed(
                    title=f"Channel is not in AutoChannels: {delete}",
                    color=discord.Color.blurple())
                embed.set_footer(
                    text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
                return
            
            await delete_channel(delete.id)
            embed = discord.Embed(
                title=f"Delete Channel from AutoChannels: {delete}",
                color=discord.Color.blurple())
            embed.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            WATCHED_CHANNEL_IDS = await get_all_channels()
            if WATCHED_CHANNEL_IDS is not None:
                if after.channel and after.channel.id in WATCHED_CHANNEL_IDS:
                    watched_channel = after.channel
                    new_channel_name = f"{member.name}'s Channel"
                    new_channel = await watched_channel.category.create_voice_channel(
                        name=new_channel_name,
                        user_limit=watched_channel.user_limit,
                        position=watched_channel.position,
                        reason=f"{member.name} created a new channel"
                    )
                    await add_autochannel(new_channel.id)

                    await new_channel.set_permissions(member, manage_channels=True)
                    await member.move_to(new_channel)

                    def check(member, before, after):
                        return len(new_channel.members) == 0

                    try:
                        await self.bot.wait_for("voice_state_update", check=check)
                    except TimeoutError:
                        pass
                    
                    await delete_autochannel(new_channel.id)
                    await new_channel.delete()
        except:
            pass
        
def setup(bot):
    return bot.add_cog(VoiceChannelCog(bot))
