import discord
from discord.ext import commands


class MembersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="members", description="View member list and count")
    async def members(self, inter: discord.ApplicationContext):
        
        with open("member_names.txt","w+") as file:
            file.writelines([member.name + "\n" for member in inter.guild.members])
        
        dc_file = discord.File("member_names.txt")
        await inter.response.send_message(f"`{inter.guild.member_count}` members",file=dc_file,ephemeral=True)