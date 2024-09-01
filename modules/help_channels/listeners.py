import disnake
from disnake.ext import commands
import variables
import asyncio
import utils.log as Log
from datetime import datetime, timedelta
from utils.update import remove


class HelpChannelListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: disnake.Thread):
        await asyncio.sleep(1)
        if thread.parent_id in variables.help_channels:
            ts30 = datetime.now() + timedelta(minutes=30)
            
            embed = disnake.Embed(
                colour=disnake.Colour.orange(),
                title=("Someone will come and help soon!"),
                description=(
                    f"💬 While you wait, take this time to provide more context and details.\n\n🙇 If nobody has answered you by <t:{int(ts30.timestamp())}:t>, feel free to use the `Summon Helpers` button to ping our helper team.\n\n✅ Once your question has been resolved (or you no longer need it), please click Resolve Question or run `/resolve`"
                ),
            )
            summon_helpers_button = disnake.ui.Button(label="Summon Helpers",custom_id="summon_helpers_button",style=disnake.ButtonStyle.blurple,emoji="🙇",)
            resolve_question_button = disnake.ui.Button(label="Resolve Question",custom_id="resolve_question_button",style=disnake.ButtonStyle.green,emoji="✅",)
            
            # Pin first message
            try:
                messages = await thread.history(oldest_first=True, limit=1).flatten()
                await messages[0].pin()
            except Exception as e:
                Log.warn("Could not pin the starting message to the help thread: " + " ".join(e.args))

            # Send message
            try:
                await thread.send(
                    f"<@&{variables.comm_helper_C!s}>",
                    embed=embed,
                    components=[
                        summon_helpers_button,
                        resolve_question_button,
                    ],
                    allowed_mentions=disnake.AllowedMentions(roles=True),
                )
            except Exception as e:
                Log.error("Could not send the opening help channel message: " + " ".join(e.args))

            # Find other questions
            parent = thread.parent
            if parent is None: return
            
            for t in parent.threads:
                if (
                    t.owner_id == thread.owner_id
                    and not t.archived
                    and thread.parent is not None
                    and thread.parent.get_tag_by_name("RESOLVED") not in t.applied_tags
                    and not t.id == thread.id
                ):
                    await thread.send(
                        embed=disnake.Embed(
                            title="⚠️ You already have a question open!",
                            description=f"Don't forget to close or resolve your old questions once you're done with them. It makes our lives much easier! :D\n\n**Open question**: <#{t.id}>",
                            colour=disnake.Colour.red(),
                        )
                    )
    
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if (
            type(message.channel) is disnake.Thread
            and message.channel.parent.id in variables.help_channels
            and message.channel.parent.get_tag_by_name("RESOLVED")
            in message.channel.applied_tags
            and not (message.author.id == self.bot.user.id)
        ):
            try: await message.channel.remove_tags(message.channel.parent.get_tag_by_name("RESOLVED"))
            except Exception as e: Log.warn("Could not remove the Resolved tag: " + " ".join(e.args))
            
            await message.reply(
                "**Re-opened the channel.** Make sure to close it again once you're done.",
                components=[
                    disnake.ui.Button(
                        label="Close Question", custom_id="resolve_question_button"
                    )
                ],
            )
            
            Log.info("Re-opened the help thread #" + message.channel.name)
            
            await remove(message.channel.id)
