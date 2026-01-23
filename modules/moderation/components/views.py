import discord
from modules.moderation.components.buttons import BanUserModPanelButton, QuickBanUserModPanelButton, KickUserModPanelButton, MuteUserModPanelButton, WarnUserModPanelButton

class UserModPanelView(discord.ui.DesignerView):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=None)
        
        container = discord.ui.Container()
        
        container.add_text(f"## Moderating `{user.name}`")
        container.add_text(f"{user.name} joined this server {discord.utils.format_dt(user.joined_at, style='R')} and joined discord {discord.utils.format_dt(user.created_at, style='R')}. Take action on them below:")
        
        container.add_item(BanUserModPanelButton(user))
        container.add_item(QuickBanUserModPanelButton(user))
        container.add_item(KickUserModPanelButton(user))
        container.add_item(MuteUserModPanelButton(user))
        container.add_item(WarnUserModPanelButton(user))
        
        self.add_item(container)