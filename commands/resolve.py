import disnake
from disnake.ext import commands
import variables


class ResolveCommand(commands.Cog, name="resolve"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(title="resolve", description="Marks question as resolved")
    async def resolve(self, inter: disnake.ApplicationCommandInteraction):
        print(inter.channel.parent.threads.__len__())
        role = inter.guild.get_role(variables.helper)

        try:
            channel = inter.channel.parent.id
            if (inter.channel.owner_id == inter.author.id) or (
                role in inter.author.roles
            ):
                if channel in variables.help_channels:
                    resolved_tag = inter.channel.parent.get_tag_by_name("RESOLVED")
                    await inter.channel.add_tags(resolved_tag)
                    embed = disnake.Embed(
                        color=disnake.Color.green(),
                        title=":white_check_mark: Closed Question",
                        description="Closed the channel and marked it as resolved! \nIf you have more questions feel free to ask them in a new channel!",
                    )
                    await inter.channel.send(embed=embed)
                    await inter.channel.edit(archived=True)
                    # Ask for feedback
                    await inter.response.send_message(ephemeral=True,embed=disnake.Embed(title="How was your experience?",description=f"Your question, <#{inter.channel.id}> ({inter.channel.name}), was resolved. Let us know how your experience asking your question in Datapack Hub was! It'll take no more than 3 clicks."),components=[disnake.ui.Button(custom_id="feedback_great",label="Great",style=disnake.ButtonStyle.success),disnake.ui.Button(custom_id="feedback_good",label="Good"),disnake.ui.Button(custom_id="feedback_okay",label="Okay"),disnake.ui.Button(custom_id="feedback_bad",label="Bad",style=disnake.ButtonStyle.red)])
                    
                    # Logging
                    embed = disnake.Embed(
                        color=disnake.Colour.orange(),
                        title=("**`/resolve` Command**"),
                        description=(str(inter.user.name) + " resolved a help channel"),
                    )
                    channel = await inter.guild.get_channel(variables.logs)
                    await channel.send(embed=embed)
                    await inter.response.send_message(embed=embed)
                elif role not in inter.author.roles:
                    embed = disnake.Embed(
                        color=disnake.Color.red(),
                        title="❌ Resolve Help Channel",
                        description="You can only do this in one of our help channels",
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)

            else:
                embed = disnake.Embed(
                    color=disnake.Color.red(),
                    title="❌ Resolve Help Channel",
                    description="Only the creator of this question and helpers can mark it as resolved",
                )
                await inter.response.send_message(embed=embed, ephemeral=True)

        except:
            embed = disnake.Embed(
                color=disnake.Color.orange(),
                title="Resolve Help Channel",
                description="You can only do this in one of our help channels",
            )

            await inter.response.send_message(embed=embed, ephemeral=True)