import discord

import utils.log as Log
import variables
from modules.moderation.components.views import MessageModPanelView, UnableToModerateView


class ModerateCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(name="Moderate")
    async def moderate(self, inter: discord.ApplicationContext, message: discord.Message):
        Log.info("opened mod panel for a message", inter.author.name)
        
        if message.author.bot or (inter.guild.get_role(variables.staff) in message.author.roles):
            return await inter.respond(view=UnableToModerateView(), ephemeral=True)
        
        if (not inter.guild.get_role(variables.moderator) in inter.author.roles):
            return await inter.respond(view=MessageModPanelView(message.author, message, helper_only=True), ephemeral=True)

        return await inter.respond(view=MessageModPanelView(message.author, message), ephemeral=True)