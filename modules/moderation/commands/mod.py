import disnake
from disnake.ext import commands
from pytimeparse.timeparse import timeparse
from datetime import datetime, timedelta
import variables
import io
import re
from utils.uwufier import Uwuifier
import json
import utils.modlogs as modlogs

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
        "label": "Inapropriate",
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
    async def mod(self, inter: disnake.ApplicationCommandInteraction):
        return
    
    @mod.sub_command("lockdown","Locks all server channels",)
    async def lockdown(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = False
        current_perms.send_messages_in_threads = False
        current_perms.create_public_threads = False
        current_perms.add_reactions = False
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.edit_original_message("🔒 **All server channels have been locked**")
        
    @mod.sub_command("unlockdown","Unlocks all server channels",)
    async def unlockdown(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = True
        current_perms.send_messages_in_threads = True
        current_perms.create_public_threads = True
        current_perms.add_reactions = True
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.edit_original_message("🔓 **All server channels have been unlocked**")
            
        
    @mod.sub_command(
        "purge",
        "Bulk delete some messages",
    )
    async def purge(
        self,
        inter: disnake.ApplicationCommandInteraction,
        limit: int = commands.Param(description="How many messages to remove"),
        user: disnake.User = commands.Param(description="User to delete messages from",default=None),
    ):
        # Stops the purge if the purge amount is over the API's limit
        if limit > 100:
            await inter.response.send_message(
                "You cannot delete more than 100 messages at once", ephemeral=True
            )
            return

        def is_user(m: disnake.Message):
            if m.author != user:
                return False
            return True

        # Deletes the messages
        if user:
            deleted_messages = await inter.channel.purge(limit=limit, check=is_user)
        else:
            deleted_messages = await inter.channel.purge(limit=limit)

        # Logs the purge action
        log_embed = disnake.Embed(
            colour=disnake.Colour.orange(),
            title="**`/purge` Command**",
            description=f"{inter.user.name} purged {len(deleted_messages)} messages in {inter.channel.mention}.",
        )

        # Add the autor and contents of the deleted messages to the log
        file_content = io.StringIO()
        for messages in deleted_messages:
            file_content.write(
                f"[{datetime.now().strftime('%d/%m/%y %H:%M:%S')}] @{messages.author.name}: {messages.content}\n"
            )

        file_content.seek(0)
        file = disnake.File(fp=file_content, filename="purged messages.txt")

        log_channel = inter.guild.get_channel(variables.logs)

        await log_channel.send(embed=log_embed, file=file)

        # Confirm the purge
        await inter.response.send_message(
            f"{len(deleted_messages)} messages have been deleted", ephemeral=True
        )

    @mod.sub_command("mute", "Mutes a member for a length of time")
    async def mute(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member, length: str, reason: str, uwufy: bool = False):
        if uwufy == True:
            uwu = Uwuifier()
            reason = uwu.uwuify_sentence(reason)
        seconds = timeparse(length)
        try:
            await user.timeout(duration=seconds, reason=reason)
        except disnake.errors.Forbidden:
            await inter.response.send_message(f"Failed to mute user {user.mention}: I don't have permission to do this.",ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Failed to mute user {user.mention}: `{' '.join(e.args)}`",ephemeral=True)
        else:
            await inter.response.send_message(f"Muted user {user.mention} for reason:```\n{reason}```",ephemeral=True)
            await user.send(
                embed=disnake.Embed(
                    title="You were muted",
                    colour=disnake.Colour.red(),
                    description=f"You were muted in Datapack Hub for {length}. You'll be unmuted {generate_discord_relative_timestamp(seconds)}.\n\nReason:```\n{reason}```",
                    timestamp=datetime.now(),
                )
            )
            await inter.guild.get_channel(variables.modlogs).send(embed=disnake.Embed(
                title="User Muted",
                description=f"{user.name} (UID {user.id}) was muted.",
                colour=disnake.Colour.red(),
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
        self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member, reason: str, uwufy: bool = False
    ):
        if uwufy == True:
            uwu = Uwuifier()
            reason = uwu.uwuify_sentence(reason)
        try:
            await user.send(
                embed=disnake.Embed(
                    title="You were banned",
                    colour=disnake.Colour.red(),
                    description=f"You were banned in Datapack Hub.\n\nReason:```\n{reason}```",
                    timestamp=datetime.now(),
                )
            )
            await user.ban(reason=reason)
        except disnake.errors.Forbidden:
            await inter.response.send_message(
                f"Failed to ban user {user.mention}: I don't have permission to do this.",
                ephemeral=True,
            )
        except Exception as e:
            await inter.response.send_message(
                f"Failed to ban user {user.mention}: `{' '.join(e.args)}`",
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                f"Banned user {user.mention} for reason:```\n{reason}```",
                ephemeral=True,
            )
            await inter.guild.get_channel(variables.modlogs).send(
                embed=disnake.Embed(
                    title="User Banned",
                    description=f"{user.name} (UID {user.id}) was banned.",
                    colour=disnake.Colour.red(),
                )
                .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
                .add_field("Reason", reason, inline=False)
            )
            modlogs.log({
                "action":"ban",
                "user":user.id,
                "reason":reason
            })
            
    @mod.sub_command("warn", "Sends a user a warning")
    async def warn(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member, message: str, uwufy: bool = False):
        if uwufy == True:
            uwu = Uwuifier()
            message = uwu.uwuify_sentence(message)
        try:
            await user.send(
                embed=disnake.Embed(
                    title="You have been warned.",
                    colour=disnake.Colour.orange(),
                    description=f"You have been warned in the Datapack Hub server for the following reason:```\n{message}```",
                    timestamp=datetime.now(),
                )
            )
        except disnake.errors.Forbidden:
            await inter.response.send_message(
                f"I could not warn {user.mention} because either they have not enabled DMs from this server, or they have blocked the bot. Either way, they are a skibidi rizzler.",
                ephemeral=True,
            )
        except Exception as e:
            await inter.response.send_message(
                f"Failed to warn user {user.mention}: `{' '.join(e.args)}`",
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                f"Warned user {user.mention} for reason:```\n{message}```",
                ephemeral=True,
            )
            await inter.guild.get_channel(variables.modlogs).send(
                embed=disnake.Embed(
                    title="User Warned",
                    description=f"{user.name} (UID {user.id}) was warned.",
                    colour=disnake.Colour.red(),
                )
                .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
                .add_field("Warn Message", message, inline=False)
            )
            modlogs.log({
                "action":"warn",
                "user":user.id,
                "reason":message
            })
    
    @mod.sub_command("helpers","Show active helpers in the last few threads",)
    async def helpers(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        max = 15

        helper_data = []

        async def update_count(user: disnake.Member, role: disnake.Role):
            for member in helper_data:
                if member["username"] == user.name:
                    member["count"] += 1
                    return
            try:
                if role in user.roles:
                    helper_data.append({"username": user.name, "count": 1, "helper":True})
                else:
                    helper_data.append({"username": user.name, "count": 1, "helper":False})
            except:
                helper_data.append({"username": user.name, "count": 1, "helper":False})

        def escape_name(name: str) -> str:
            pattern: re.Pattern[str] = re.compile("[_~*|#`>-]")
            new_name: str = ""

            for char in name:
                if (re.match(pattern, char)):
                    new_name += f"\{char}"
                else:
                    new_name += char

            return new_name

        # Find helper role
        role = inter.guild.get_role(variables.helper)
        
        # Get all messages
        for channel in variables.help_channels:
            ch = inter.guild.get_channel(channel)

            # Get archived threads
            archived_threads = await ch.archived_threads().flatten()
            for thread in ch.threads + archived_threads:
                thread_owner = thread.owner_id
                async for message in thread.history():
                    if message.author.id != thread_owner and not message.author.bot:
                        # Increment count on the message author
                        await update_count(user=message.author, role=role)

        # Sort array by count
        helper_data = sorted(helper_data, key=lambda x: x['count'], reverse=True)

        # Construct embed body
        total = sum(helper["count"] for helper in helper_data)
        body = "This list is generated by counting the amount of messages sent by users in help threads which they did not create. It queries the messages from open threads and the previous 50 resolved threads.\n\n"

        index = 1
        for helper in helper_data[:max]:
            percentage = round((helper["count"] / total) * 100, 1)
            if helper["helper"]:
                body += f"{index!s}. 🔹 **{escape_name(helper['username'])}**: `{percentage!s}%` ({helper['count']})\n"
            else:
                body += f"{index!s}. **{escape_name(helper['username'])}**: `{percentage!s}%` ({helper['count']})\n"
            index += 1
        
        if len(helper_data) > max:
            body += f"\n{len(helper_data) - max!s} users were hidden from this list for having low message counts."
                        
        await inter.edit_original_message(embed=disnake.Embed(
            title="List of active helpers",
            description=body,
            colour=disnake.Colour.orange()
        ).add_field("Total messages queried",total))
        
    @mod.sub_command("user","Get moderation history of a user",)
    async def banall(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        logs = modlogs.get_logs(user.id)
        details = ""
        for i in logs:
            if i["action"] == "mute":
                details += f"**Mute** | {disnake.utils.format_dt(i['time'],'R')} for `{i['length']}` | *{i['reason']}*\n"
            elif i["action"] == "warn":
                details += f"**Warn** | {disnake.utils.format_dt(i['time'],'R')} | *{i['reason']}*\n"
            elif i["action"] == "ban":
                details += f"**Ban** | {disnake.utils.format_dt(i['time'],'R')} | *{i['reason']}*\n"
        
        emb = disnake.Embed(
            title=f"Moderation history for `{user.name}`",
            description=f"`{user.name}` has been moderated {len(logs)} times.\n\n**Most recent 10 logs**:\n{details}",
            colour=disnake.Colour.orange()
        ).set_thumbnail(user.avatar.url)
        await inter.response.send_message(embed=emb, ephemeral=True)

    
    @mod.sub_command("banall","Ban literally everyone",)
    async def banall(self, inter: disnake.ApplicationCommandInteraction):
        #legi go away
        emb = disnake.Embed(
            title="⚠️ BAN ALL MEMBERS",
            description="Are you sure? This action is IRREVERSIBLE. Flyne is going to be very angry if you run this command. ONLY USE THIS IN EMERGENCIES. You have been warned.",
            colour=disnake.Colour.dark_red()
        )
        await inter.response.send_message(embed=emb,components=[disnake.ui.Button(style=disnake.ButtonStyle.red,label="CONFIRM")])
