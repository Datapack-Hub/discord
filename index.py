import disnake
from disnake.ext import commands, tasks
from bottoken import TOKEN
import variables
import time

# Events
from events.thread_create import OnThreadCreate
from events.button_click import OnButtonClick
from events.message import OnMessage

from events.on_member_join import OnMemberJoin

# Message Commands
from commands.redirect import RedirectCommand

# Slash Commands
from commands.resolve import ResolveCommand
from commands.stats import StatsCommand
from commands.view import ViewFileCommand

intents = disnake.Intents.all()

bot = commands.Bot(
    command_prefix="nerds",
    activity=disnake.Activity(
        name="the game of life",
        details="The best datapacking server",
        url="https://datapackhub.net",
        type=disnake.ActivityType.competing,
        state="i am death, destroyer of worlds",
        buttons=["Website"],
    ),
    test_guilds=[variables.guild],
    intents=disnake.Intents.all(),
)


bot.add_cog(OnThreadCreate(bot))
bot.add_cog(OnButtonClick(bot))
bot.add_cog(OnMemberJoin(bot))
bot.add_cog(OnMessage(bot))

bot.add_cog(ResolveCommand(bot))
bot.add_cog(StatsCommand(bot))
bot.add_cog(RedirectCommand(bot))
bot.add_cog(ViewFileCommand(bot))


# Loops
@tasks.loop(minutes=10)
async def ten():
    print("Starting query")
    channel_asked = bot.get_channel(variables.stats_asked)
    total_threads = 0
    for i in variables.help_channels:
        questions = bot.get_channel(i).threads.__len__()
        archived_qns = await bot.get_channel(i).archived_threads(limit=None).flatten()
        for thread in bot.get_channel(i).threads:
            total_threads += 1
        questions = questions + archived_qns.__len__()

        for thread in archived_qns:
            creation_unix = time.mktime(thread.create_timestamp.timetuple())
            if creation_unix >= 1674615000:
                total_threads += 1

    await channel_asked.edit(name=f"Questions Asked: {total_threads}")


@bot.event
async def on_ready():
    await ten.start()


bot.run(TOKEN)

# oldest resolved thread timestamp 1674615000
