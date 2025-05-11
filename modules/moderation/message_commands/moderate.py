import discord
from discord.ext import commands
from datetime import datetime, timedelta
import variables
from utils.uwufier import Uwuifier
from pytimeparse.timeparse import timeparse
import utils.modlogs as modlogs

uwu = Uwuifier()
AUTO_UWU = []

def generate_discord_relative_timestamp(seconds):
    # Calculate the future Unix timestamp
    future_timestamp = int((datetime.now() + timedelta(seconds=seconds)).timestamp())

    # Format the relative timestamp in the Discord style
    formatted_timestamp = f"<t:{future_timestamp}:R>"

    return formatted_timestamp

class ModerateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Moderate")
    async def moderate(self, inter: discord.MessageCommandInteraction):
        # Store message
        message = inter.target
        
        if message.author.id == self.bot.user.id:
            return await inter.response.send_modal(EditBotMessageModal(message))
        
        # Send initial response message
        prompt = discord.Embed(
            title="Moderate this message",
            description="Select a moderation option below. The message will be deleted when you select an option.",
            colour=discord.Colour.orange()
        ).add_field("Message Author",f"{message.author.global_name} ({message.author.id})",inline=False)
        await inter.response.send_message(embed=prompt,view=ModActions(message),ephemeral=True)
        
