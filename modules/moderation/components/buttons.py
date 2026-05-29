import discord
import variables
from modules.moderation.components.modals import BanUserModPanelModal, KickUserModPanelModal, MuteUserModPanelModal, WarnUserModPanelModal
from modules.moderation.components.views import FeedbackView

class BanUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None):
        self.user = user
        self.cause_message = cause_message
        
        super().__init__(
            label="Ban",
            custom_id="ban_user_button",
            style=discord.ButtonStyle.red
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(BanUserModPanelModal(self.user, cause_message=self.cause_message))
        
class QuickBanUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None):
        self.user = user
        self.cause_message = cause_message
        
        super().__init__(
            label="Softban",
            custom_id="soft_ban_user_button",
            style=discord.ButtonStyle.red
        )
        
    async def callback(self, inter: discord.Interaction):
        try:
            await self.user.ban(delete_message_seconds=86400,reason="Softban")
            await self.user.unban(reason="Softban")
        except Exception as err:
            await inter.respond("I couldn't fully softban this user. This error has been recorded.", allowed_mentions=discord.AllowedMentions(replied_user=False, roles=True), ephemeral=True)
            
            raise err
        else:
            await inter.respond(view=FeedbackView([
                "## User softbanned",
                f"Successfully softbanned user {self.user.mention} ({self.user.id!s})."
            ]),ephmeral=True)
            
            log_embed = discord.Embed(
                title="User Softbanned",
                description=f"{self.user.name} (UID {self.user.id}) was softbanned.",
                colour=discord.Colour.red(),
            )
            log_embed.set_author(name=inter.user.global_name, icon_url=inter.user.avatar.url)

            await inter.client.get_channel(variables.modlogs).send(embed=log_embed)


class KickUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None):
        self.user = user
        self.cause_message = cause_message
        
        super().__init__(
            label="Kick",
            custom_id="kick_user_button",
            style=discord.ButtonStyle.blurple
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(KickUserModPanelModal(self.user, cause_message=self.cause_message))
        
class MuteUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None):
        self.user = user
        self.cause_message = cause_message
        
        super().__init__(
            label="Mute",
            custom_id="mute_user_button",
            style=discord.ButtonStyle.blurple
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(MuteUserModPanelModal(self.user, cause_message=self.cause_message))
        
class WarnUserModPanelButton(discord.ui.Button):
    def __init__(self, user: discord.Member, cause_message: discord.Message | None = None):
        self.user = user
        self.cause_message = cause_message
        
        super().__init__(
            label="Warn",
            custom_id="warn_user_button",
            style=discord.ButtonStyle.gray
        )
        
    async def callback(self, inter: discord.Interaction):
        await inter.response.send_modal(WarnUserModPanelModal(self.user, cause_message=self.cause_message))