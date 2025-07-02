import discord
from discord.ext import commands
import utils.log as Log


class RemindCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Remind them to resolve thread")
    async def remind(self, inter: discord.ApplicationContext, message: discord.Message):
        # Build the embed
        embed = discord.Embed(
            title="🎗️ Is your question resolved?",
            description="""
            If your question is resolved, that's great to hear! Make sure to run `/resolve` or click the Resolve Question button. Otherwise, feel free to continue asking for help! :D
            """,
            colour=discord.Colour.orange(),
        ).set_footer(
            text="Requested by " + inter.author.display_name,
            icon_url=inter.author.display_avatar.url,
        )
        
        # Send embed with resolve button
        await message.reply(
            embed=embed,
            components=[
                discord.ui.Button(
                    style=discord.ButtonStyle.success,
                    label="Resolve Question",
                    custom_id="resolve_question_button",
                )
            ],
        )
        
        # Send confirmation message
        await inter.response.send_message("Done! :D", ephemeral=True)
        
        Log.info(f"{inter.author.name} reminded OP to resolve the channel #{inter.channel.name}")
