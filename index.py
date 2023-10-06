import disnake
from disnake.ext import commands, tasks
from bottoken import TOKEN

bot = commands.Bot(command_prefix="nerds", activity=disnake.Activity(name="the game of life",details="The best datapacking server", url="https://datapackhub.net",type=disnake.ActivityType.competing, state="i am death, destroyer of worlds", buttons=["Website"]), test_guilds=[911644509249613864,1144269849414074418])

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

bot.run(TOKEN)