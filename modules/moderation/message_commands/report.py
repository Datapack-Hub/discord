import discord
from discord.ext import commands
import variables

class ReportCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Report Message")
    async def report(self, inter: discord.MessageCommandInteraction):
        await inter.response.send_modal(ReportModal(inter.target))

class ReportModal(discord.ui.Modal):
    def __init__(self, message: discord.Message) -> None:
        self.message = message
        components = [
            discord.ui.TextInput(
                label="(Optional) Additional information",
                placeholder="If you have nothing to add, leave this blank.",
                custom_id="message",
                style=discord.TextInputStyle.long,
                required=False
            )
        ]
        super().__init__(title="Report Message", custom_id="report", components=components)

    async def callback(self, inter: discord.ModalInteraction) -> None:
        report_message = inter.text_values["message"]
        
        report_embed = discord.Embed(
            title="New Message Report",
            colour=discord.Colour.red()
        )
        
        report_embed.add_field("Message",self.message.clean_content,inline=False)
        report_embed.add_field("Additional Information",report_message if bool(report_message.strip()) else "None supplied",inline=False)
        report_embed.set_author(name=inter.author.global_name,icon_url=inter.author.avatar.url)
        
        await inter.guild.get_channel(variables.report_channel).send(
            content=f"<@&{variables.report_ping}>",
            allowed_mentions=discord.AllowedMentions(roles=True),
            embed=report_embed,
            components=[
                discord.ui.Button(url=self.message.jump_url,label="View Message"),
                discord.ui.Button(custom_id="close_report",label="Dismiss/Close Report",style=discord.ButtonStyle.red)
            ]
        )
        
        await inter.response.send_message(
            embed=discord.Embed(
                title="Reported message",
                colour=discord.Colour.orange(),
                description="Successfully reported the message to moderators.",
            )
            .add_field("Report Message",report_message if bool(report_message.strip()) else "None supplied",inline=False)
            .add_field("Infringing Message",f"`{self.message.clean_content}`",inline=False),
            ephemeral=True
        )

    async def on_error(self, error, interaction: discord.ModalInteraction) -> None:
        await interaction.response.send_message("Oops, something went wrong.", ephemeral=True)