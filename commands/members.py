import disnake
from disnake.ext import commands


class MembersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="members", description="View member list and count")
    async def members(self, inter: disnake.ApplicationCommandInteraction):
        with open("Member Names.txt","w") as file:
            file.writelines([member.name for member in inter.guild.members])
            await inter.response.send_message(f"`{inter.guild.member_count}` members",file=disnake.File(file),ephemeral=True)
            file.close()