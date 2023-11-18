import disnake
from disnake.ext import commands


class RedirectCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Redirect to help channel")
    async def redirect(self, inter: disnake.MessageCommandInteraction):
        # embed = disnake.Embed().set_image("https://cdn.discordapp.com/attachments/723984082853298297/1153381044322570260/Z.png")
        embed = disnake.Embed(
            title="This should go in a help chat!",
            description="""
            **There's a better place for this question - the help channels!**
            We think that this question would be better if you asked it in a designated help channel. If you ask in a help channel, you'll get help quicker from one of our official helpers.
            
            If you can't see the help channels, make sure that you have "Show All Channels" visible in your server settings.
            
            Check out <#935570290317086841> for more information about our help channels.
            """,
            color=disnake.Colour.orange(),
        ).set_footer(
            text="Requested by " + inter.author.display_name,
            icon_url=inter.author.display_avatar.url,
        )
        await inter.target.reply(embed=embed)
        await inter.response.send_message("Done! :D", ephemeral=True)
