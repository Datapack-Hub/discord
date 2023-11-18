import disnake
from disnake.ext import commands
import json


def value_getter(item):
    return item[1]


class TopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="top", description="View the most helpful members of the server."
    )
    async def top(self, inter: disnake.MessageCommandInteraction):
        with open("/root/dph_bot/discord/points.json", "r") as fp:
            fp.seek(0)
            data = json.loads(fp.read())
            fp.close()
        asc = sorted(data.items(), key=value_getter)
        asc = asc[0:9]
        asc.reverse()
        text = ""
        for i in asc:
            text += f"**<@{i[0]}>**: {i[1]}\n"
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Most Thanked Members",
                description=text,
                color=disnake.Color.orange(),
            )
        )
