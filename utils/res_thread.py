import discord
import utils.log as Log
from utils.stats import update
import datetime

async def resolve_thread(thread: discord.Thread, response: discord.InteractionResponse):
    if len(thread.applied_tags) == 5:
        return await response.send_message("This post has 5 tags, which is the maximum. **Please remove one tag** and then try again.")

    if thread.archived: await thread.edit(archived=False)
    
    resolved_tag = next(t for t in thread.parent.available_tags if t.name.lower() == "resolved")
    tags = thread.applied_tags
    tags.append(resolved_tag)
    await response.send_message("Done",ephemeral=True)
    
    from modules.help_channels.components.views import ResolvedThreadView
    
    msg = await thread.send(
        view=ResolvedThreadView(thread=thread)
    )

    # Archive channel
    await thread.edit(archived=True, applied_tags=tags)
    
async def resolve_thread_without_interaction(thread: discord.Thread):
    if len(thread.applied_tags) == 5:
        return await thread.send_message("This post has 5 tags, which is the maximum. **Please remove one tag** and then try again.")

    # if thread.archived: await thread.edit(archived=False)
    
    resolved_tag = next(t for t in thread.parent.available_tags if t.name.lower() == "resolved")
    tags = thread.applied_tags
    tags.append(resolved_tag)
    
    from modules.help_channels.components.views import ResolvedThreadView
    
    msg = await thread.send(
        view=ResolvedThreadView(thread=thread)
    )

    # Archive channel
    await thread.edit(archived=True, applied_tags=tags)