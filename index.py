import disnake
from disnake.ext import commands, tasks
from bottoken import TOKEN
import variables

intents = disnake.Intents.all()

bot = commands.Bot(activity=disnake.Activity(name="the game of life",details="The best datapacking server", url="https://datapackhub.net",type=disnake.ActivityType.competing, state="i am death, destroyer of worlds", buttons=["Website"]), test_guilds=[911644509249613864,1144269849414074418,1144269849414074418], intents=intents)

# Events
from events.thread_create import OnThreadCreate
from events.button_click import OnButtonClick
bot.add_cog(OnThreadCreate(bot))
bot.add_cog(OnButtonClick(bot))

# Slash Commands
from commands.resolve import ResolveCommand
bot.add_cog(ResolveCommand(bot))
from commands.stats import StatsCommand
bot.add_cog(StatsCommand(bot))

# Message Commands
from commands.redirect import RedirectCommand
bot.add_cog(RedirectCommand(bot))

# Loops
@tasks.loop(minutes=10)
async def ten():
    print("Starting query")
    channel = bot.get_channel(variables.stats)
    total = 0
    
    for i in variables.help_channels:
        questions = bot.get_channel(i).threads.__len__()
        archived_qns = await bot.get_channel(i).archived_threads(limit=None).flatten()
        questions = questions + archived_qns.__len__()
        resolved_threads = 0
        resolved_tag = bot.get_channel(i).threads[0].parent.get_tag_by_name("RESOLVED")

        for thread in archived_qns:
            parent_channel = thread.parent
            resolved_tag = parent_channel.get_tag_by_name("RESOLVED")
            
            if resolved_tag in thread.applied_tags:
                resolved_threads += 1
                print(thread.name)

        total = total + questions

    await channel.edit(name=f"Resolved Questions: {resolved_threads}/{total}")
    print(f"Finshed {resolved_threads}")
    
@bot.event
async def on_ready():
    await ten.start()

bot.run(TOKEN)