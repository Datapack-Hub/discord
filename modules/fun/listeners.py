import discord

import variables
from utils.uwufier import Uwuifier
import json
import utils.log as Log
import os
from .commands.uwu import uwu_data

class FunListeners(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            uwu_data["enabled"] and 
            message.channel.type == discord.ChannelType.text and 
            not message.author.bot and 
            not message.author.id in uwu_data["banned"]
        ):
            if variables.uwu_trigger in message.content.lower():
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
                try: await hook.send(uwu.uwuify_sentence(message.content.lower()),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=discord.AllowedMentions.none())
                except Exception as e: Log.error(f"Could not uwufy message from {message.author.name}: {e}")
                
            elif (
                (message.author.id in uwu_data["users"]) or 
                (message.channel.id in uwu_data["channels"])
            ):
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
                await hook.send(uwu.uwuify_sentence(message.content.lower()),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=discord.AllowedMentions.none())
            
            elif message.author.id in uwu_data["nexts"]:
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
                await hook.send(uwu.uwuify_sentence(message.content.lower()),wait=False,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=discord.AllowedMentions.none())

                # Remove from nexts
                uwu_data["nexts"].remove(message.author.id)