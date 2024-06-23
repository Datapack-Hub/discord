import disnake
from disnake.ext import commands
import utils.log as Log


class TopCommand(commands.Cog, name="top"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(title="top", description="Jump to the top of the thread or channel!")
    async def top(self, inter: disnake.ApplicationCommandInteraction):
        message = await inter.channel.history(limit=1, oldest_first=True).flatten()

        await inter.response.send_message(
            components=[disnake.ui.Button(label="Jump to top", url=message[0].jump_url)],
            ephemeral=True
        )

        Log.info(f"{inter.author.name} jumped to the top of channel #{inter.channel.name}")