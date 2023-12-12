import disnake
from disnake.ext import commands
import requests

class SiteCommand(commands.Cog, name="site"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(title="site")
    async def site(self, inter: disnake.ApplicationCommandInteraction):
        return
    
    @site.sub_command("search",description="Search the datapackhub.net library")
    async def search(inter: disnake.ApplicationCommandInteraction, query: str):
        out = requests.get(f"https://api.datapackhub.net/projects/search?query={query}").json()
        results = ""
        for i in out["result"]:
            results += f"- [**{i['title']}**](https://datapackhub.net/project/{i['url']}), by [{i['author']['username']}](https://datapackhub.net/user/{i['author']['username']})\n"
            
        if results == "":
            results = "Your search found 0 results."

        await inter.response.send_message(embed=disnake.Embed(
            title="Search: " + query,
            description=results,
            color=disnake.Color.orange()
        ))
        
    @site.sub_command("project",description="View details about a DPH Project",options=[disnake.Option("slug","The slug (URL) of the datapack hub project.",required=True)])
    async def project(inter: disnake.ApplicationCommandInteraction, slug: str):
        out = requests.get(f"https://api.datapackhub.net/projects/get/{slug}").json()
        emb = disnake.Embed(
            title=out["title"],
            url=f"https://datapackhub.net/project/{out['url']}",
            description=out["description"],
            color=disnake.Color.orange(),
        ).set_author(name=out["author"]["username"],url=f"https://datapackhub.net/user/{out['author']['username']}",icon_url=out['author']['profile_icon']
        ).add_field("Updated",f"<t:{str(out['updated'])}:D>"
        ).set_thumbnail(out["icon"]
        ).add_field("Categories"," | ".join(out["category"])
        ).add_field("Downloads",str(out["downloads"]))
        
        await inter.response.send_message(embed=emb)