import discord
from discord.ext import commands
from pytimeparse.timeparse import timeparse
from datetime import datetime, timedelta
import variables
import io
from utils.uwufier import Uwuifier
import utils.modlogs as modlogs
import matplotlib.pyplot as plt
import numpy as np

REASONS = [
    {
        "label": "Excessive Swearing",
        "description": "You've been swearing a lot. We have a no swearing rule in this server.",
    },
    {
        "label": "Spam",
        "description": "Please don't spam in the channels - it's unnecessary and bad.",
    },
    {
        "label": "Inappropriate",
        "description": "This server is meant to be friendly for all ages. Please don't post inappropriate things.",
    },
    {
        "label": "Self Promotion",
        "description": "Please keep self promo to a minimum - it can get very annoying.",
    },
    {
        "label": "Homophobia",
        "description": "Homophobia is strictly not tolerated in Datapack Hub.",
    },
]

def generate_discord_relative_timestamp(seconds):
    # Calculate the future Unix timestamp
    future_timestamp = int((datetime.now() + timedelta(seconds=seconds)).timestamp())

    # Format the relative timestamp in the Discord style
    formatted_timestamp = f"<t:{future_timestamp}:R>"

    return formatted_timestamp


class ModCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="mod")
    async def mod(self, inter: discord.ApplicationContext):
        return
    
    @mod.sub_command("lockdown","Locks all server channels",)
    async def lockdown(self, inter: discord.ApplicationContext):
        await inter.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = False
        current_perms.send_messages_in_threads = False
        current_perms.create_public_threads = False
        current_perms.add_reactions = False
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.send_followup("🔒 **All server channels have been locked**")
        
    @mod.sub_command("unlockdown","Unlocks all server channels",)
    async def unlockdown(self, inter: discord.ApplicationContext):
        await inter.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = True
        current_perms.send_messages_in_threads = True
        current_perms.create_public_threads = True
        current_perms.add_reactions = True
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.send_followup("🔓 **All server channels have been unlocked**")
            
        
    @mod.sub_command("purge", "Bulk delete some messages")
    async def purge(
        self, 
        inter: discord.ApplicationContext, 
        limit: int = discord.Option(description="How many messages to remove"), 
        user: discord.User = discord.Option(description="User to delete messages from",default=None)
    ):
        # Stops the purge if the purge amount is over the API's limit
        if limit > 100:
            await inter.response.send_message(
                "You cannot delete more than 100 messages at once", ephemeral=True
            )
            return

        def is_user(m: discord.Message):
            if m.author != user:
                return False
            return True

        # Deletes the messages
        if user:
            deleted_messages = await inter.channel.purge(limit=limit, check=is_user)
        else:
            deleted_messages = await inter.channel.purge(limit=limit)

        # Logs the purge action
        log_embed = discord.Embed(
            colour=discord.Colour.orange(),
            title="`/purge` Command",
            description=f"{inter.user.name} purged {len(deleted_messages)} messages in {inter.channel.mention}.",
        )

        # Add the author and contents of the deleted messages to the log
        file_content = io.StringIO()
        for messages in deleted_messages:
            file_content.write(
                f"[{datetime.now().strftime('%d/%m/%y %H:%M:%S')}] @{messages.author.name}: {messages.content}\n"
            )

        file_content.seek(0)
        file = discord.File(fp=file_content, filename="purged messages.txt")

        log_channel = inter.guild.get_channel(variables.logs)

        await log_channel.send(embed=log_embed, file=file)

        # Confirm the purge
        await inter.response.send_message(
            f"{len(deleted_messages)} messages have been deleted", ephemeral=True
        )
            
    @mod.sub_command("warn", "Sends a user a warning")
    async def warn(self, inter: discord.ApplicationContext, user: discord.Member, message: str, uwufy: bool = False):
        if uwufy:
            uwu = Uwuifier()
            message = uwu.uwuify_sentence(message)
        try:
            await user.send(
                embed=discord.Embed(
                    title="You recieved a warning",
                    colour=discord.Colour.orange(),
                    description="You have been given a warning in Datapack Hub by a moderator.",
                    timestamp=datetime.now(),
                )
                .add_field("Warning",f"```\n{message}```",inline=False)
                .set_footer(text="If you think this was done incorrectly, please contact a staff member.")
            )
        except discord.errors.Forbidden:
            await inter.response.send_message(
                f"I could not warn {user.mention} because either they have not enabled DMs from this server, or they have blocked the bot.",
                ephemeral=True,
            )
        except Exception as e:
            await inter.response.send_message(
                f"Failed to warn user {user.mention}: `{e}`",
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                f"Warned user {user.mention} for reason:```\n{message}```",
                ephemeral=True,
            )
            
            await inter.guild.get_channel(variables.modlogs).send(
                embed=discord.Embed(
                    title="User Warned",
                    description=f"{user.name} (UID {user.id}) was warned.",
                    colour=discord.Colour.red(),
                )
                .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
                .add_field("Warning",f"```\n{message}```",inline=False)
            )
            
            modlogs.log({
                "action":"warn",
                "user":user.id,
                "reason":message
            })

    @mod.sub_command("mute", "Mutes a member for a length of time")
    async def mute(self, inter: discord.ApplicationContext, user: discord.Member, length: str, reason: str, uwufy: bool = False):
        if uwufy:
            uwu = Uwuifier()
            reason = uwu.uwuify_sentence(reason)
        seconds = timeparse(length)
        try:
            await user.timeout(duration=seconds, reason=reason)
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to mute user {user.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to mute user {user.mention}: `{e}`",ephemeral=True)
        else:
            await inter.response.send_message(f"Muted user {user.mention} for reason:```\n{reason}```",ephemeral=True)
            try:
                await user.send(
                    embed=discord.Embed(
                        title=f"You were muted",
                        colour=discord.Colour.red(),
                        description=f"You were muted in Datapack Hub by a moderator for {length}.",
                        timestamp=datetime.now(),
                    )
                    .add_field("Reason",f"```\n{reason}```",inline=False)
                    .add_field("Expires",generate_discord_relative_timestamp(seconds),inline=False)
                    .set_footer(text="If you think this was done incorrectly, please contact a staff member.")
                )
            except:
                pass
            
            await inter.guild.get_channel(variables.modlogs).send(embed=discord.Embed(
                title="User Muted",
                description=f"{user.name} (UID {user.id}) was muted.",
                colour=discord.Colour.red(),
            )
            .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
            .add_field("Reason", reason, inline=False)
            .add_field("Expires",generate_discord_relative_timestamp(seconds),inline=False)
            .add_field("Length",length,inline=False)
            )
            
            modlogs.log({
                "action":"mute",
                "user":user.id,
                "reason":reason,
                "length":length
            })

    @mod.sub_command("ban", "Bans a member for a length of time")
    async def ban(
        self, inter: discord.ApplicationContext, user: discord.Member, reason: str, uwufy: bool = False
    ):
        if uwufy:
            uwu = Uwuifier()
            reason = uwu.uwuify_sentence(reason)
        try:
            await user.send(
                embed=discord.Embed(
                    title="You were banned",
                    colour=discord.Colour.red(),
                    description=f"You were banned from Datapack Hub by a moderator.",
                    timestamp=datetime.now(),
                )
                .add_field("Reason",f"```\n{reason}```",inline=False)
                .set_footer(text="If you think this was done incorrectly, please contact a staff member.")
            )
            
            await user.ban(reason=reason)
        except discord.errors.Forbidden:
            await inter.response.send_message(f"Failed to ban user {user.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to ban user {user.mention}: `{e}`",ephemeral=True)
        else:
            await inter.response.send_message(f"Banned user {user.mention} for reason:```\n{reason}```",ephemeral=True)
            
            await inter.guild.get_channel(variables.modlogs).send(embed=discord.Embed(
                title="User Banned",
                description=f"{user.name} (UID {user.id}) was banned.",
                colour=discord.Colour.red(),
            )
            .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
            .add_field("Reason",f"```\n{reason}```",inline=False)
            )
            
            modlogs.log({
                "action":"ban",
                "user":user.id,
                "reason":reason
            })
    
    @mod.sub_command("banall","Ban literally everyone",)
    async def banall(self, inter: discord.ApplicationContext):
        #legi go away
        emb = discord.Embed(
            title="⚠️ BAN ALL MEMBERS",
            description="Are you sure? This action is IRREVERSIBLE. Flyne is going to be very angry if you run this command. ONLY USE THIS IN EMERGENCIES. You have been warned.",
            colour=discord.Colour.dark_red()
        )
        await inter.response.send_message(embed=emb,components=[discord.ui.Button(style=discord.ButtonStyle.red,label="CONFIRM")])

    def role_list(self):
        return [discord.OptionChoice(name=role.name,value=role.id) for role in self.bot.guild.roles if role.id in variables.mod_edit_roles]

    @mod.sub_command("role","Grants or removes a (non-vital) role")
    async def role(
        self,
        inter: discord.ApplicationContext,
        user: discord.Member,
        modification: str = discord.Option(
            default = "add",
            choices = ["add", "remove"]
        ),
        role: discord.Role = discord.Option()
    ):
        if not role.id in variables.mod_edit_roles:
            await inter.response.send_message(f"Role `{role.name}` is not allowed in this command", ephemeral=True)
            return

        try:
            if modification == "add":
                if role in user.roles:
                    await inter.response.send_message(f"User {user.name} already has the role {role}.", ephemeral=True)
                else:
                    await user.add_roles(role)
            else:
                if role in user.roles:
                    await user.remove_roles(role)
                else:
                    await inter.response.send_message(f"User {user.name} doesn't have the role {role}.", ephemeral=True)
        except:
            await inter.response.send_message(f"Failed to {modification} role {role.name}, to user {user.name}", ephemeral=True)
        await inter.response.send_message(f"Role {modification + ('ed' if modification == 'add' else 'd')}", ephemeral=True)
