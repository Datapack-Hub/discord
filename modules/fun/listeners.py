import disnake
from disnake.ext import commands
import variables
from utils.uwufier import Uwuifier
import json


class FunListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if variables.uwu_trigger in message.content.lower() and not message.author.bot:
            # Create/get hook
            hooks = await message.channel.webhooks()
            for hook in hooks:
                if hook.name == "DPH":
                    break
            else:
                hook = await message.channel.create_webhook(name="DPH")

            # Delete message
            await message.delete()
            
            # The important bit
            uwu = Uwuifier()
            await hook.send(uwu.uwuify_sentence(message.content.lower()),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none())
        with open("uwufied.json","r") as fp:
            if message.author.id in json.load(fp) and message.channel.type == disnake.ChannelType.text:
                # Create/get hook
                hooks = await message.channel.webhooks()
                for hook in hooks:
                    if hook.name == "DPH":
                        break
                else:
                    hook = await message.channel.create_webhook(name="DPH")

                # Delete message
                await message.delete()
                
                # The important bit
                uwu = Uwuifier()
                await hook.send(uwu.uwuify_sentence(message.content.lower()),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none())
            fp.close()