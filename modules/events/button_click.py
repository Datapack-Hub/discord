import disnake
from disnake.ext import commands
import variables
import datetime
import utils.log as Log
from utils.stats import update
from utils.res_thread import resolve_thread


class OnButtonClick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "resolve_question_button":
            role = inter.guild.get_role(variables.helper)
            if (inter.channel.owner_id == inter.user.id) or (role in inter.user.roles):
                if len(inter.channel.applied_tags.count) == 5:
                    await inter.response.send_message("This post has too many tags and the resolved tag cannot be applied. Please remove the least important one to properly resolve it.")
                else:
                    await inter.response.send_message("Done.")
                    await inter.delete_original_message()   
                    await resolve_thread(inter.channel,inter.author)
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
