import discord
import json
import variables
import asyncio
import utils.log as Log
from modules.help_channels.res_thread import resolve_thread_without_interaction
from modules.help_channels.components.views import HelpChannelMessageView, ReopenedThreadView

def get_opened_threads(thread: discord.Thread) -> list[discord.Thread]:
    parent = thread.parent
    if parent is None: return []

    # Find other open threads by the same owner (excluding the current one)
    return [
        t for t in parent.threads if (
            t.owner_id == thread.owner_id
            and not t.archived
            and thread.parent is not None
            and not any(tag.name.lower() == "resolved" for tag in t.applied_tags)
            and t.id != thread.id
        )
    ]
            
class HelpChannelListeners(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(HelpChannelMessageView())

    @discord.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        await asyncio.sleep(1)
        if thread.parent_id in variables.help_channels and not thread.name.startswith("!n"):
            # Pin first message
            try:
                messages = await thread.history(oldest_first=True, limit=1).flatten()
                await messages[0].pin()
            except Exception as e:
                Log.warn("Could not pin the starting message to the help thread: " + " ".join(e.args))

            # Send message
            msg = await thread.send(
                f"-# (thread created) <@&{variables.comm_helper_C!s}>",
                allowed_mentions=discord.AllowedMentions(roles=True)
            )
            await msg.delete()
            await thread.send(view=HelpChannelMessageView(created_at=discord.utils.utcnow(), threads=get_opened_threads(thread)))
    
    @discord.Cog.listener()
    async def on_raw_thread_update(self, payload: discord.RawThreadUpdateEvent):
        thread = payload.thread
        
        if (
            thread.archived == True 
            and not (any(tag.name.lower() == "resolved" for tag in thread.applied_tags)) 
            and thread.parent.id in variables.help_channels
        ):
            await resolve_thread_without_interaction(thread=thread)
            
        elif (
            thread.archived == False 
            and (any(tag.name.lower() == "resolved" for tag in thread.applied_tags)) 
            and thread.parent.id in variables.help_channels
        ):
            tags = [tag for tag in thread.applied_tags if not (tag.name.lower() == "resolved")]
            await thread.edit(applied_tags=tags)
            await thread.last_message.reply(view=ReopenedThreadView(), allowed_mentions=discord.AllowedMentions.none())
            
            if thread.parent.id == variables.help_channels[0]:
                # Remove from stats
                with open("data/questions.json","r") as fp:
                    qns = json.load(fp)
                    
                new_qns = [t for t in qns if t["id"] != thread.id]
                
                with open("data/questions.json","w") as fp:
                    json.dump(new_qns,fp)
            