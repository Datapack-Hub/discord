import disnake
from disnake.ext import commands


class ServerCommand(commands.Cog, name="server"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="server")
    async def server(self, inter: disnake.ApplicationCommandInteraction):
        return
    
    @server.sub_command("wordcloud","Generate a wordcloud")
    async def image(self, inter: disnake.ApplicationCommandInteraction):