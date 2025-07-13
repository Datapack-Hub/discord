import discord
import variables
import utils.log as Log
from modules.help_channels.components.views import SummonedHelpersView, HelpChannelMessageView


def get_opened_threads(thread: discord.Thread) -> list[discord.Thread]:
    parent = thread.parent
    if parent is None: return []

    # Find other open threads by the same owner (excluding the current one)
    return [
        t for t in parent.threads if (
            t.owner_id == thread.owner_id
            and not t.archived
            and thread.parent is not None
            and not any(tag.name.lower() == "resolved" for tag in t.applied_tags)
            and t.id != thread.id
        )
    ]

class QuestionCommand(discord.Cog, name="question"):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
    question = discord.SlashCommandGroup(name="question")

    @question.command(name="summon-helpers", description="Manually summon helpers")
    async def summon(self, inter: discord.ApplicationContext):
        msg = await inter.respond(
            f"Summoning helpers... (<@&{variables.helper!s}> <@&{variables.comm_helper_B!s}>)",
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        await msg.delete_original_response() 
        await inter.channel.send(
            f"<@&{variables.helper!s}> <@&{variables.comm_helper_B!s}>",
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        await inter.channel.send(
            view=SummonedHelpersView()
        )
        Log.info(f"User {inter.author.name} summoned helpers with a slash command")

    @question.command(name="reset", description="Reset the original message and allow the user to summon helpers.")
    async def reset(self, inter: discord.ApplicationContext):
        async for msg in inter.channel.history(oldest_first=True, limit=10):
            if msg.author == self.bot.user and len(msg.components) != 0:
                await msg.edit(view=HelpChannelMessageView(threads=get_opened_threads(inter.channel)))
                await inter.respond("**This help channel has been reset.** The `Summon Helpers` button can now be used again.", ephemeral=True)
                break

    @question.command(name="setup", description="Send the initial message again, just in case something went wrong the first time.")
    async def reset(self, inter: discord.ApplicationContext):
        await inter.respond(view=HelpChannelMessageView(threads=get_opened_threads(inter.channel)))
