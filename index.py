import utils.log as Log
import discord
from discord.ext import tasks
from bottoken import TOKEN
import variables
import time



# Setup bot
bot = discord.Bot(
    test_guilds=[variables.guild],
    intents=discord.Intents.all(),
)

# Logs
from modules.logs.listeners import LogsListeners
bot.add_cog(LogsListeners(bot))

# Moderation
from modules.moderation.listeners import ModerationListeners
bot.add_cog(ModerationListeners(bot))
from modules.moderation.commands.mod import ModCommand
bot.add_cog(ModCommand(bot))
from modules.moderation.message_commands.moderate import ModerateCommand
bot.add_cog(ModerateCommand(bot))

# Help Channels
from modules.help_channels.listeners import HelpChannelListeners
bot.add_cog(HelpChannelListeners(bot))
from modules.help_channels.commands.resolve import ResolveCommand
bot.add_cog(ResolveCommand(bot))
from modules.help_channels.commands.question import QuestionCommand
bot.add_cog(QuestionCommand(bot))
from modules.help_channels.commands.top import TopCommand
bot.add_cog(TopCommand(bot))
from modules.help_channels.message_commands.redirect import RedirectCommand
bot.add_cog(RedirectCommand(bot))
from modules.help_channels.message_commands.remind import RemindCommand
bot.add_cog(RemindCommand(bot))

# Utilities
from modules.utilities.commands.members import MembersCommand
bot.add_cog(MembersCommand(bot))
from modules.utilities.commands.help import HelpCommand
bot.add_cog(HelpCommand(bot))
from modules.utilities.commands.icon import IconCommand
bot.add_cog(IconCommand(bot))
from modules.utilities.message_commands.view import ViewFileCommand
bot.add_cog(ViewFileCommand(bot))

# Fun
from modules.fun.listeners import FunListeners
bot.add_cog(FunListeners(bot))
from modules.fun.commands.suspension import SuspensionRailwayCommand
bot.add_cog(SuspensionRailwayCommand(bot))
from modules.fun.commands.uwu import UwuCommand
bot.add_cog(UwuCommand(bot))

# Welcome
from modules.welcome.listeners import WelcomeListeners
bot.add_cog(WelcomeListeners(bot))

# Stats
from modules.stats.commands.stats import StatsCommand
bot.add_cog(StatsCommand(bot))
from modules.stats.commands.stats_admin import StatsAdminCommand
bot.add_cog(StatsAdminCommand(bot))


# QOTD
# from modules.qotd.schedule import schedule_qotd

# Loops
@tasks.loop(minutes=10)
async def ten():
    channel_asked: discord.VoiceChannel = bot.get_channel(variables.stats_asked)
    total_threads = 0
    for i in variables.help_channels:
        channel: discord.ForumChannel = bot.get_channel(i)
        questions = len(channel.threads)
        archived_qns = await channel.archived_threads(limit=None).flatten()
        for _ in channel.threads:
            total_threads += 1
        questions = questions + len(archived_qns)

        for thread in archived_qns:
            creation_unix = time.mktime(thread.create_timestamp.timetuple())
            if creation_unix >= 1674615000:
                total_threads += 1

    await channel_asked.edit(name=f"Questions Asked: {total_threads}")

from modules.help_channels import loops

@bot.event
async def on_ready():
    Log.info("Bot has started!")
    
    await loops.autoclose_loop.start(bot=bot)

# Run bot
bot.run(TOKEN)
