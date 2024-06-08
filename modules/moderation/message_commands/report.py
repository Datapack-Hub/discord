import disnake
from disnake.ext import commands
import variables

class ReportCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Report Message")
    async def report(self, inter: disnake.MessageCommandInteraction):
        await inter.response.send_modal(ReportModal(inter.target))

class ReportModal(disnake.ui.Modal):
    def __init__(self, message: disnake.Message) -> None:
        self.message = message
        components = [
            disnake.ui.TextInput(
                label="(Optional) Additional information",
                placeholder="If you have nothing to add, leave this blank.",
                custom_id="message",
                style=disnake.TextInputStyle.long,
                required=False
            )
        ]
        super().__init__(title="Report Message", custom_id="report", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        report_message = inter.text_values["message"]
        
        report_embed = disnake.Embed(
            title="New Message Report",
            colour=disnake.Colour.red()
        )
        
        report_embed.add_field("Message",self.message.clean_content,inline=False)
        report_embed.add_field("Additional Information",report_message if bool(report_message.strip()) else "None supplied",inline=False)
        report_embed.set_author(name=inter.author.global_name,icon_url=inter.author.avatar.url)
        
        await inter.guild.get_channel(variables.report_channel).send(
            content=f"<@&{variables.report_ping}>",
            allowed_mentions=disnake.AllowedMentions(roles=True),
            embed=report_embed,
            components=[
                disnake.ui.Button(url=self.message.jump_url,label="View Message"),
                disnake.ui.Button(custom_id="close_report",label="Dismiss/Close Report",style=disnake.ButtonStyle.red)
            ]
        )
        
        await inter.response.send_message(
            embed=disnake.Embed(
                title="Reported message",
                colour=disnake.Colour.orange(),
                description="Successfully reported the message to moderators.",
            )
            .add_field("Report Message",report_message if bool(report_message.strip()) else "None supplied",inline=False)
            .add_field("Infringing Message",f"`{self.message.clean_content}`",inline=False),
            ephemeral=True
        )

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.", ephemeral=True)