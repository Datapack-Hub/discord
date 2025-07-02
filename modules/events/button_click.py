import discord
from discord.ext import commands
import variables
import utils.log as Log
from utils.res_thread import resolve_thread

class OnButtonClick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.Cog.listener("on_button_click")
    async def on_button_click(self, inter: discord.ApplicationContext):
        if inter.component.custom_id == "resolve_question_button":
            role = inter.guild.get_role(variables.helper)
            if (inter.channel.owner_id == inter.user.id) or (role in inter.user.roles):
                await resolve_thread(inter.channel, inter.response, inter.author)
            else:
                await inter.response.send_message(
                    embed=discord.Embed(
                        colour=discord.Colour.red(),
                        title="❌ Resolve Help Channel",
                        description="You can't do this since you are neither a helper nor the owner of this channel!",
                    ),
                    ephemeral=True,
                )
                
                Log.info(f"{inter.author.name} tried to close a help thread, but did not have permissions.")

        if inter.component.custom_id == "del_this_button":
            await inter.message.delete()
        if inter.component.custom_id == "close_report":
            embed = inter.message.embeds[0]
            embed.colour = discord.Colour.blue()
            embed.title = "Closed Message Report"
            embed.add_field("Closed by",f"{inter.author.global_name} ({inter.author.id})",inline=False)
            
            await inter.message.edit(embed=embed,components=[],content="")
            
            await inter.response.send_message("Closed the report",ephemeral=True)
            
            Log.info(f"A message report was closed by {inter.author.name}")
