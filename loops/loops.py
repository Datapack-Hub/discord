from disnake.ext import commands, tasks
import variables


class loops(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @tasks.loop(minutes=10)
    async def ten(self):
        channel = self.bot.get_channel(variables.stats)

        dp_questions = len(channel.threads)
        archived_dps = await channel.archived_threads(limit=None).flatten()
        dp_questions = dp_questions + len(archived_dps)

        rp_questions = len(channel.threads)
        archived_rps = await channel.archived_threads(limit=None).flatten()
        rp_questions = rp_questions + len(archived_rps)

        total = rp_questions + dp_questions

        channel.edit(name=f"Questions Asked: {total}")
