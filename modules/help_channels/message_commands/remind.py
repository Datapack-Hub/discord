import discord
from discord.ext import commands
import utils.log as Log
from modules.help_channels.components.views import ReminderMessageView


class RemindCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Remind them to resolve thread")
    async def remind(self, inter: discord.ApplicationContext, message: discord.Message):
        # Send embed with resolve button
        await message.reply(view=ReminderMessageView())
        
        # Send confirmation message
        await inter.respond("Done!",ephemeral=True)
        
        Log.info(f"{inter.author.name} reminded OP to resolve the channel #{inter.channel.name}")
