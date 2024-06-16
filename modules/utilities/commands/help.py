import disnake
from disnake.ext import commands

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
"""

features = """
- **Help Channels**: The bot organises help channels, closes them if they are inactive, pings helpers, and more.
- **Moderation**: Behind the scenes, the bot has loads of moderation features to help our staff team out.
- **Welcome System**: When a new member joins, the bot will give them the necessary roles, and send a welcome message.
- **Logging**: We have a custom-built logs system which this bot logs deleted/edited messages, members joining, and more.
- **Fun**: There's loads of hidden easter eggs in the bot and secret staff-only fun commands!
"""

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description="View all commands")
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(title="Datapack Hub Server Bot",description="This bot helps manage Datapack Hub server. Below is a list of all the features provided by the bot. *\* means the command only works in the help channels*",color=disnake.Color.orange())
        
        embed.add_field("Features",features,inline=False)
        embed.add_field("Commands",slash_commands,inline=False)
        embed.add_field("Message Commands",message_commands,inline=False)
        embed.add_field("Datapack Helper","My fellow bot <@1108074519308017734> provides loads of other useful commands helping people create datapacks. Check out that bot's help command for more info.",inline=False)
        
        await inter.response.send_message(embed=embed)