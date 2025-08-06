import discord
import json
import variables

# Add to stats
async def register(thread: discord.Thread):
    def format_duration_between(date_time_start, date_time_end):
        time_difference = date_time_end - date_time_start

        # Calculate days, hours, and minutes
        days = time_difference.days
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        # Build the human-readable string
        formatted_duration = ""
        if days > 0:
            formatted_duration += f"{days}d"
        if hours > 0:
            formatted_duration += f"{hours}h"
        if minutes > 0:
            formatted_duration += f"{minutes}m"

        return formatted_duration if formatted_duration else "0m"
    
    messages = [msg async for msg in thread.history(limit=None, oldest_first=True) if not msg.author.bot]
    if len(messages) == 0:
        print("This thread has no messages. Skipping.")
        return None

    first_answer = next(
        (message for message in messages if not message.author.bot and message.author.id != thread.owner_id),
        messages[0]
    )

    this = {
        "name": thread.name,
        "id": thread.id,
        "tags": [tag.name for tag in thread.applied_tags],
        "first_answer": {
            "when": {
                "friendly": first_answer.created_at.strftime("%H:%M | %d/%m/%Y"),
                "timestamp": thread.created_at.timestamp()
            },
            "author": {
                "id": first_answer.author.id,
                "name": getattr(first_answer.author, "global_name", first_answer.author.name)
            }
        },
        "asker": {
            "id": thread.owner_id if thread.owner_id else 0,
            "name": thread.owner.name if thread.owner else "???"
        },
        "duration": {
            "friendly": format_duration_between(thread.created_at, thread.archive_timestamp),
            "seconds": abs((thread.created_at - thread.archive_timestamp).total_seconds()),
            "minutes": abs((thread.created_at - thread.archive_timestamp).total_seconds() / 60)
        },
        "created_at": {
            "friendly": thread.created_at.strftime("%H:%M | %d/%m/%Y"),
            "timestamp": thread.created_at.timestamp()
        },
        "archived_at": {
            "friendly": thread.archive_timestamp.strftime("%H:%M | %d/%m/%Y"),
            "timestamp": thread.archive_timestamp.timestamp()
        },
        "total_messages": len(messages)
    }
    
    with open("data/questions.json","r") as fp:
        qns = json.load(fp)
        qns.append(this)
        
    with open("data/questions.json","w") as fp:
        json.dump(qns, fp)

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
    
    # Register to stats
    if thread.parent.id == variables.help_channels[0]:
        await register(thread)

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
    
    # Register to stats
    if thread.parent.id == variables.help_channels[0]:
        await register(thread)

    # Archive channel
    await thread.edit(archived=True, applied_tags=tags)