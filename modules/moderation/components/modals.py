import discord
import variables
from pytimeparse import timeparse
from datetime import datetime, timedelta
import utils.log as Log
import traceback
from modules.moderation.components.views import PunishmentMessageView

def generate_discord_relative_timestamp(seconds):
    future_timestamp = int((datetime.now() + timedelta(seconds=seconds)).timestamp())
    formatted_timestamp = f"<t:{future_timestamp}:R>"
    return formatted_timestamp

class BanUserModPanelModal(discord.ui.Modal):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None, *args, **kwargs) -> None:
        super().__init__(
            title="Ban " + user.name, custom_id="ban_user", *args, **kwargs
        )
        
        self.user = user
        self.cause_message = cause_message
        
        self.add_item(discord.ui.InputText(
            label="Reason",
            placeholder="Disrespecting the Wuppertal Suspension Railway Network",
            custom_id="id",
            style=discord.InputTextStyle.long
        ))
        
        self.add_item(discord.ui.InputText(
            label="Delete their last 7d of messages?",
            placeholder="enter 'y' for yes",
            custom_id="delete",
            style=discord.InputTextStyle.short,
            required=False
        ))
        
    async def callback(self, inter: discord.Interaction) -> None:
        reason = self.children[0].value
        delete = bool(self.children[1].value.strip().lower() == "y")
        
        try:
            try:
                await self.user.send(view=PunishmentMessageView("ban",reason, cause=self.cause_message))
            except:
                sent_dm = False
            else:
                sent_dm = True
            
            if delete:
                await self.user.ban(delete_message_seconds=604800)
            else:
                await self.user.ban()
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to ban user {self.user.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to ban user {self.user.mention}: `{e}`",ephemeral=True)
            raise e
        else:
            if self.cause_message:
                await self.cause_message.delete()

            # Immediate bot feedback
            conf = discord.Embed(
                title="User Banned",
                description=f"Successfully banned user {self.user.mention} for reason:```\n{reason}```{'\nNote that this user had DMs disabled, and so did not receive the reason' if not sent_dm else ''}",
                colour= discord.Colour.red()
            )
            await inter.response.send_message(embed=conf,ephemeral=True)
            
            # Log
            log_embed = discord.Embed(
                title="User Banned",
                description=f"{self.user.name} (UID {self.user.id}) was banned.",
                colour=discord.Colour.red(),
            )
            log_embed.set_author(name=inter.user.global_name, icon_url=inter.user.avatar.url)
            log_embed.add_field(name=f"Reason ({'not' if not sent_dm else ''} sent to member)",value=f"```\n{reason}```",inline=False)

            if self.cause_message:
                log_embed.add_field(name="Reference",value=f"{self.cause_message.author.name}**: <t:{int(self.cause_message.created_at.timestamp())!s}:R>: ```\n{discord.utils.remove_markdown(self.cause_message.clean_content)[:300]}```",inline=False)

            await inter.client.get_channel(variables.modlogs).send(embed=log_embed)
        
class KickUserModPanelModal(discord.ui.Modal):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None, *args, **kwargs) -> None:
        super().__init__(
            title="Kick " + user.name, custom_id="kick_user", *args, **kwargs
        )
        
        self.user = user
        self.cause_message = cause_message
        
        self.add_item(discord.ui.InputText(
            label="Reason",
            placeholder="Disrespecting the Wuppertal Suspension Railway Network",
            custom_id="id",
            style=discord.InputTextStyle.long
        ))
        
    async def callback(self, inter: discord.Interaction) -> None:
        reason = self.children[0].value
        
        try:
            try:
                await self.user.send(view=PunishmentMessageView("kick",reason, cause=self.cause_message))
            except:
                sent_dm = False
            else:
                sent_dm = True
            
            await self.user.kick(reason=reason)
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to kick user {self.user.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to kick user {self.user.mention}: `{e}`",ephemeral=True)
        else:
            if self.cause_message:
                await self.cause_message.delete()

            # Immediate bot feedback
            conf = discord.Embed(
                title="User Kicked",
                description=f"Successfully kicked user {self.user.mention} for reason:```\n{reason}```{'\nNote that this user had DMs disabled, and so did not receive the reason' if not sent_dm else ''}",
                colour= discord.Colour.red()
            )
            await inter.response.send_message(embed=conf,ephemeral=True)
            
            # Log
            log_embed = discord.Embed(
                title="User Kicked",
                description=f"{self.user.name} (UID {self.user.id}) was kicked.",
                colour=discord.Colour.red(),
            )
            log_embed.set_author(name=inter.user.global_name, icon_url=inter.user.avatar.url)
            log_embed.add_field(name=f"Reason ({'not' if not sent_dm else ''} sent to member)",value=f"```\n{reason}```",inline=False)

            if self.cause_message:
                log_embed.add_field(name="Reference",value=f"{self.cause_message.author.name}**: <t:{int(self.cause_message.created_at.timestamp())!s}:R>: ```\n{discord.utils.remove_markdown(self.cause_message.clean_content)[:300]}```",inline=False)

            await inter.client.get_channel(variables.modlogs).send(embed=log_embed)
        
class MuteUserModPanelModal(discord.ui.Modal):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None, *args, **kwargs) -> None:
        super().__init__(
            title="Mute " + user.name, custom_id="mute_user", *args, **kwargs
        )
        
        self.user = user
        self.cause_message = cause_message
        
        self.add_item(discord.ui.InputText(
            label="Reason",
            placeholder="Disrespecting the Wuppertal Suspension Railway Network",
            custom_id="id",
            style=discord.InputTextStyle.long
        ))
        
        self.add_item(discord.ui.InputText(
            label="Mute length (max two weeks)",
            placeholder="4d8h",
            custom_id="length",
            style=discord.InputTextStyle.short
        ))
        
    async def callback(self, inter: discord.Interaction) -> None:
        reason = self.children[0].value
        seconds = timeparse.timeparse(self.children[1].value)
        
        try:
            try:
                await self.user.send(view=PunishmentMessageView("mute",reason, cause=self.cause_message, expires=seconds))
            except:
                sent_dm = False
            else:
                sent_dm = True
            
            await self.user.timeout_for(timedelta(seconds=seconds), reason=reason)
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to mute user {self.user.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to mute user {self.user.mention}: `{e}`",ephemeral=True)
        else:
            if self.cause_message:
                await self.cause_message.delete()

            # Immediate bot feedback
            conf = discord.Embed(
                title="User Muted",
                description=f"Successfully muted user {self.user.mention} for reason:```\n{reason}```{'\nNote that this user had DMs disabled, and so did not receive the reason' if not sent_dm else ''}",
                colour= discord.Colour.red()
            )

            await inter.response.send_message(embed=conf,ephemeral=True)
            
            # Log
            log_embed = discord.Embed(
                title="User Muted",
                description=f"{self.user.name} (UID {self.user.id}) was muted.",
                colour=discord.Colour.red(),
            )
            log_embed.set_author(name=inter.user.global_name, icon_url=inter.user.avatar.url)
            log_embed.add_field(name=f"Reason ({'not' if not sent_dm else ''} sent to member)",value=f"```\n{reason}```",inline=False)

            if self.cause_message:
                log_embed.add_field(name="Reference",value=f"{self.cause_message.author.name}**: <t:{int(self.cause_message.created_at.timestamp())!s}:R>: ```\n{discord.utils.remove_markdown(self.cause_message.clean_content)[:300]}```",inline=False)

            log_embed.add_field(name="Expires",value=f"{generate_discord_relative_timestamp(seconds)} ({self.children[1].value})",inline=False)

            await inter.client.get_channel(variables.modlogs).send(embed=log_embed)
        
class WarnUserModPanelModal(discord.ui.Modal):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None, *args, **kwargs) -> None:
        super().__init__(
            title="Warn " + user.name, custom_id="warn_user", *args, **kwargs
        )
        
        self.user = user
        self.cause_message = cause_message
        
        self.add_item(discord.ui.InputText(
            label="Warn message",
            placeholder="Disrespecting the Wuppertal Suspension Railway Network",
            custom_id="id",
            style=discord.InputTextStyle.long
        ))
        
    async def callback(self, inter: discord.Interaction) -> None:
        reason = self.children[0].value
        
        try:
            await self.user.send(view=PunishmentMessageView("warn",reason, cause=self.cause_message))
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to warn user {self.user.mention}: This user has DMs disabled!",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to warn user {self.user.mention}: `{e}`",ephemeral=True)
            raise e
        else:
            if self.cause_message:
                await self.cause_message.delete()

            # Immediate bot feedback
            conf = discord.Embed(
                title="User Warned",
                description=f"Successfully warned user {self.user.mention} with message:```\n{reason}```",
                colour= discord.Colour.red()
            )
            await inter.response.send_message(embed=conf,ephemeral=True)
            
            # Log
            log_embed = discord.Embed(
                title="User Warned",
                description=f"{self.user.name} (UID {self.user.id}) was warned.",
                colour=discord.Colour.red(),
            )
            log_embed.set_author(name=inter.user.global_name, icon_url=inter.user.avatar.url)
            log_embed.add_field(name="Warn message",value=f"```\n{reason}```",inline=False)

            if self.cause_message:
                log_embed.add_field(name="Reference",value=f"{self.cause_message.author.name}**: <t:{int(self.cause_message.created_at.timestamp())!s}:R>: ```\n{discord.utils.remove_markdown(self.cause_message.clean_content)[:300]}```",inline=False)

            await inter.client.get_channel(variables.modlogs).send(embed=log_embed)