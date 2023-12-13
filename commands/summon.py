import disnake
from disnake.ext import commands
import variables


class SummonCommand(commands.Cog, name="summon"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="plzsomebodyhelpthisguy", description="Summon helpers")
    async def summon(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(f"Psst, <@&{variables.helper}>!")
