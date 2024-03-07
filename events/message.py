import disnake
from disnake.ext import commands
import variables
import re
from events.highlighter.highlighter import Hl

def replace_code_blocks(message):
    pattern = re.compile(r'```mcf(?:unction)?\n([\s\S]+?)```', re.DOTALL)

    def replace_function(match):
        code_block_content = match.group(1).strip()
        return f'```ansi\n{Hl.highlight(code_block_content)}\n```'

    edited_message = pattern.sub(replace_function, message)

    return edited_message

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
            message.add_reaction("👋")
        if re.findall(r'```mcf(?:unction)?\n([\s\S]+?)```',message.content) and not message.author.bot:
            if message.channel.type == disnake.ChannelType.public_thread:
                hooks = await message.channel.parent.webhooks()
                
                for hook in hooks:
                    if hook.name == "DPH":
                        break
                else:
                    hook = await message.channel.parent.create_webhook(name="DPH")
                
                await message.delete()
                await hook.send(replace_code_blocks(message.content),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,thread=message.channel,allowed_mentions=disnake.AllowedMentions.none())
            else:
                hooks = await message.channel.webhooks()
                
                for hook in hooks:
                    if hook.name == "DPH":
                        break
                else:
                    hook = await message.channel.create_webhook(name="DPH")
                
                await message.delete()
                await hook.send(replace_code_blocks(message.content),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none())
