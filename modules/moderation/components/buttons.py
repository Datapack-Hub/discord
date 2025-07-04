import discord
from modules.moderation.components.modals import BanUserModPanelModal, KickUserModPanelModal, MuteUserModPanelModal, WarnUserModPanelModal

class BanUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member):
        self.user = user
        
        super().__init__(
            label="Ban",
            custom_id="ban_user_button",
            style=discord.ButtonStyle.red
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(BanUserModPanelModal(self.user))
        
class QuickBanUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member):
        self.user = user
        
        super().__init__(
            label="Quick Ban",
            custom_id="quick_ban_user_button",
            style=discord.ButtonStyle.red
        )
        
    async def callback(self, inter: discord.Interaction):
        await self.user.ban(reason="Quick ban")
        await inter.respond("Banned user " + self.user.name,ephemeral=True)

class KickUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member):
        self.user = user
        
        super().__init__(
            label="Kick",
            custom_id="kick_user_button",
            style=discord.ButtonStyle.blurple
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(KickUserModPanelModal(self.user))
        
class MuteUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member):
        self.user = user
        
        super().__init__(
            label="Mute",
            custom_id="mute_user_button",
            style=discord.ButtonStyle.blurple
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(MuteUserModPanelModal(self.user))
        
class WarnUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member):
        self.user = user
        
        super().__init__(
            label="Warn",
            custom_id="warn_user_button",
            style=discord.ButtonStyle.gray
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(WarnUserModPanelModal(self.user))