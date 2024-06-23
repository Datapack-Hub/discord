import disnake
from disnake.ext import commands
import variables
import datetime
import utils.log as Log


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


class ResolveCommand(commands.Cog, name="resolve"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(title="resolve", description="Marks question as resolved")
    async def resolve(self, inter: disnake.ApplicationCommandInteraction):
        role = inter.guild.get_role(variables.helper)
        
        # Try and get parent channel
        try:
            channel = inter.channel.parent.id
        except:
            await inter.response.send_message("Invalid",ephemeral=True)
            return False
        
        if (inter.channel.owner_id == inter.author.id) or (role in inter.author.roles) and channel in variables.help_channels:
            # Add Resolved tag
            resolved_tag = inter.channel.parent.get_tag_by_name("RESOLVED")
            await inter.channel.add_tags(resolved_tag)

            # Feedback
            messages = await inter.channel.history(oldest_first=True, limit=1).flatten()

            # Build embed
            emb = disnake.Embed(
                title="Question Closed",
                description=f"Your question, <#{inter.channel.id}> ({inter.channel.name}), was resolved!",
                colour=disnake.Colour.green()
            ).add_field("Original Message", messages[0].jump_url, inline=False).add_field("Duration open",format_duration_between(messages[0].created_at, datetime.datetime.now(messages[0].created_at.tzinfo)))
            
            # Send message
            try:
                await inter.response.send_message(
                    embed=emb,
                    components=[
                        disnake.ui.ActionRow()
                        .add_button(label="Jump to top", url=messages[0].jump_url)
                        .add_button(label="Review Datapack Hub", url="https://disboard.org/review/create/935560260725379143")
                    ]
                )
            except Exception as e:
                Log.error(f"Could not send the finishing message in #{inter.channel.name}: {e}")

            # Mark as closed
            await inter.channel.edit(archived=True)
            
            Log.info(f"{inter.author.name} resolved the thread #{inter.channel.name}")
        
        else:
            await inter.response.send_message("You aren't allowed to do this here.", ephemeral=True)
            Log.info(f"{inter.author.name} tried to resolve a thread which wasn't theirs")
