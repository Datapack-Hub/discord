import discord


message_commands = """
- `Quick Look`: Opens a ZIP or text file inside Discord.
- `Redirect to help channel`: Sends a message telling the user to use a help channel.
- `Report Message`: Reports a message to the moderation team.
- `Remind them to resolve thread`\*: Sends a reminder message to the thread author, asking them to resolve the thread.
"""

slash_commands = """
- `/help`: Shows you this message.
- `/resolve`\*: Resolves the help channel.
- `/top`: Jumps to the top of any channel.
- `/stats`: View basic stats about the help channels
"""

slash_commands_staff = """
- `/mod user <user>` - Opens the moderation panel for a user
- `/mod purge <limit> [user]` - Mass deletes messages, optionally filtering by user
- `/mod lockdown` and `/mod unlockdown` - Un/locks all server channels

- `/question reset` - Reset the original "header" message in the thread
- `/question setup` - Re-send the original "header" message, if it didn't send originally.
` `/question summon-helpers` - Manually summon the helpers to the channel.

- `/stats-admin stats` - Regenerate all stats data (can take up to 15m)
- `/stats-admin update` - Add any missed questions to the stats cache (debug)

- `/uwu user <user>` and `/uwu channel` - Turns on the uwufier for a specific user or channel
- `/uwu ban <user>` - Toggle uwufier ban for a specific user
- `/uwu override` - Globally disable/enable uwufier features

- `/susprail image` - Random suspension railway image
- `/susprail info`- Information about suspension railways

"""

features = """
- **Help Channels**: The bot organises help channels, closes them if they are inactive, pings helpers, and more.
- **Stats**: We use this bot to monitor stats in help channels - this will be available publicly soon!
- **Moderation**: Behind the scenes, the bot has loads of moderation features to help our staff team out.
- **Welcome System**: When a new member joins, the bot will give them the necessary roles, and send a welcome message.
- **Logging**: We have a custom-built logs system which this bot logs deleted/edited messages, members joining, and more.
- **Scam detection**: The **scamn't** bot is built into this discord bot, so most scam messages will be caught pretty quickly.
- **Fun**: There's loads of hidden easter eggs in the bot and secret staff-only fun commands!
"""

class HelpCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="help", description="View all commands")
    async def help(self, inter: discord.ApplicationContext):
        embed = discord.Embed(
            title="Datapack Hub Server Bot",
            description="This bot helps manage Datapack Hub server. Below is a list of all the features provided by the bot. *\* means the command only works in the help channels*",
            color=discord.Color.orange()
        )
        
        embed.add_field(name="Features",value=features,inline=False)
        embed.add_field(name="Commands",value=slash_commands,inline=False)
        embed.add_field(name="Message Commands",value=message_commands,inline=False)
        embed.add_field(name="Datapack Helper",value="My fellow bot <@1108074519308017734> provides loads of other useful commands helping people create datapacks. Check out that bot's help command for more info.",inline=False)
        
        await inter.response.send_message(embed=embed)
        
    @discord.slash_command(name="help-staff",description="Show help commands including staff-only commands")
    async def help_staff(self, inter: discord.ApplicationContext):
        embed = discord.Embed(
            title="Staff Commands",
            description=slash_commands_staff,
            color=discord.Color.orange()
        )
        
        await inter.response.send_message(embed=embed)