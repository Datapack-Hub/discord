import disnake
from disnake.ext import commands

MESSAGE = """
**If you've got a question, please head to the help channels**
- <#1051225367807000706> for questions about datapacks
- <#1051227454980755546> for questions about resource packs
- <#1143095605577654392> for anything else
More info about the help channels can be found in <#935570290317086841>.

*If you can't see the above channels, make sure you have `Show All Channels` enabled in the server menu.*
"""

class RedirectCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Redirect to help channel")
    async def redirect(self, inter: disnake.MessageCommandInteraction):
        embed = disnake.Embed(
            title="Please ask this in the help channels!",
            description=MESSAGE,
            color=disnake.Colour.orange(),
        ).set_footer(
            text="Requested by " + inter.author.display_name,
            icon_url=inter.author.display_avatar.url,
        )
        await inter.target.reply(embed=embed)
        await inter.response.send_message("Sent message", ephemeral=True)
