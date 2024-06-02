import disnake
from disnake.ext import commands
import variables
import re
from uwufier import Uwuifier

class OnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if (
            type(message.channel) is disnake.Thread
            and message.channel.parent.id in variables.help_channels
            and message.channel.parent.get_tag_by_name("RESOLVED")
            in message.channel.applied_tags
            and not (message.author.id == self.bot.user.id)
        ):
            await message.channel.remove_tags(
                message.channel.parent.get_tag_by_name("RESOLVED")
            )
            await message.reply(
                "**Re-opened the channel.** Make sure to close it again once you're done.",
                components=[
                    disnake.ui.Button(
                        label="Close Question", custom_id="resolve_question_button"
                    )
                ],
            )
        if message.channel.id == variables.intro:
            await message.add_reaction("👋")
            
        if variables.uwu_trigger in message.content.lower() and not message.author.bot:
            hooks = await message.channel.webhooks()

            for hook in hooks:
                if hook.name == "DPH":
                    break
            else:
                hook = await message.channel.create_webhook(name="DPH")

            await message.delete()
            
            uwu = Uwuifier()
            
            await hook.send(uwu.uwuify_sentence(message.content.lower()),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none())
