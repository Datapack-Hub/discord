import discord

import utils.log as Log
import variables
from modules.moderation.components.views import MessageModPanelView


class ModerateCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(name="Moderate")
    async def moderate(self, inter: discord.ApplicationContext, message: discord.Message):
        await inter.respond(view=MessageModPanelView(message.author, message), ephemeral=True)