# Defines a simple view of row buttons.
class ModActions(discord.ui.View):
    def __init__(self, message: discord.Message):
        self.responded = False
        self.message = message
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Warn", style=discord.ButtonStyle.gray)
    async def warn(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        if not self.responded:
            self.responded = True
            await self.message.delete()
            await inter.response.send_modal(WarnModal(self.message))
        else:
            await inter.response.send_message("This has already been responded to before. To moderate, please use the `/mod` command.",ephemeral=True)
    
    @discord.ui.button(label="Mute", style=discord.ButtonStyle.gray)
    async def mute(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        if not self.responded:
            self.responded = True
            await self.message.delete()
            await inter.response.send_modal(MuteModal(self.message))
        else:
            await inter.response.send_message("This has already been responded to before. To moderate, please use the `/mod` command.",ephemeral=True)
    
    @discord.ui.button(label="Ban", style=discord.ButtonStyle.gray)
    async def ban(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        if not self.responded:
            self.responded = True
            await self.message.delete()
            await inter.response.send_modal(BanModal(self.message))
        else:
            await inter.response.send_message("This has already been responded to before. To moderate, please use the `/mod` command.",ephemeral=True)
    
    @discord.ui.button(label="Purge following messages", style=discord.ButtonStyle.red)
    async def purge(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        if not self.responded:
            begin = self.message.created_at
            msgs = await inter.channel.purge(after=begin)
            await self.message.delete()
            
            conf = discord.Embed(
                title=f"Purged {len(msgs) + 1!s} messages",
                description=f"Removed {len(msgs) + 1!s} messages following the selected message.",
                colour= discord.Colour.red()
            )
            
            await inter.response.send_message(embed=conf,ephemeral=True)
            
            await inter.guild.get_channel(variables.modlogs).send(
                embed=discord.Embed(
                    title="Messages Purged",
                    description=f"{len(msgs) + 1!s} messages were purged in the channel {inter.channel.mention}",
                    colour=discord.Colour.orange(),
                )
                .add_field(name="Start Message",value=f"<t:{int(self.message.created_at.timestamp())!s}:f> ({self.message.author.name}): ```\n{self.message.content}```")
                .add_field(name="End Message",value=f"<t:{int(msgs[-1].created_at.timestamp())!s}:f> ({msgs[-1].author.name}): ```\n{msgs[-1].content}```")
                .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
            )
            
        else:
            await inter.response.send_message("This has already been responded to before. To moderate, please use the `/mod` command.",ephemeral=True)
    
class WarnModal(discord.ui.Modal):
    def __init__(self, message: discord.Message) -> None:
        self.member = message.author
        self.message = message
        components = [
            discord.ui.TextInput(
                label="Warn Message",
                placeholder="Don't do a silly like that.",
                custom_id="message",
                style=discord.TextInputStyle.long
            )
        ]
        super().__init__(title="Warn User", custom_id="warn", components=components)

    async def callback(self, inter: discord.ModalInteraction) -> None:
        reason = uwu.uwuify_sentence(inter.text_values["message"]) if self.member.id in AUTO_UWU else inter.text_values["message"]
        try:
            await self.member.send(
                embed=discord.Embed(
                    title="You recieved a warning",
                    colour=discord.Colour.orange(),
                    description="You have been given a warning in Datapack Hub by a moderator. Please read and acknowledge the warning listed below.",
                    timestamp=datetime.now(),
                )
                .add_field("Warning",f"```\n{reason}```",inline=False)
                .add_field("Your Message",f"```\n{self.message.clean_content}```in channel {self.message.channel.mention}",inline=False)
                .set_footer(text="If you think this was done incorrectly, please contact a staff member.")
            )
        except discord.errors.Forbidden:
            await inter.response.send_message(
                f"I could not warn {self.member.mention} because either they have not enabled DMs from this server, or they have blocked the bot. Either way, they are a skibidi rizzler.",
                ephemeral=True,
            )
        except Exception as e:
            await inter.response.send_message(
                f"Failed to warn user {self.member.mention}: `{e}`",
                ephemeral=True,
            )
        else:
            conf = discord.Embed(
                title="User Warned",
                description=f"Successfully deleted the message from and warned user {self.member.mention} for reason:```\n{reason}```",
                colour= discord.Colour.red()
            )
            await inter.response.send_message(embed=conf,ephemeral=True)
            
            await inter.guild.get_channel(variables.modlogs).send(
                embed=discord.Embed(
                    title="User Warned",
                    description=f"{self.member.name} (UID {self.member.id}) was warned.",
                    colour=discord.Colour.red(),
                )
                .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
                .add_field("Warning",f"```\n{reason}```",inline=False)
                .add_field("Quoted message",f"```\n{self.message.clean_content}```in channel {self.message.channel.mention}",inline=False)
            )
            
            modlogs.log({
                "action":"warn",
                "user":self.member.id,
                "reason":reason
            })

    async def on_error(self, error, interaction: discord.ModalInteraction) -> None:
        await interaction.response.send_message("Oops, something went wrong.", ephemeral=True)
        
class MuteModal(discord.ui.Modal):
    def __init__(self, message: discord.Message) -> None:
        self.member = message.guild.get_member(message.author.id)
        self.message = message
        components = [
            discord.ui.TextInput(
                label="Mute Message",
                placeholder="Don't do a silly like that.",
                custom_id="message",
                style=discord.TextInputStyle.long
            ),
            discord.ui.TextInput(
                label="Mute Length (max two weeks)",
                placeholder="4h",
                custom_id="length",
                style=discord.TextInputStyle.short
            )
        ]
        super().__init__(title="Mute User", custom_id="mute", components=components)

    async def callback(self, inter: discord.ModalInteraction) -> None:
        reason = uwu.uwuify_sentence(inter.text_values["message"]) if self.member.id in AUTO_UWU else inter.text_values["message"]
        length = inter.text_values["length"]
        seconds = timeparse(length)
        
        try:
            await self.member.timeout(duration=seconds, reason=reason)
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to mute user {self.member.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to mute user {self.member.mention}: `{e}`",ephemeral=True)
        else:
            conf = discord.Embed(
                title="User Muted",
                description=f"Successfully deleted the message from and muted user {self.member.mention} for reason:```\n{reason}```",
                colour= discord.Colour.red()
            )
            await inter.response.send_message(embed=conf,ephemeral=True)
            
            await self.member.send(
                embed=discord.Embed(
                    title=f"You were muted",
                    colour=discord.Colour.red(),
                    description=f"You were muted in Datapack Hub by a moderator for `{length}`. You will be unable to send messages until the time is up.",
                    timestamp=datetime.now(),
                )
                .add_field("Reason",f"```\n{reason}```",inline=False)
                .add_field("Your message",f"```\n{self.message.clean_content}```in channel {self.message.channel.mention}",inline=False)
                .add_field("Expires",generate_discord_relative_timestamp(seconds),inline=False)
                .set_footer(text="If you think this was done incorrectly, please contact a staff member.")
            )
            
            await inter.guild.get_channel(variables.modlogs).send(embed=discord.Embed(
                title="User Muted",
                description=f"{self.member.name} (UID {self.member.id}) was muted.",
                colour=discord.Colour.red(),
            )
            .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
            .add_field("Reason", f"```\n{reason}```", inline=False)
            .add_field("Quoted Message", f"```\n{self.message.clean_content}```in channel {self.message.channel.mention}", inline=False)
            .add_field("Expires",generate_discord_relative_timestamp(seconds),inline=False)
            .add_field("Length",length,inline=False)
            )
            
            modlogs.log({
                "action":"mute",
                "user":self.member.id,
                "reason":reason,
                "length":length
            })

    async def on_error(self, error, interaction: discord.ModalInteraction) -> None:
        await interaction.response.send_message("Oops, something went wrong.", ephemeral=True)
        
class BanModal(discord.ui.Modal):
    def __init__(self, message: discord.Message) -> None:
        self.member = message.author
        self.message = message
        components = [
            discord.ui.TextInput(
                label="Ban Message",
                placeholder="Don't do a silly like that.",
                custom_id="message",
                style=discord.TextInputStyle.long
            ),
            discord.ui.TextInput(
                label="Delete Messages?",
                placeholder="Leave blank for yes, or enter anything for no",
                custom_id="delete",
                style=discord.TextInputStyle.short
            )
        ]
        super().__init__(title="Ban User", custom_id="ban", components=components)

    async def callback(self, inter: discord.ModalInteraction) -> None:
        reason = uwu.uwuify_sentence(inter.text_values["message"]) if self.member.id in AUTO_UWU else inter.text_values["message"]
        delete = not bool(inter.text_values["message"].strip())
        
        try:
            await self.member.send(
                embed=discord.Embed(
                    title="You were banned",
                    colour=discord.Colour.red(),
                    description=f"You were banned from Datapack Hub by a moderator.",
                    timestamp=datetime.now(),
                )
                .add_field("Reason",f"```\n{reason}```",inline=False)
                .add_field("Your message",f"```\n{self.message.clean_content}```in channel {self.message.channel.mention}")
                .set_footer(text="If you think this was done incorrectly, please contact a staff member.")
            )
            
            if delete:
                await self.member.ban()
            else:
                await self.member.ban(clean_history_duration=0)
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to ban user {self.member.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to ban user {self.member.mention}: `{e}`",ephemeral=True)
        else:
            conf = discord.Embed(
                title="User Banned",
                description=f"Successfully deleted the message from and banned user {self.member.mention} for reason:```\n{reason}```",
                colour= discord.Colour.red()
            )
            await inter.response.send_message(embed=conf,ephemeral=True)
            
            await inter.guild.get_channel(variables.modlogs).send(embed=discord.Embed(
                title="User Banned",
                description=f"{self.member.name} (UID {self.member.id}) was banned.",
                colour=discord.Colour.red(),
            )
            .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
            .add_field("Reason",f"```\n{reason}```",inline=False)
            .add_field("Quoted Message message",f"```\n{self.message.clean_content}```in channel {self.message.channel.mention}")
            )
            
            modlogs.log({
                "action":"ban",
                "user":self.member.id,
                "reason":reason
            })

    async def on_error(self, error, interaction: discord.ModalInteraction) -> None:
        await interaction.response.send_message("Oops, something went wrong.", ephemeral=True)
        
class EditBotMessageModal(discord.ui.Modal):
    def __init__(self, message: discord.Message) -> None:
        self.message = message
        components = [
            discord.ui.TextInput(
                label="Message Content",
                placeholder="This can't be blank!",
                custom_id="message",
                style=discord.TextInputStyle.long,
                value=message.content
            )
        ]
        super().__init__(title="Edit Bot Message", custom_id="edit", components=components)

    async def callback(self, inter: discord.ModalInteraction) -> None:
        await self.message.edit(inter.text_values["message"])
        
        await inter.response.send_message("Done!",ephemeral=True)

    async def on_error(self, error, interaction: discord.ModalInteraction) -> None:
        await interaction.response.send_message("Oops, something went wrong.", ephemeral=True)