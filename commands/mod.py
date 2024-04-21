import disnake
from disnake.ext import commands
from pytimeparse.timeparse import timeparse
from datetime import datetime, timedelta
import variables
import io

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
        await inter.response.defer(ephemeral=True)
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = False
        current_perms.send_messages_in_threads = False
        current_perms.create_public_threads = False
        current_perms.add_reactions = False
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.edit_original_message(f"Locked down the server")
        
    @mod.sub_command("unlockdown","Unlocks all server channels",)
    async def unlockdown(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = True
        current_perms.send_messages_in_threads = True
        current_perms.create_public_threads = True
        current_perms.add_reactions = True
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.edit_original_message(f"Unlocked the server")
            
        
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
            color=disnake.Colour.orange(),
            title="**`/purge` Command**",
            description=f"{inter.user.name} purged {len(deleted_messages)} messages in {inter.channel.mention}.",
        )

        # Add the autor and contents of the deleted messages to the log
        file_content = io.StringIO()
        for messages in deleted_messages:
            file_content.write(
                f"[{datetime.utcnow().strftime('%d/%m/%y %H:%M:%S')}] @{messages.author.name}: {messages.content}\n"
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
    async def mute(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member,
        length: str,
    ):
        seconds = timeparse(length)
        embed = disnake.Embed(
            title="Are you sure?",
            description=f"You're going to mute user {user.mention} - they'll be unmuted in {generate_discord_relative_timestamp(seconds)}.\n\nTo add a reason, select an option from the dropdown",
        )
        return await inter.send(
            embed=embed, ephemeral=True, view=MuteDropdownView(user, seconds)
        )

    @mod.sub_command("ban", "Bans a member for a length of time")
    async def ban(
        self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member
    ):
        embed = disnake.Embed(
            title="Are you sure?",
            description=f"You're going to ban user {user.mention}.\n\nTo add a reason, select an option from the dropdown",
        )
        return await inter.send(embed=embed, ephemeral=True, view=BanDropdownView(user))
    
    @mod.sub_command("helpers","Show active helpers in the last few threads",)
    async def info(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        MAX = 15

        helper_data = []
        
        def update_count(username):
            for member in helper_data:
                if member["username"] == username:
                    member["count"] += 1
                    return
            helper_data.append({"username": username, "count": 1})
        
        # Get all messages
        for channel in variables.help_channels:
            channel = inter.guild.get_channel(channel)
            
            # Get archived threads
            archived = await channel.archived_threads().flatten()
            for thread in channel.threads + archived:
                thread_owner = thread.owner_id
                async for message in thread.history():
                    if message.author.id != thread_owner and not message.author.bot:
                        # Increment count on the message author
                        update_count(message.author.name)
                        
        # Sort array by count
        helper_data = sorted(helper_data, key=lambda x: x['count'], reverse=True)
        
        # Construct embed body
        total = sum(helper["count"] for helper in helper_data)
        body = "This list is generated by counting the amount of messages sent by users in help threads which they did not create. It queries the messages from open threads and the previous 50 resolved threads.\n\n"
        
        index = 1
        for helper in helper_data[:MAX]:
            percentage = round((helper["count"] / total) * 100, 1)
            body += f"{index!s}. **{helper['username']}**: `{percentage!s}%` ({helper['count']})\n"
            index += 1
        
        if len(helper_data) > MAX:
            body += f"\n{len(helper_data - MAX)!s} users were hidden from this list for having low message counts."
                        
        await inter.edit_original_message(embed=disnake.Embed(
            title="List of active helpers",
            description=body,
            color=disnake.Colour.orange()
        ).add_field("Total messages queried",total))
                            


# Mute
class NoMuteReason(disnake.ui.Button):
    def __init__(self, target: disnake.Member, length: int):
        self.target = target
        self.length = length

        super().__init__(
            label="Mute without adding a reason", style=disnake.ButtonStyle.red
        )

    async def callback(self, inter: disnake.MessageInteraction):
        try:
            await self.target.timeout(duration=self.length, reason="no")
        except disnake.errors.Forbidden:
            await inter.response.send_message(
                f"Failed to mute user {self.target.mention}: I don't have permission to do this.",
                ephemeral=True,
            )
        except:
            await inter.response.send_message(
                f"Failed to mute user {self.target.mention}: Unknown Error",
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                f"Muted user {self.target.mention}", ephemeral=True
            )
            await inter.guild.get_channel(variables.modlogs).send(
                embed=disnake.Embed(
                    title="User Muted",
                    description=f"{self.target.name} (UID {self.target.id}) was muted.",
                    color=disnake.Color.red(),
                )
                .set_author(
                    name=inter.author.global_name, icon_url=inter.author.avatar.url
                )
                .add_field("Reason", "N/A", inline=False)
                .add_field(
                    "Expires",
                    generate_discord_relative_timestamp(self.length),
                    inline=False,
                )
            )


class MuteDropdown(disnake.ui.StringSelect):
    def __init__(self, target: disnake.Member, length: int):
        self.target = target
        self.length = length
        options = [
            disnake.SelectOption(
                label=reason["label"], description=reason["description"]
            )
            for reason in REASONS
        ]

        options.append(disnake.SelectOption(label="Custom"))

        super().__init__(
            placeholder="Choose a reason...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        reason = None
        for r in REASONS:
            if r["label"] == self.values[0]:
                reason = r

        if reason is None:
            await inter.response.send_modal(
                ReasonModal("mute", self.target, self.length)
            )
        else:
            try:
                await self.target.timeout(duration=self.length, reason=reason["label"])
            except disnake.errors.Forbidden:
                await inter.response.send_message(
                    f"Failed to mute user {self.target.mention}: I don't have permission to do this.",
                    ephemeral=True,
                )
            except Exception as e:
                await inter.response.send_message(
                    f"Failed to mute user {self.target.mention}: `{' '.join(e.args)}`",
                    ephemeral=True,
                )
            else:
                await inter.response.send_message(
                    f"Muted user {self.target.mention} for reason:```\n{reason['description']}```",
                    ephemeral=True,
                )
                await self.target.send(
                    embed=disnake.Embed(
                        title="You were muted",
                        color=disnake.Color.red(),
                        description=f"You were muted in Datapack Hub. You'll be unmuted {generate_discord_relative_timestamp(self.length)}.\n\nReason:```\n{reason['description']}```",
                        timestamp=datetime.utcnow(),
                    )
                )
                await inter.guild.get_channel(variables.modlogs).send(
                    embed=disnake.Embed(
                        title="User Muted",
                        description=f"{self.target.name} (UID {self.target.id}) was muted.",
                        color=disnake.Color.red(),
                    )
                    .set_author(
                        name=inter.author.global_name, icon_url=inter.author.avatar.url
                    )
                    .add_field("Reason", reason["description"], inline=False)
                    .add_field(
                        "Expires",
                        generate_discord_relative_timestamp(self.length),
                        inline=False,
                    )
                )


class MuteDropdownView(disnake.ui.View):
    def __init__(self, target: disnake.Member, length: int):
        super().__init__()

        self.add_item(MuteDropdown(target, length))
        self.add_item(NoMuteReason(target, length))


## BAN
class NoBanReason(disnake.ui.Button):
    def __init__(self, target: disnake.Member):
        self.target = target

        super().__init__(
            label="Ban without adding a reason", style=disnake.ButtonStyle.red
        )

    async def callback(self, inter: disnake.MessageInteraction):
        try:
            await self.target.ban(reason="no")
        except disnake.errors.Forbidden:
            await inter.response.send_message(
                f"Failed to ban user {self.target.mention}: I don't have permission to do this.",
                ephemeral=True,
            )
        except:
            await inter.response.send_message(
                f"Failed to ban user {self.target.mention}: Unknown Error",
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                f"Banned user {self.target.mention}", ephemeral=True
            )
            await inter.guild.get_channel(variables.modlogs).send(
                embed=disnake.Embed(
                    title="User Banned",
                    description=f"{self.target.name} (UID {self.target.id}) was banned.",
                    color=disnake.Color.red(),
                )
                .set_author(
                    name=inter.author.global_name, icon_url=inter.author.avatar.url
                )
                .add_field("Reason", "N/A", inline=False)
            )


class BanDropdown(disnake.ui.StringSelect):
    def __init__(self, target: disnake.Member):
        self.target = target
        options = [
            disnake.SelectOption(
                label=reason["label"], description=reason["description"]
            )
            for reason in REASONS
        ]

        options.append(disnake.SelectOption(label="Custom"))

        super().__init__(
            placeholder="Choose a reason...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        reason = None
        for r in REASONS:
            if r["label"] == self.values[0]:
                reason = r

        if reason is None:
            await inter.response.send_modal(ReasonModal("ban", self.target, 0))
        else:
            try:
                await self.target.send(
                    embed=disnake.Embed(
                        title="You were banned",
                        color=disnake.Color.red(),
                        description=f"You were banned in Datapack Hub.\n\nReason:```\n{reason['description']}```",
                        timestamp=datetime.utcnow(),
                    )
                )
                await self.target.ban(reason=reason["description"])
            except disnake.errors.Forbidden:
                await inter.response.send_message(
                    f"Failed to ban user {self.target.mention}: I don't have permission to do this.",
                    ephemeral=True,
                )
            except Exception as e:
                await inter.response.send_message(
                    f"Failed to ban user {self.target.mention}: `{' '.join(e.args)}`",
                    ephemeral=True,
                )
            else:
                await inter.response.send_message(
                    f"Banned user {self.target.mention} for reason:```\n{reason['label']}```",
                    ephemeral=True,
                )
                await inter.guild.get_channel(variables.modlogs).send(
                    embed=disnake.Embed(
                        title="User Banned",
                        description=f"{self.target.name} (UID {self.target.id}) was banned.",
                        color=disnake.Color.red(),
                    )
                    .set_author(
                        name=inter.author.global_name, icon_url=inter.author.avatar.url
                    )
                    .add_field("Reason", reason["description"], inline=False)
                )


class BanDropdownView(disnake.ui.View):
    def __init__(self, target: disnake.Member):
        super().__init__()

        self.add_item(BanDropdown(target))
        self.add_item(NoBanReason(target))


class ReasonModal(disnake.ui.Modal):
    def __init__(self, action: str, user: disnake.Member, length: int) -> None:
        self.action = action
        self.user = user
        self.length = length
        components = [
            disnake.ui.TextInput(
                label="Reason",
                placeholder="Being a very silly person",
                custom_id="reason",
                style=disnake.TextInputStyle.paragraph,
                min_length=10,
                max_length=500,
            ),
        ]
        super().__init__(
            title=f"{action.upper()} User: {user.name}",
            custom_id="mod_reason",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        if self.action == "mute":
            try:
                await self.user.timeout(
                    duration=self.length, reason=inter.text_values["reason"]
                )
            except disnake.errors.Forbidden:
                await inter.response.send_message(
                    f"Failed to mute user {self.user.mention}: I don't have permission to do this.",
                    ephemeral=True,
                )
            except Exception as e:
                await inter.response.send_message(
                    f"Failed to mute user {self.user.mention}: `{' '.join(e.args)}`",
                    ephemeral=True,
                )
            else:
                await inter.response.send_message(
                    f"Muted user {self.user.mention} for reason:```\n{inter.text_values['reason']}```",
                    ephemeral=True,
                )
                await self.user.send(
                    embed=disnake.Embed(
                        title="You were muted",
                        color=disnake.Color.red(),
                        description=f"You were muted in Datapack Hub until {generate_discord_relative_timestamp(self.length)}.\n\nReason:```\n{inter.text_values['reason']}```",
                        timestamp=datetime.utcnow(),
                    )
                )
                await inter.guild.get_channel(variables.modlogs).send(
                    embed=disnake.Embed(
                        title="User Muted",
                        description=f"{self.user.name} (UID {self.user.id}) was muted.",
                        color=disnake.Color.red(),
                    )
                    .set_author(
                        name=inter.author.global_name, icon_url=inter.author.avatar.url
                    )
                    .add_field("Reason", inter.text_values["reason"], inline=False)
                    .add_field(
                        "Expires",
                        generate_discord_relative_timestamp(self.length),
                        inline=False,
                    )
                )
        elif self.action == "ban":
            try:
                await self.user.send(
                    embed=disnake.Embed(
                        title="You were banned",
                        color=disnake.Color.red(),
                        description=f"You were banned in Datapack Hub.\n\nReason:```\n{inter.text_values['reason']}```",
                        timestamp=datetime.utcnow(),
                    )
                )
                await self.user.ban(reason=inter.text_values["reason"])
            except disnake.errors.Forbidden:
                await inter.response.send_message(
                    f"Failed to ban user {self.user.mention}: I don't have permission to do this.",
                    ephemeral=True,
                )
            except Exception as e:
                await inter.response.send_message(
                    f"Failed to ban user {self.user.mention}: `{' '.join(e.args)}`",
                    ephemeral=True,
                )
            else:
                await inter.response.send_message(
                    f"Banned user {self.user.mention} for reason:```\n{inter.text_values['reason']}```",
                    ephemeral=True,
                )
                await inter.guild.get_channel(variables.modlogs).send(
                    embed=disnake.Embed(
                        title="User Banned",
                        description=f"{self.user.name} (UID {self.user.id}) was banned.",
                        color=disnake.Color.red(),
                    )
                    .set_author(
                        name=inter.author.global_name, icon_url=inter.author.avatar.url
                    )
                    .add_field("Reason", inter.text_values["reason"], inline=False)
                )

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.", ephemeral=True)
