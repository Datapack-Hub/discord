import disnake
from disnake.ext import commands
import variables
from utils.uwufier import Uwuifier
import json
import utils.log as Log
import os

class FunListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        Log.debug(os.getcwd())
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
            try: await hook.send(uwu.uwuify_sentence(message.content.lower()),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none())
            except Exception as e: Log.error(f"Could not uwufy message from {message.author.name}: {e}")
        with open("uwufied.json","r") as fp:
            data = json.load(fp)
            if ((message.author.id in data["users"]) or (message.channel.id in data["channels"])) and message.channel.type == disnake.ChannelType.text and not message.author.bot:
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