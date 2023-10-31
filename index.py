import disnake
from disnake.ext import commands, tasks
from bottoken import TOKEN
import variables
import time

intents = disnake.Intents.all()

bot = commands.Bot(command_prefix="nerds", activity=disnake.Activity(name="the game of life",details="The best datapacking server", url="https://datapackhub.net",type=disnake.ActivityType.competing, state="i am death, destroyer of worlds", buttons=["Website"]), test_guilds=[variables.guild],intents=disnake.Intents.all())

# Events
from events.thread_create import OnThreadCreate
from events.button_click import OnButtonClick
from events.message import OnMessage

from events.on_member_join import OnMemberJoin
bot.add_cog(OnThreadCreate(bot))
bot.add_cog(OnButtonClick(bot))
bot.add_cog(OnMemberJoin(bot))
bot.add_cog(OnMessage(bot))

# Slash Commands
from commands.resolve import ResolveCommand
bot.add_cog(ResolveCommand(bot))
from commands.stats import StatsCommand
bot.add_cog(StatsCommand(bot))
from commands.thank import ThankCommand
bot.add_cog(ThankCommand(bot))
from commands.top import TopCommand
bot.add_cog(TopCommand(bot))

# Message Commands
from commands.redirect import RedirectCommand
bot.add_cog(RedirectCommand(bot))

# Loops
@tasks.loop(minutes=10)
async def ten():
    print("Starting query")
    channel_resolved = bot.get_channel(variables.stats)
    channel_asked = bot.get_channel(variables.stats_asked)
    total_threads = 0
    resolved_threads = 0
    for i in variables.help_channels:
        questions = bot.get_channel(i).threads.__len__()
        archived_qns = await bot.get_channel(i).archived_threads(limit=None).flatten()
        for thread in bot.get_channel(i).threads:
            total_threads += 1
            resolved_tag = thread.parent.get_tag_by_name("RESOLVED")
            if resolved_tag in thread.applied_tags:
                    resolved_threads += 1
        questions = questions + archived_qns.__len__()

        for thread in archived_qns:
            
            creation_unix = time.mktime(thread.create_timestamp.timetuple())
            parent_channel = thread.parent
            resolved_tag = parent_channel.get_tag_by_name("RESOLVED")
            if creation_unix >= 1674615000:
                total_threads += 1
                if resolved_tag in thread.applied_tags:
                    resolved_threads += 1

    await channel_resolved.edit(name=f"Questions Resolved: {resolved_threads}")
    await channel_asked.edit(name=f"Questions Asked: {total_threads}")
    print(f"Finshed {resolved_threads}/{total_threads}")
    
@bot.event
async def on_ready():
    await ten.start()
    
bot.run(TOKEN)

# oldest resolved thread timestamp 1674615000