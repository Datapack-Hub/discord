import disnake
from disnake.ext import commands
import utils.log as Log

MESSAGE = """
**If you've got a question, please head to the help channels**
- <#1051225367807000706> for questions about datapacks and commands
- <#1051227454980755546> for questions about resource packs
- <#1143095605577654392> for anything else

*If you can't see the above channels, make sure you have `Show All Channels` enabled in the server menu.*
"""

WRONG_CHANNEL_MESSAGE = """
Please ask this question again in the correct channel. This channel is **not** for help with datapacks, resource packs, or commands.
- <#1051225367807000706> for questions about datapacks and commands
- <#1051227454980755546> for questions about resource packs

*If you can't see the above channels, make sure you have `Show All Channels` enabled in the server menu.*
"""


class RedirectCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Redirect to help channel")
    async def redirect(self, inter: disnake.MessageCommandInteraction):
        if inter.target.channel.id == 1143095605577654392:
            embed = disnake.Embed(
                title="This is the wrong channel.",
                description=WRONG_CHANNEL_MESSAGE,
                color=disnake.Color.red()
            )
        else: 
            embed = disnake.Embed(
                title="Please ask this in the help channels!",
                description=MESSAGE,
                colour=disnake.Colour.orange(),
            )
            
        embed.set_footer(
            text="Requested by " + inter.author.display_name,
            icon_url=inter.author.display_avatar.url,
        )
        await inter.target.reply(embed=embed)
        await inter.response.send_message("Sent message", ephemeral=True)
        
        Log.info(f"{inter.author.name} redirected the user {inter.target.author.name} to help channels in #{inter.channel.name}")
