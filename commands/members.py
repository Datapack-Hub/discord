import disnake
from disnake.ext import commands


class MembersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="members", description="View member list and count")
    async def members(self, inter: disnake.ApplicationCommandInteraction):
        if inter.author.id == 880000911848636468:
            await inter.response.send_message("no flyne you do not deserve to use this command with your stinky private member list command",ephemeral=True)
        else:
            open("Member Names.txt","w").close()
            with open("Member Names.txt","w+") as file:
                file.writelines([member.name for member in inter.guild.members])
                file.close()
            
            file = open("Member Names.txt","r")
            await inter.response.send_message(f"`{inter.guild.member_count}` members",file=disnake.File(file),ephemeral=True)
            file.close()