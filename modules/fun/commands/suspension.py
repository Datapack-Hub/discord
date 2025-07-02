import random

import discord
from discord.ext import commands

IMAGES = [
    {
        "url":"https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Wuppertal-100508-12833-Uferstra%C3%9Fe.jpg/1280px-Wuppertal-100508-12833-Uferstra%C3%9Fe.jpg",
        "title":"Schwebebahn monorail in Wuppertal, Germany",
        "credits":"Mbdortmund, GFDL 1.2 http://www.gnu.org/licenses/old-licenses/fdl-1.2.html, via Wikimedia Commons"
    },
    {
        "url":"https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Optics_Valley_Suspended_Monorail_%2810%29.jpg/800px-Optics_Valley_Suspended_Monorail_%2810%29.jpg",
        "title":"Optics Valley Suspension Railway",
        "credits":"Painjet, CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0>, via Wikimedia Commons"
    },
    {
        "url":"https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Optics_Valley_Suspended_Monorail_%284%29.jpg/640px-Optics_Valley_Suspended_Monorail_%284%29.jpg",
        "title":"Optics Valley Suspension Railway",
        "credits":"Painjet, CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0>, via Wikimedia Commons"
    },
    {
        "url":"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Memphis_Suspension_Railway_%281%29.jpg/800px-Memphis_Suspension_Railway_%281%29.jpg?20230701171934",
        "title":"Memphis Suspension Railway",
        "credits":"Heipedia, CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0>, via Wikimedia Commons"
    },
    {
        "url":"https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Chiba_monorail%2C_Japan%3B_September_2016_%2812%29.jpg/640px-Chiba_monorail%2C_Japan%3B_September_2016_%2812%29.jpg",
        "title":"Chiba Suspension Railway",
        "credits":"Gary Lee Todd, Ph.D., CC0, via Wikimedia Commons"
    },
    {
        "url":"https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Chiba_monorail%2C_Japan%3B_September_2016_%2809%29.jpg/640px-Chiba_monorail%2C_Japan%3B_September_2016_%2809%29.jpg",
        "title":"Chiba Suspension Railway",
        "credits":"Gary Lee Todd, Ph.D., CC0, via Wikimedia Commons"
    },
    {
        "url":"https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Daizouin_temple_suspended_monorail.jpg/640px-Daizouin_temple_suspended_monorail.jpg",
        "title":"Daizouin Temple Suspension Railway",
        "credits":"Gary Lee Todd, Ph.D., CC0, via Wikimedia Commons"
    }
]


class SuspensionRailwayCommand(commands.Cog, name="suspension_railway"):
    def __init__(self, bot):
        self.bot = bot

    susprail = discord.SlashCommandGroup(name="susprail")
    
    @susprail.command(description="Generate a random image of a suspension railway")
    async def image(self, inter: discord.ApplicationContext):
        image = random.choice(IMAGES)
        embed = discord.Embed(
            title=image["title"],
            colour=discord.Colour.blue()
        ).set_image(url=image["url"]).set_footer(text=image["credits"])
        await inter.response.send_message(embed=embed)
        
    @susprail.command(description="Learn about suspension railways")
    async def info(self, inter: discord.ApplicationContext):
        embed = discord.Embed(
            title="Learn about Suspension Railways",
            colour=discord.Colour.blue()
        )
        embed.add_field(
            name="What are suspension railways?",
            value="A suspension railway is a type of elevated monorail. The suspension railway vehicles are suspended from a single, fixed track (not a cable). This makes them good for being built above streets or even other railway types.",
            inline=False
        )
        embed.add_field(
            name="What suspension railways are there?",
            value="There are many suspension railways including the following:\n- **Schwebebahn** in Wuppertal, Germany\n- **Schwebebahn** in Dresden, Germany\n- **H-Bahn** in TU Dortmund, Germany\n- **Sky train** in Dusseldorf Airport, Germany\n- **Strela** in Glukhovo , Russia\n- **Shonan** in Kanagawa Prefecture, Japan\n- **Chiba Urban** in Chiba, Japan\n- **SkyTrain** in Chengdu, China\n- **Optics Valley** in Wuhan, China\n- **Red Rail** in Xingguo, China",
            inline=False
        )
        await inter.response.send_message(embed=embed)