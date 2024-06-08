import disnake
from disnake.ext import commands
import variables
from uwufier import Uwuifier


class FunListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
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