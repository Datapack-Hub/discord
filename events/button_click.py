import disnake
from disnake.ext import commands
import variables
import datetime


class OnButtonClick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        print("asdasd")
        if inter.component.custom_id == "resolve_question_button":
            role = inter.guild.get_role(variables.helper)
            if (inter.channel.owner_id == inter.user.id) or (role in inter.user.roles):
                # Add tag
                resolved_tag = inter.channel.parent.get_tag_by_name("RESOLVED")
                await inter.channel.add_tags(resolved_tag)
                
                # Send message
                await inter.channel.send(embed=disnake.Embed(
                    color=disnake.Color.green(),
                    title=":white_check_mark: Closed Question",
                    description="Closed the channel and marled it as resolved! \nIf you have more questions feel free to ask them in a new channel!",
                ))
                
                # Ask for feedback
                await inter.response.send_message(ephemeral=True,embed=disnake.Embed(title="How was your experience?",description=f"Your question, <#{inter.channel.id}> ({inter.channel.name}), was resolved. Let us know how your experience asking your question in Datapack Hub was! It'll take no more than 3 clicks."),components=[disnake.ui.Button(custom_id="feedback_great",label="Great",style=disnake.ButtonStyle.success),disnake.ui.Button(custom_id="feedback_good",label="Good"),disnake.ui.Button(custom_id="feedback_okay",label="Okay"),disnake.ui.Button(custom_id="feedback_bad",label="Bad",style=disnake.ButtonStyle.red)])
                
                # Archive channel
                await inter.channel.edit(archived=True)
                                
                # Logging
                channel = self.bot.get_channel(variables.logs)
                await channel.send(embed=disnake.Embed(
                    color=disnake.Colour.orange(),
                    title=("**`Resolve Help Channel` Button**"),
                    description=(str(inter.user.name) + " resolved a help channel"),
                ))
            else:
                await inter.response.send_message(embed=disnake.Embed(
                    color=disnake.Color.red(),
                    title="❌ Resolve Help Channel",
                    description="You can't do this since you are neither a helper nor the owner of this channel!",
                ), ephemeral=True)

        if inter.component.custom_id == "summon_helpers_button":
            # Get time
            creation_time = inter.channel.create_timestamp
            current_time = datetime.datetime.now(creation_time.tzinfo)
            time_difference = current_time - creation_time
            time_difference_seconds = time_difference.total_seconds()
            time_difference_minutes = time_difference_seconds / 60

            # Get helper role
            role = inter.guild.get_role(
                variables.helper
            )
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
                        title=("**Someone will come and help soon!**"),
                        description=(
                            "💬 While you wait, take this time to provide more context and details. What are you trying to achieve overall - maybe there's an easier way to solve this problem\n\n🙇 ~~If it's been 30 minutes and you`re still waiting for someone to help, hit the __Summon Helpers__ button to call the official helpers here~~ **Someone has already summoned the helpers in this help channel!**\n\n✅ Once your question has been resolved (or you no longer need it), hit the __Resolve Question__ button or run /resolve"
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
            helper = role = inter.guild.get_role(
                variables.helper
            )
            if not helper in inter.author.roles:
                return await inter.response.send_message("Only helpers can use this :)",ephemeral=True)
            
            await inter.response.send_message(embed=disnake.Embed(
                title="Close Post",
                description="If this post is not appropriate for this channel, use one of the options below to close the post along with a reason to help the user know what they did wrong",
                colour=disnake.Colour.red()
            ),view=DropDownView(),ephemeral=True)
        if inter.component.custom_id == "del_this_button":
            await inter.message.delete()
        if inter.component.custom_id == "feedback_great":
            chan = await inter.guild.get_channel(variables.feedback)
            await chan.send(f"**Great** feedback on thread <#{str(inter.channel_id)}>")
            await inter.response.send_message("Thanks for your feedback!",ephemeral=True)
        if inter.component.custom_id == "feedback_good":
            chan = await inter.guild.get_channel(variables.feedback)
            await chan.send(f"**Good** feedback on thread <#{str(inter.channel_id)}>")
            await inter.response.send_message("Thanks for your feedback!",ephemeral=True)
        if inter.component.custom_id == "feedback_okay":
            chan = await inter.guild.get_channel(variables.feedback)
            await chan.send(f"**Okay** feedback on thread <#{str(inter.channel_id)}>")
            await inter.response.send_message("Thanks for your feedback!",ephemeral=True)
        if inter.component.custom_id == "feedback_bad":
            chan = await inter.guild.get_channel(variables.feedback)
            await chan.send(f"**Bad** feedback on thread <#{str(inter.channel_id)}>")
            await inter.response.send_message("Thanks for your feedback!",ephemeral=True)
            
            
class ChoiceMenu(disnake.ui.StringSelect):
    def __init__(self):
        options = [
            disnake.SelectOption(label="Incorrect Channel",description="This post is in an incorrect help channel."),
            disnake.SelectOption(label="Not Enough Information",description="This post does not have enough information."),
            disnake.SelectOption(label="Spam",description="This post is purely spam."),
            disnake.SelectOption(label="Off-topic",description="This post is not a question relevant to this context.")
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
            await inter.response.send_message(embed=disnake.Embed(
                title="CHANNEL CLOSED: Incorrect Channel",
                description="You've posted this question in an incorrect help channel. Please take another look at your question and put it in another help channel. Thanks.",
                color=disnake.Color.red()
            ))
            await inter.channel.edit(archived=True)
        elif selection == "Not Enough Information":
            await inter.response.send_message(embed=disnake.Embed(
                title="CHANNEL CLOSED: Not Enough Information",
                description="This post does not provide enough information for us to be able to help you. Please take a look in <#935570290317086841> to get some tips on how to write a good question. Thanks! :D",
                color=disnake.Color.red()
            ))
            await inter.channel.edit(archived=True)
        elif selection == "Spam":
            await inter.response.send_message(embed=disnake.Embed(
                title="CHANNEL CLOSED: Spam",
                description="This post is just spam. Please only post actual relevant questions in the help channels, otherwise you could face a punishment. Thanks!",
                color=disnake.Color.red()
            ))
            await inter.channel.edit(archived=True)
        elif selection == "Off-topic":
            await inter.response.send_message(embed=disnake.Embed(
                title="CHANNEL CLOSED: Off-topic",
                description="This post is off-topic. The help forums are for asking questions related to creating and using Minecraft datapacks and resource packs. For off-topic discussions, use the general or off topic text channels. Thanks!",
                color=disnake.Color.red()
            ))
            await inter.channel.edit(archived=True)
        
class DropDownView(disnake.ui.View):
    def __init__(self):
        # You would pass a new `timeout=` if you wish to alter it, but
        # we will leave it empty for this example so that it uses the default 180s.
        super().__init__()

        # Now let's add the `StringSelect` object we created above to this view
        self.add_item(ChoiceMenu())