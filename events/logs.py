import disnake
from disnake.ext import commands
import variables

class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.logs_channel = self.bot.get_channel(variables.logs)
        
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.abc.GuildChannel):
        entry = await channel.guild.audit_logs(action=disnake.AuditLogAction.channel_delete, limit=1).get()
        await self.logs_channel.send(embed=disnake.Embed(
            title="Guild Channel Deleted",
            color=disnake.Color.from_rgb(130, 7, 31)
        ).add_field("Channel Name",channel.name,inline=False).add_field("Category",channel.category.name,inline=False).set_author(name=entry.user.global_name,icon_url=entry.user.avatar.url))
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel):
        entry = await channel.guild.audit_logs(action=disnake.AuditLogAction.channel_create, limit=1).get()
        await self.logs_channel.send(embed=disnake.Embed(
            title="Guild Channel Created",
            color=disnake.Color.from_rgb(37, 199, 32)
        ).add_field("Channel Name",channel.name,inline=False).add_field("Category",channel.category.name,inline=False).set_author(name=entry.user.global_name,icon_url=entry.user.avatar.url))
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        await self.logs_channel.send(embed=disnake.Embed(
            title="Message Edited",
            description=f"**[Jump to the message]({after.jump_url})**",
            color=disnake.Color.from_rgb(209, 192, 59)
        ).add_field("Before",before.content,inline=False).add_field("After",after.content,inline=False).set_author(name=after.author.global_name,icon_url=after.author.avatar.url))
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        await self.logs_channel.send(embed=disnake.Embed(
            title="Message Deleted",
            color=disnake.Color.from_rgb(230, 50, 50)
        ).add_field("Content",message.content,inline=False).add_field("Channel",message.channel.jump_url,inline=False).add_field("Attachments",f"{message.attachments.__len__()!s} attachments",inline=False).set_author(name=message.author.global_name,icon_url=message.author.avatar.url))