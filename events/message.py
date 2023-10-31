import disnake
from disnake.ext import commands
import variables
import regex as re
import json


class OnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if not message.channel.parent.id in variables.help_channels:
            print("Not right channel")
            return
        if not message.author.id == message.channel.owner_id:
            return
        c = message.content.lower()
        if not (c.startswith("thanks") or c.startswith("thank you") or c.startswith("thx") or c.startswith("ty") or c.startswith("tysm")):
            return
        
        mention = re.findall("<@([0-9]*)>",c)
        if not mention:
            await message.reply("If someone has helped you resolve your question, make sure to thank them by typing `thanks @user` 🤝")
        else:
            with open("/root/dph_bot/discord/points.json", "r+") as fp:
                fp.seek(0)
                data = json.loads(fp.read())
                if str(mention[0]) in data:
                    data[str(mention[0])] += 1
                else:
                    data[str(mention[0])] = 1
                fp.seek(0)
                fp.write(json.dumps(data))
                fp.close()
                
            await message.add_reaction("🤝")
            await message.reply(embed=disnake.Embed(
                title="Is your question done?",
                description=f"We're happy that <@{str(mention[0])}> helped you with your question!\n\nIf your question is now done, please don't forget to close the question with /resolve.",
                color=disnake.Color.dark_green()
            ),components=[disnake.ui.Button(style=disnake.ButtonStyle.green,label="Close Question",custom_id="resolve_question_button"),disnake.ui.Button(style=disnake.ButtonStyle.red,label="I'm not done yet!",custom_id="del_this_button")])