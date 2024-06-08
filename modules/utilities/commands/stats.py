import disnake
from disnake.ext import commands


class StatsCommand(commands.Cog, name="stats"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="stats", description="View some server stats")
    async def stats(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()

        dp_questions = len(inter.guild.get_channel(1051225367807000706).threads)
        archived_dps = (
            await inter.guild.get_channel(1051225367807000706)
            .archived_threads(limit=None)
            .flatten()
        )
        dp_questions = dp_questions + len(archived_dps)
        rp_questions = len(inter.guild.get_channel(1051227454980755546).threads)
        archived_rps = (
            await inter.guild.get_channel(1051227454980755546)
            .archived_threads(limit=None)
            .flatten()
        )
        rp_questions = rp_questions + len(archived_rps)

        embed = (
            disnake.Embed(
                colour=disnake.Colour.orange(),
                title="Datapack Hub Stats",
                description="These stats are the up-to-date question counts as of right now. There may be a minor inaccuracy due to discord API limitations.",
            )
            .add_field("Datapack Questions", dp_questions, inline=True)
            .add_field("Resourcepack Questions", rp_questions, inline=True)
        )
        await inter.edit_original_message(embed=embed)
