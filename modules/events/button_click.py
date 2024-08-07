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


class OnButtonClick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "resolve_question_button":
            role = inter.guild.get_role(variables.helper)
            if (inter.channel.owner_id == inter.user.id) or (role in inter.user.roles):
                # Add tag
                resolved_tag = inter.channel.parent.get_tag_by_name("RESOLVED")
                await inter.channel.add_tags(resolved_tag)

                # Feedback
                messages = await inter.channel.history(
                    oldest_first=True, limit=1
                ).flatten()

                emb = (
                    disnake.Embed(
                        title="Question Closed",
                        description=f"Your question, <#{inter.channel.id}> ({inter.channel.name}), was resolved!",
                        colour=disnake.Colour.green(),
                    )
                    .add_field("Original Message", messages[0].jump_url, inline=False)
                    .add_field(
                        "Duration open",
                        format_duration_between(
                            messages[0].created_at,
                            datetime.datetime.now(messages[0].created_at.tzinfo),
                        ),
                    )
                )

                await inter.response.send_message(
                    embed=emb,
                    components=[
                        disnake.ui.ActionRow()
                        .add_button(label="Jump to top", url=messages[0].jump_url)
                        .add_button(
                            label="Review Datapack Hub",
                            url="https://disboard.org/review/create/935560260725379143",
                            style=disnake.ButtonStyle.gray,
                        ),
                    ],
                )

                # await inter.guild.get_member(inter.channel.owner_id).send(embed=emb,components=[
                #     disnake.ui.ActionRow().add_select(placeholder="Leave a rating:",options=[disnake.SelectOption(label="Great :D"),disnake.SelectOption(label="Good :)"),disnake.SelectOption(label="Meh :/"),disnake.SelectOption(label="Bad :("),disnake.SelectOption(label="Terrible >:(")]),
                #     disnake.ui.ActionRow().add_button(label="Jump to thread",url=inter.channel.jump_url).add_button(label="Review Datapack Hub",url="https://disboard.org/review/create/935560260725379143",style=disnake.ButtonStyle.gray)
                # ])

                # Archive channel
                await inter.channel.edit(archived=True)

                Log.info(f"{inter.author.name} closed a help channel using a button.")
            else:
                await inter.response.send_message(
                    embed=disnake.Embed(
                        colour=disnake.Colour.red(),
                        title="❌ Resolve Help Channel",
                        description="You can't do this since you are neither a helper nor the owner of this channel!",
                    ),
                    ephemeral=True,
                )
                
                Log.info(f"{inter.author.name} tried to close a help thread, but did not have permissions.")

        if inter.component.custom_id == "summon_helpers_button":
            # Get time
            creation_time = inter.channel.create_timestamp
            current_time = datetime.datetime.now(creation_time.tzinfo)
            time_difference = current_time - creation_time
            time_difference_seconds = time_difference.total_seconds()
            time_difference_minutes = time_difference_seconds / 60

            # Get helper role
            role = inter.guild.get_role(variables.helper)
            channel = inter.channel.parent.id
            if (inter.channel.owner_id == inter.author.id) or (
                role in inter.author.roles
            ):
                if time_difference_minutes >= 30 or role in inter.author.roles:
                    await inter.response.send_message(
                        f"<@&{variables.helper!s}> <@&{variables.comm_helper_B!s}>",
                        embed=disnake.Embed(
                            colour=disnake.Colour.blue(),
                            title=("🙇 Helpers Arise!"),
                            description=(
                                "Please note that you still might not immediately get a response since all helpers are human beings and volunteers (and also might be sleeping right now)"
                            ),
                        ).set_footer(
                            text=("Requested by " + inter.user.name),
                            icon_url=inter.user.avatar,
                        ),
                        allowed_mentions=disnake.AllowedMentions(roles=True),
                    )

                    embed = disnake.Embed(
                        colour=disnake.Colour.orange(),
                        title="Someone will come and help soon!",
                        description="💬 While you wait, take this time to provide more context and details.\n\n✅ Once your question has been resolved (or you no longer need it), please click Resolve Question or run `/resolve`"
                    )
                    resolve_question_button = disnake.ui.Button(
                        label="Resolve Question",
                        custom_id="resolve_question_button",
                        style=disnake.ButtonStyle.green,
                        emoji="✅",
                    )

                    await inter.message.edit(
                        embed=embed, components=[resolve_question_button]
                    )

                    Log.info(f"{inter.author.name} summoned helpers")

                else:
                    embed = disnake.Embed(
                        colour=disnake.Colour.red(),
                        title="🕑 Be patient!",
                        description=(
                            f"Typically, you should get a response within 10 minutes, but our helpers are volunteers. We therefore need you to wait until <t:{int((datetime.datetime.now() + datetime.timedelta(minutes=30 - time_difference_minutes)).timestamp())}:t> before you use this button.\n\nIf nobody has helped you yet, try rephrasing your question, giving more details, or just being patient."
                        ),
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)
                    
                    Log.info(f"{inter.author.name} tried to summon helpers, but still has {str(30 - int(time_difference_minutes))} minutes left.")
            else:
                embed = disnake.Embed(
                    colour=disnake.Colour.red(),
                    title="❌ Summon Helpers",
                    description="You can't do this since you are neither a helper nor the owner of this channel!",
                )
                await inter.response.send_message(embed=embed, ephemeral=True)

        if inter.component.custom_id == "del_this_button":
            await inter.message.delete()
        if inter.component.custom_id == "close_report":
            embed = inter.message.embeds[0]
            embed.colour = disnake.Colour.blue()
            embed.title = "Closed Message Report"
            embed.add_field("Closed by",f"{inter.author.global_name} ({inter.author.id})",inline=False)
            
            await inter.message.edit(embed=embed,components=[],content="")
            
            await inter.response.send_message("Closed the report",ephemeral=True)
            
            Log.info(f"A message report was closed by {inter.author.name}")