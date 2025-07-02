import discord
from discord.ext import commands
import utils.log as Log
import variables

MESSAGE = """
**If you've got a question, please head to the help channels**
- <#1051225367807000706> for questions about datapacks and commands
- <#1051227454980755546> for questions about resource packs
- <#1143095605577654392> for anything else

*If you can't see the above channels, make sure you have `Show All Channels` enabled in the server menu.*
"""

WRONG_CHANNEL_MESSAGE = """
Your post is not suited for this channel. To keep the server tidy and organised, please ask it again in the correct one of the following:
- <#1051225367807000706> for questions about datapacks and commands
- <#1051227454980755546> for questions about resource packs
- <#1143095605577654392> for anything else

*If you can't see the above channels, make sure you have `Show All Channels` enabled in the server menu.*
"""


class RedirectCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Redirect to help channel")
    async def redirect(self, inter: discord.ApplicationContext, message: discord.Message):
        embed = discord.Embed(
            title="Please ask this in the help channels!",
            description=MESSAGE,
            colour=discord.Colour.orange(),
        )
        
        # python :D :D :D
        try:
            if message.channel.parent.id in variables.help_channels + [1143095605577654392]:
                embed = discord.Embed(
                    title="This is the wrong channel.",
                    description=WRONG_CHANNEL_MESSAGE,
                    color=discord.Colour.red()
                )
        except:
            pass
            
        embed.set_footer(
            text="Requested by " + inter.author.display_name,
            icon_url=inter.author.display_avatar.url,
        )
        await message.reply(embed=embed)
        await inter.response.send_message("Sent message", ephemeral=True)
        
        Log.info(f"{inter.author.name} redirected the user {message.author.name} to help channels in #{inter.channel.name}")
