import disnake
from disnake.ext import commands
import variables


class StatsCommand(commands.Cog, name="stats"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(title="stats", description="Marks question as resolved")
    async def stats(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message("Querying...")
        
        dp_questions = inter.guild.get_channel(1051225367807000706).threads.__len__()
        archived_dps = await inter.guild.get_channel(1051225367807000706).archived_threads(limit=None).flatten()
        dp_questions = dp_questions + archived_dps.__len__()
        rp_questions = inter.guild.get_channel(1051227454980755546).threads.__len__()
        archived_rps = await inter.guild.get_channel(1051227454980755546).archived_threads(limit=None).flatten()
        rp_questions = rp_questions + archived_rps.__len__()

        
        embed = disnake.Embed(
            color=disnake.Color.orange(),
            title="Datapack Hub Stats",
        ).add_field("Datapack Questions",dp_questions,inline=True).add_field("Resourcepack Questions",rp_questions,inline=True)
        await inter.edit_original_message(embed=embed)