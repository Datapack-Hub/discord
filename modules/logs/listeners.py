import discord
from discord.ext import commands
import variables

class LogsListeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.logs_channel = self.bot.get_channel(variables.logs)
        self.user_logs_channel = self.bot.get_channel(variables.userlogs)
    
    # Member Join
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.user_logs_channel.send(
            embed=discord.Embed(
                title="Member Joined",
                colour=discord.Colour.green()
            )
            .add_field("User Details",f"<@{member.id}> | {member.name} | {member.id}",inline=False)
            .add_field("Account Created",f"<t:{int(member.created_at.timestamp())}:D>",inline=False)
            .add_field("New Member Count",f"**{member.guild.member_count}**",inline=False)
            .set_author(name=member.global_name,icon_url=member.display_avatar.url)
        )
        
    # Member Join
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        roles = "None"
        if len(member.roles) != 0:
            for role in member.roles:
                roles += f", {role.name}"
            roles = roles[2:]
        await self.user_logs_channel.send(
            embed=discord.Embed(
                title="Member Left",
                colour=discord.Colour.brand_red()
            )
            .add_field("User Details",f"<@{member.id}> | {member.name} | {member.id}",inline=False)
            .add_field("New Member Count",f"**{member.guild.member_count}**",inline=False)
            .add_field("Join Date",f"<t:{int(member.joined_at.timestamp())}:D>")
            .add_field("Roles",roles,inline=False)
            .set_author(name=member.global_name,icon_url=member.display_avatar.url)
        )
            
        
    # Channel Delete
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
        await self.logs_channel.send(embed=discord.Embed(
            title="Guild Channel Deleted",
            colour=discord.Colour.from_rgb(130, 7, 31)
        ).add_field("Channel Name",channel.name,inline=False).add_field("Category",channel.category.name,inline=False).set_author(name=entry.user.global_name,icon_url=entry.user.avatar.url))
    
    # Channel Create
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1).get()
        await self.logs_channel.send(embed=discord.Embed(
            title="Guild Channel Created",
            colour=discord.Colour.from_rgb(37, 199, 32)
        ).add_field("Channel Name",channel.name,inline=False).add_field("Category",channel.category.name,inline=False).set_author(name=entry.user.global_name,icon_url=entry.user.avatar.url))
    
    # Message Edit
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content:
            await self.logs_channel.send(embed=discord.Embed(
                title="Message Edited",
                description=f"**[Jump to the message]({after.jump_url})**",
                colour=discord.Colour.from_rgb(209, 192, 59)
            ).add_field("Before",before.content,inline=False).add_field("After",after.content,inline=False).set_author(name=after.author.global_name,icon_url=after.author.avatar.url))
    
    # Message Delete
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        await self.logs_channel.send(embed=discord.Embed(
            title="Message Deleted",
            colour=discord.Colour.from_rgb(230, 50, 50)
        ).add_field("Content",message.content,inline=False).add_field("Channel",message.channel.jump_url,inline=False).add_field("Attachments",f"{message.attachments.__len__()!s} attachments",inline=False).set_author(name=message.author.global_name,icon_url=message.author.avatar.url))
