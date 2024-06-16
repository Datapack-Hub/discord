import json
from utils.uwufier import Uwuifier
import utils.log as Log
import disnake
from disnake.ext import commands

uwu_data = {"users": [], "channels": [], "banned": []}

class UwuCommand(commands.Cog, name="uwu"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="uwu")
    async def uwu(self, inter: disnake.ApplicationCommandInteraction):
        return
    
    @uwu.sub_command("message","Send an uwufied message")
    async def message(self, inter: disnake.ApplicationCommandInteraction, text: str):
        hooks = await inter.channel.webhooks()

        for hook in hooks:
            if hook.name == "DPH":
                break
        else:
            hook = await inter.channel.create_webhook(name="DPH")
        uwu = Uwuifier()
        await hook.send(uwu.uwuify_sentence(text.lower()),wait=False,username=inter.author.display_name,avatar_url=inter.author.display_avatar.url,allowed_mentions=disnake.AllowedMentions.none())
        await inter.response.send_message("yes done",ephemeral=True)
        Log.info(f"Uwufied a message from {inter.author.name} in #{inter.channel.name}")
    
    @uwu.sub_command("auto","Enable the auto uwufier")
    async def auto(self, inter: disnake.ApplicationCommandInteraction):
        try:
            users = uwu_data["users"]
            if inter.author.id in users:
                users.remove(inter.author.id)
                await inter.response.send_message("**Disabled** auto uwufier for user " + inter.author.mention, allowed_mentions=disnake.AllowedMentions.none())
                Log.info(f"Disabled the user uwufier for {inter.author.name}")
            else:
                users.append(inter.author.id)
                await inter.response.send_message("**Enabled** auto uwufier for user " + inter.author.mention, allowed_mentions=disnake.AllowedMentions.none())
                Log.info(f"Enabled the user uwufier for {inter.author.name}")
            uwu_data["users"] = users
        except Exception as e:
            Log.error(f"Could not toggle uwufier for user {inter.author.name}: {e}")
    
    @uwu.sub_command("channel","Enable the auto uwufier for the current channel")
    async def channel(self, inter: disnake.ApplicationCommandInteraction):
        try:
            if inter.channel.id in uwu_data["channels"]:
                uwu_data["channels"].remove(inter.channel.id)
                await inter.response.send_message("**Disabled** auto uwufier for channel " + inter.channel.mention)
                Log.info(f"Disabled the uwufier for #{inter.channel.name}")
            else:
                uwu_data["channels"].append(inter.channel.id)
                await inter.response.send_message("**Enabled** auto uwufier for channel " + inter.channel.mention)
                Log.info(f"Enabled the uwufier for #{inter.channel.name}")
        except Exception as e:
            Log.error(f"Could not toggle uwufier for channel #{inter.channel.name}: {e}")
            
    @uwu.sub_command("ban","Ban a user from using the uwu features")
    async def ban(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member):
        try:
            if user.id in uwu_data["banned"]:
                uwu_data["banned"].remove(user.id)
                await inter.response.send_message(f"**Unbanned** user {user.mention} from the uwufier.", allowed_mentions=disnake.AllowedMentions.none())
                Log.info(f"Unbanned {user.name} from the uwufier.")
            else:
                uwu_data["banned"].append(user.id)
                await inter.response.send_message(f"**Banned** user {user.mention} from the uwufier.", allowed_mentions=disnake.AllowedMentions.none())
                Log.info(f"Banned {user.name} from the uwufier.")
        except Exception as e:
            Log.error(f"Could not toggle uwufier for channel #{user.name}: {e}")
        
    @uwu.sub_command("user","Enable the auto uwufier for another user")
    async def auto(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member):
        try:
            users = uwu_data["users"]
            if user.id in users:
                users.remove(user.id)
                await inter.response.send_message("**Disabled** auto uwufier for user " + user.mention)
                Log.info(f"Disabled the user uwufier for {user.name}")
            else:
                users.append(user.id)
                await inter.response.send_message("**Enabled** auto uwufier for user " + user.mention)
                Log.info(f"Enabled the user uwufier for {user.name}")
            uwu_data["users"] = users
        except Exception as e:
            Log.error(f"Could not toggle uwufier for user {user.name}: {e}")