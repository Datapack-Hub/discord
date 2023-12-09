import disnake
from disnake.ext import commands
import variables
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
                        color=disnake.Colour.green(),
                    )
                    .add_field("Original Message", messages[0].content, inline=False)
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
                        .add_button(label="Leave a rating:", disabled=True)
                        .add_button(
                            custom_id="feedback_great:" + str(inter.channel.owner_id),
                            label="Great",
                            style=disnake.ButtonStyle.success,
                        )
                        .add_button(
                            custom_id="feedback_okay:" + str(inter.channel.owner_id),
                            label="Meh",
                            style=disnake.ButtonStyle.blurple,
                        )
                        .add_button(
                            custom_id="feedback_bad:" + str(inter.channel.owner_id),
                            label="Bad",
                            style=disnake.ButtonStyle.red,
                        ),
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

                # Logging
                channel = self.bot.get_channel(variables.logs)
                await channel.send(
                    embed=disnake.Embed(
                        color=disnake.Colour.orange(),
                        title=("**`Resolve Help Channel` Button**"),
                        description=(str(inter.user.name) + " resolved a help channel"),
                    )
                )
            else:
                await inter.response.send_message(
                    embed=disnake.Embed(
                        color=disnake.Color.red(),
                        title="❌ Resolve Help Channel",
                        description="You can't do this since you are neither a helper nor the owner of this channel!",
                    ),
                    ephemeral=True,
                )

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
                        "<@&" + str(variables.helper) + ">",
                        embed=disnake.Embed(
                            color=disnake.Colour.blue(),
                            title=("**🙇 Helpers Arise!**"),
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
                        color=disnake.Colour.orange(),
                        title=("Someone will come and help soon!"),
                        description=(
                            """💬 While you wait, take this time to provide more context and details.\n\n
                            
                            🙇 After a while, hit the Summon Helpers button to ping the helper team. They'll be happy to help you\n\n
                            
                            ✅ Once your question has been resolved (or you no longer need it), please click Resolve Question or run /resolve"""
                        ),
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

                    # Logging
                    embed = disnake.Embed(
                        color=disnake.Colour.orange(),
                        title=("**`Summon Helpers` Button**"),
                        description=(str(inter.user.name) + " summoned helper"),
                    )
                    channel = self.bot.get_channel(variables.logs)
                    await channel.send(embed=embed)

                else:
                    embed = disnake.Embed(
                        color=disnake.Colour.red(),
                        title=("**🕑 Be patient!**"),
                        description=(
                            "All helpers are volunteers and thus can't always respond instantly. We'd therefore advise you to give them some time! If you still haven't gotten an answer in `"
                            + str(30 - int(time_difference_minutes))
                            + " minutes` feel free to use this again to ping all helpers :D"
                        ),
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)
                    # Logging
                    embed = disnake.Embed(
                        color=disnake.Colour.orange(),
                        title=("**`Summon Helpers` Button**"),
                        description=(
                            str(inter.user.name) + " failed summoning Helpers"
                        ),
                    )
                    channel = self.bot.get_channel(variables.logs)
                    await channel.send(embed=embed)
            else:
                embed = disnake.Embed(
                    color=disnake.Color.red(),
                    title="❌ Summon Helpers",
                    description="You can't do this since you are neither a helper nor the owner of this channel!",
                )
                await inter.response.send_message(embed=embed, ephemeral=True)

                # Logging
                embed = disnake.Embed(
                    color=disnake.Colour.orange(),
                    title=("**`Summon Helpers` Button**"),
                    description=(str(inter.user.name) + " failed summoning Helpers"),
                )
                channel = self.bot.get_channel(variables.logs)
                await channel.send(embed=embed)
        if inter.component.custom_id == "close_button":
            helper = role = inter.guild.get_role(variables.helper)
            if helper not in inter.author.roles:
                return await inter.response.send_message(
                    "Only helpers can use this :)", ephemeral=True
                )

            await inter.response.send_message(
                embed=disnake.Embed(
                    title="Close Post",
                    description="If this post is not appropriate for this channel, use one of the options below to close the post along with a reason to help the user know what they did wrong",
                    colour=disnake.Colour.red(),
                ),
                view=DropDownView(),
                ephemeral=True,
            )
        if inter.component.custom_id == "del_this_button":
            await inter.message.delete()

        if inter.component.custom_id.startswith("feedback_great"):
            user = int(inter.component.custom_id.split(":")[1])
            if inter.author.id != user:
                await inter.response.send_message(
                    "Only the question asker can respond!", ephemeral=True
                )
                return

            chan = self.bot.get_channel(variables.feedback)
            link = inter.message.components[1].children[0].url
            await inter.message.edit(
                components=disnake.ui.ActionRow()
                .add_button(
                    label="Jump to thread",
                    url=inter.message.components[1].children[0].url,
                    style=disnake.ButtonStyle.blurple,
                )
                .add_button(
                    label="Review Datapack Hub",
                    url="https://disboard.org/review/create/935560260725379143",
                    style=disnake.ButtonStyle.gray,
                )
            )
            await chan.send(f"**Great** feedback on [this thread]({link})")
            await inter.response.send_message(
                "Thanks for your feedback!", ephemeral=True
            )

            await inter.channel.edit(archived=True)

        if inter.component.custom_id.startswith("feedback_okay"):
            user = int(inter.component.custom_id.split(":")[1])
            if inter.author.id != user:
                await inter.response.send_message(
                    "Only the question asker can respond!", ephemeral=True
                )
                return

            chan = self.bot.get_channel(variables.feedback)
            link = inter.message.components[1].children[0].url
            await inter.message.edit(
                components=disnake.ui.ActionRow()
                .add_button(
                    label="Jump to thread",
                    url=inter.message.components[1].children[0].url,
                    style=disnake.ButtonStyle.blurple,
                )
                .add_button(
                    label="Review Datapack Hub",
                    url="https://disboard.org/review/create/935560260725379143",
                    style=disnake.ButtonStyle.gray,
                )
            )
            await chan.send(f"**Meh** feedback on [this thread]({link})")
            await inter.response.send_message(
                "Thanks for your feedback!", ephemeral=True
            )

            await inter.channel.edit(archived=True)

        if inter.component.custom_id.startswith("feedback_bad"):
            user = int(inter.component.custom_id.split(":")[1])
            if inter.author.id != user:
                await inter.response.send_message(
                    "Only the question asker can respond!", ephemeral=True
                )
                return

            chan = self.bot.get_channel(variables.feedback)
            link = inter.message.components[1].children[0].url
            await inter.message.edit(
                components=disnake.ui.ActionRow()
                .add_button(
                    label="Jump to thread",
                    url=inter.message.components[1].children[0].url,
                    style=disnake.ButtonStyle.blurple,
                )
                .add_button(
                    label="Review Datapack Hub",
                    url="https://disboard.org/review/create/935560260725379143",
                    style=disnake.ButtonStyle.gray,
                )
            )
            await chan.send(f"**Bad** feedback on [this thread]({link})")
            await inter.response.send_message(
                "Thanks for your feedback!", ephemeral=True
            )

            await inter.channel.edit(archived=True)


class ChoiceMenu(disnake.ui.StringSelect):
    def __init__(self):
        options = [
            disnake.SelectOption(
                label="Incorrect Channel",
                description="This post is in an incorrect help channel.",
            ),
            disnake.SelectOption(
                label="Not Enough Information",
                description="This post does not have enough information.",
            ),
            disnake.SelectOption(label="Spam", description="This post is purely spam."),
            disnake.SelectOption(
                label="Off-topic",
                description="This post is not a question relevant to this context.",
            ),
        ]

        super().__init__(
            placeholder="Select a reason",
            min_values=1,
            max_values=1,
            options=options,
        )

    # This callback is called each time a user has selected an option
    async def callback(self, inter: disnake.MessageInteraction):
        selection = self.values[0]
        if selection == "Incorrect Channel":
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="CHANNEL CLOSED: Incorrect Channel",
                    description="You've posted this question in an incorrect help channel. Please take another look at your question and put it in another help channel. Thanks.",
                    color=disnake.Color.red(),
                )
            )
            await inter.channel.edit(archived=True)
        elif selection == "Not Enough Information":
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="CHANNEL CLOSED: Not Enough Information",
                    description="This post does not provide enough information for us to be able to help you. Please take a look in <#935570290317086841> to get some tips on how to write a good question. Thanks! :D",
                    color=disnake.Color.red(),
                )
            )
            await inter.channel.edit(archived=True)
        elif selection == "Spam":
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="CHANNEL CLOSED: Spam",
                    description="This post is just spam. Please only post actual relevant questions in the help channels, otherwise you could face a punishment. Thanks!",
                    color=disnake.Color.red(),
                )
            )
            await inter.channel.edit(archived=True)
        elif selection == "Off-topic":
            await inter.response.send_message(
                embed=disnake.Embed(
                    title="CHANNEL CLOSED: Off-topic",
                    description="This post is off-topic. The help forums are for asking questions related to creating and using Minecraft datapacks and resource packs. For off-topic discussions, use the general or off topic text channels. Thanks!",
                    color=disnake.Color.red(),
                )
            )
            await inter.channel.edit(archived=True)


class DropDownView(disnake.ui.View):
    def __init__(self):
        # You would pass a new `timeout=` if you wish to alter it, but
        # we will leave it empty for this example so that it uses the default 180s.
        super().__init__()

        # Now let's add the `StringSelect` object we created above to this view
        self.add_item(ChoiceMenu())
