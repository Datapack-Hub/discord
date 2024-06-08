import disnake
from disnake.ext import commands
import variables
from utils.uwufier import Uwuifier
import re
import automod
import json


class ModerationListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # * CENSOR
        if any(ext in message.content.lower() for ext in automod.terms) and not message.author.bot:
            if message.channel.type != disnake.ChannelType.public_thread and message.channel.type != disnake.ChannelType.private_thread:
                hooks = await message.channel.webhooks()
                for hook in hooks:
                    if hook.name == "DPH":
                        break
                else:
                    hook = await message.channel.create_webhook(name="DPH")
            else:
                hooks = await message.channel.parent.webhooks()
                
                for hook in hooks:
                    if hook.name == "DPH":
                        break
                else:
                    hook = await message.channel.parent.create_webhook(name="DPH")

            # Keep attachments
            files = []
            for attachment in message.attachments:
                file = await attachment.to_file()
                files.append(file)

            # Delete message
            await message.delete()
            
            # Start modification
            text = message.content
            
            # Uwufy if jeferwalg
            if message.author.id in [711944262173982822, 543741360478355456]:
                uwu = Uwuifier()
                text = uwu.uwuify_sentence(text)
            
            # Create filter
            censored = text
            search_string = ""
            for term in automod.terms:
                search_string += f"({term})|"
            search_string = search_string[:-1]
            pattern = re.compile(search_string,re.IGNORECASE)
            
            # Censor
            censored = pattern.sub("<:r1:1100839366005358692><:r2:1100839228792901752><:r3:1100839175361671309>",text)
            
            # Resend
            if message.channel.type != disnake.ChannelType.public_thread and message.channel.type != disnake.ChannelType.private_thread:
                await hook.send(censored,wait=False,files=files,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none())
            else:
                await hook.send(censored,wait=False,files=files,username=message.author.display_name,avatar_url=message.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none(),thread=message.channel)
            
            # Timeout
            data = json.load(open("mute_lengths.json","r"))
            try:
                data[str(message.author.id)]
            except KeyError:
                data[str(message.author.id)] = 1
                seconds = 1
            else:
                data[str(message.author.id)] += 0.4
                seconds = data[str(message.author.id)]
                
            json.dump(data,open("mute_lengths.json","w"))
            
            try:
                await message.author.timeout(duration=seconds,reason="Censor Timeout")
            except disnake.errors.Forbidden:
                pass
            
            # Log
            await self.bot.get_channel(variables.automodlogs).send(embed=disnake.Embed(
                title="Message Censored",
                colour=disnake.Colour.orange()
            ).add_field("Content",f"{message.content}",inline=False).add_field("Channel",message.channel.jump_url,inline=False).add_field("Attachments",f"{message.attachments.__len__()!s} attachments",inline=False).set_author(name=message.author.global_name,icon_url=message.author.avatar.url))