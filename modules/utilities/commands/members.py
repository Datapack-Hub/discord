import disnake
from disnake.ext import commands


class MembersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="members", description="View member list and count")
    async def members(self, inter: disnake.ApplicationCommandInteraction):
        
        with open("member_names.txt","w+") as file:
            file.writelines([member.name + "\n" for member in inter.guild.members])
        
        dc_file = disnake.File("member_names.txt")
        await inter.response.send_message(f"`{inter.guild.member_count}` members",file=dc_file,ephemeral=True)