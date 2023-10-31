import disnake
from disnake.ext import commands
import variables
import json

class ThankCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.user_command(name="Award Helper Points")
    async def award(self, inter: disnake.MessageCommandInteraction):
        if inter.user.get_role(variables.helper):
            with open("/root/dph_bot/discord/points.json", "r+") as fp:
                fp.seek(0)
                data = json.loads(fp.read())
                if str(inter.target.id) in data:
                    data[str(inter.target.id)] += 1
                else:
                    data[str(inter.target.id)] = 1
                fp.seek(0)
                fp.write(json.dumps(data))
                fp.close()
            await inter.response.send_message(f"Awarded one help point to {inter.target.mention}!",ephemeral=True)
        else:
            await inter.response.send_message("Only Official Helpers and Staff can run this comamnd!",ephemeral=True)