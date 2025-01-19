import disnake
import utils.log as Log
from utils.stats import update
import datetime

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

async def resolve_thread(thread: disnake.Thread, response: disnake.InteractionResponse, closer: disnake.User):
    if len(thread.applied_tags) == 5:
        await thread.response.send_message("This post has too many tags and the resolved tag cannot be applied. Please remove the least important one to properly resolve it.")
        return

    if thread.archived: await thread.edit(archived=False)
    
    try:
        resolved_tag = thread.parent.get_tag_by_name("Resolved")
        await thread.add_tags(resolved_tag)
    except Exception as e:
        Log.error("Could not add or find the resolved tag: " + " ".join(e.args))
        await thread.send("-# Error resolving this thread.")
    else:

        # Feedback
        messages = await thread.history(
            oldest_first=True, limit=1
        ).flatten()

        emb = disnake.Embed(
            title="Question Closed",
            description=f"Your question, <#{thread.id}> ({thread.name}), was resolved!",
            colour=disnake.Colour.green()
        ).add_field("Original Message", messages[0].jump_url, inline=False).add_field("Duration open",format_duration_between(messages[0].created_at,datetime.datetime.now(messages[0].created_at.tzinfo))).set_footer(text="Any further messages or reactions will re-open this thread.")
        

        await thread.send(
            embed=emb,
            components=[
                disnake.ui.ActionRow()
                .add_button(label="Jump to top", url=messages[0].jump_url)
                .add_button(
                    label="Review Datapack Hub",
                    url="https://disboard.org/review/create/935560260725379143",
                    style=disnake.ButtonStyle.gray,
                )
            ]
        )

        # Archive channel
        await thread.edit(archived=True)

        Log.info(f"{closer.name} closed a help channel using a button.")

        try:
            await update(thread)
        except Exception as e:
            Log.error("Could not log thread to stats data: " + ' '.join(e.args))