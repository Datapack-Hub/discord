import discord
from discord.ext import commands
import utils.log as Log
import variables
from modules.help_channels.components.views import RedirectMessageView, WrongChannelMessageView


class RedirectCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Redirect to help channel")
    async def redirect(self, inter: discord.ApplicationContext, message: discord.Message):
        try: message.channel.parent
        except: await message.reply(view=RedirectMessageView())
        else:
            if message.channel.parent.id in variables.help_channels + [1143095605577654392]:
                await message.reply(view=WrongChannelMessageView())
            else:
                await message.reply(view=RedirectMessageView())
        
        await inter.response.send_message("Done!", ephemeral=True)
        
        Log.info(f"{inter.author.name} redirected the user {message.author.name} to help channels in #{inter.channel.name}")
