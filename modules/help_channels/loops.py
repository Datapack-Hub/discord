from discord.ext import tasks
import discord
import variables
from datetime import timedelta
import utils.log as Log
from modules.help_channels.components.views import AutoclosedThreadView

@tasks.loop(hours=1)
async def autoclose_loop(bot: discord.Bot):
    for i in variables.help_channels:
        forum_channel: discord.ForumChannel = bot.get_channel(i)
        resolved_tag = next(t for t in forum_channel.available_tags if t.name.lower() == "resolved")
        
        for thread in [thread for thread in forum_channel.threads if not (resolved_tag in thread.applied_tags)]:
            last = await thread.history(limit=1).flatten()
            last = last[0]
            
            if last:
                diff = discord.utils.utcnow() - last.created_at
                if diff > timedelta(days=3):
                    try:
                        tags = thread.applied_tags
                        tags.append(resolved_tag)
                        await thread.edit(applied_tags=tags)
                    except Exception as e:
                        Log.error("Failed to autoclose thread: " + " ".join(e.args))
                    else:
                        resolved_tag = next(t for t in thread.parent.available_tags if t.name.lower() == "resolved")
                        tags = thread.applied_tags
                        tags.append(resolved_tag)
                        if len(tags) < 5:
                            await thread.send(view=AutoclosedThreadView(thread))
                            await thread.edit(archived=True, applied_tags=tags)
                            
                            Log.info(f"Automatically closed thread {thread.name} due to inactivity")