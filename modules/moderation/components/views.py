import discord
from datetime import datetime, timedelta

def generate_discord_relative_timestamp(seconds):
    future_timestamp = int((datetime.now() + timedelta(seconds=seconds)).timestamp())
    formatted_timestamp = f"<t:{future_timestamp}:R>"
    return formatted_timestamp

def generate_discord_full_timestamp(seconds):
    future_timestamp = int((datetime.now() + timedelta(seconds=seconds)).timestamp())
    formatted_timestamp = f"<t:{future_timestamp}:f>"
    return formatted_timestamp

class UserModPanelView(discord.ui.DesignerView):
    def __init__(self, user: discord.Member):
        from modules.moderation.components.buttons import BanUserModPanelButton, QuickBanUserModPanelButton, KickUserModPanelButton, MuteUserModPanelButton, WarnUserModPanelButton
        
        super().__init__(timeout=None)
        
        container = discord.ui.Container()
        
        container.add_text(f"## Moderating `{user.name}`")
        container.add_text(f"{user.name} joined this server {discord.utils.format_dt(user.joined_at, style='R')} and joined discord {discord.utils.format_dt(user.created_at, style='R')}. Take action on them below:")
        
        container.add_row(
            BanUserModPanelButton(user), 
            QuickBanUserModPanelButton(user),
            KickUserModPanelButton(user),
            MuteUserModPanelButton(user),
            WarnUserModPanelButton(user)
        )
        
        self.add_item(container)

class MessageModPanelView(discord.ui.DesignerView):
    def __init__(self, user: discord.Member, message: discord.Message):
        from modules.moderation.components.buttons import BanUserModPanelButton, QuickBanUserModPanelButton, KickUserModPanelButton, MuteUserModPanelButton, WarnUserModPanelButton
        
        super().__init__(timeout=None)
        
        container = discord.ui.Container()
        
        container.add_text(f"## Moderating `{user.name}`")
        container.add_text(f"{user.name} joined this server {discord.utils.format_dt(user.joined_at, style='R')} and joined discord {discord.utils.format_dt(user.created_at, style='R')}. Take action on them below:")
        
        container.add_row(
            BanUserModPanelButton(user, cause_message=message), 
            QuickBanUserModPanelButton(user, cause_message=message),
            KickUserModPanelButton(user, cause_message=message),
            MuteUserModPanelButton(user, cause_message=message),
            WarnUserModPanelButton(user, cause_message=message)
        )

        container.add_separator()

        container.add_text(f"-# You are moderating `{user.name}` with reference to the selected message. **The user will see a copy of their message along with the reason you provide.** 5heir message will be deleted when an action is taken.")
        
        self.add_item(container)

MESSAGES = [
    {
        "type":"warn",
        "heading": "You were warned in Datapack Hub",
        "long":"A moderator has warned you in Datapack Hub. Please take a moment to read the reason attached, and figure out how you can be a better part of the community. This warning doesn't impact your ability to interact with the server.",
        "long_no_reason":"A moderator has warned you in Datapack Hub. This warning doesn't impact your ability to interact with the server."
    },
    {
        "type":"mute",
        "heading": "You were muted in Datapack Hub",
        "long":"A moderator has temporarily muted you in Datapack Hub. Please take a moment to read the reason attached, and figure out how you can be a better part of the community. You won't be able to interact with the community until the time has elapsed.",
        "long_no_reason":"A moderator has temporarily muted you in Datapack Hub. You won't be able to interact with the community until the time has elapsed."
    },
    {
        "type":"kick",
        "heading": "You were kicked from Datapack Hub",
        "long":"A moderator has removed you from Datapack Hub. Please take a moment to read the reason attached, and figure out how you can be a better part of the community. You are able to rejoin the server, but please acknowledge and use the reason attached to improve yourself if you choose to rejoin.",
        "long_no_reason":"A moderator has removed you from Datapack Hub. You are able to rejoin the server, but it may be wise to wait a while before doing so."
    },
    {
        "type":"ban",
        "heading": "You were banned from Datapack Hub",
        "long":"A moderator has banned you from Datapack Hub. The reason for this is attached below. You will not be able to rejoin the server unless you are unbanned.",
        "long_no_reason":"A moderator has banned you from Datapack Hub. You will not be able to rejoin the server unless you are unbanned."
    }
]

class PunishmentMessageView(discord.ui.DesignerView):
    def __init__(self, type: str, message: str | None = None, cause: discord.Message | None = None, expires: int | None = None):
        super().__init__(timeout=None)

        container = discord.ui.Container(color=discord.Color.from_rgb(222, 40, 65))
    
        msg_data = next((msg for msg in MESSAGES if msg["type"] == type), None)
        if not msg_data:
            return
        
        container.add_text("## " + msg_data["heading"])
        if message:
            container.add_text(msg_data["long"])
            container.add_separator(divider=False)
            container.add_text(f"### Moderator's reason:\n```\n{message}\n```")
        else:
            container.add_text(msg_data["long_no_reason"])
        
        if cause:
            container.add_separator(divider=False)
            container.add_text(f"### Your message (shown below) was the cause of this action:\n**{cause.author.name}**: <t:{int(cause.created_at.timestamp())!s}:R>: ```\n{discord.utils.remove_markdown(cause.clean_content)[:300]}```")

        if expires:
            container.add_separator(divider=False)
            container.add_text(f"### This will expire at the following time:\n{generate_discord_full_timestamp(expires)} ({generate_discord_relative_timestamp(expires)})")

        container.add_text("-# This action was taken by a moderator or admin. If you think this was a mistake, please contact a staff member.")

        self.add_item(container)