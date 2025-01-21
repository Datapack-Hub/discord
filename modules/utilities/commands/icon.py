import os
import disnake
from disnake.ext import commands

ICONS = list(map(lambda s:  s.removesuffix(".gif"),os.listdir(os.path.join(os.getcwd(), "static", "icons"))))

class IconCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="icon", description="Changes the icon of the server.")
    async def icon(
        self,
        inter: disnake.ApplicationCommandInteraction,
        icon_type: str = commands.Param(
            default="Normal",
            choices=ICONS
        )
    ):
        try:
            with open(os.path.join(os.getcwd(), "static", "icons", f"{icon_type}.gif"), "rb") as image_file:
                icon_data = image_file.read()

            await inter.guild.edit(icon=icon_data)
            await inter.send("Guild icon updated.", ephemeral=True)
        except Exception as e:
            await inter.send(f"Updating guild icon failed: {''.join(e.args)}", ephemeral=True)
        