import io
from disnake import ApplicationCommandInteraction, Option, Embed, Colour, File
from disnake.ext import commands
import variables


class PurgeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='purge',
        description='Deletes a specified number(max.  100) of messages from the channel.',
        options=[
            Option(
                name='limit',
                description='Number of messages to delete',
                type=ApplicationCommandInteraction.integer,
                required=True
            )
        ]
    )
    # Deletes a specified number of messages from the channel and logs the action
    async def purge(self, inter: ApplicationCommandInteraction, limit: int):
        # Stops the purge if the purge amount is over the API's limit
        if limit > 100:
            await inter.response.send_message("You cannot delete more than 100 messages at once", ephemeral=True)
            return

        # Deletes the messages
        deleted_messages = await inter.channel.purge(limit=limit)

        # Logs the purge action
        log_embed = Embed(
            color=Colour.orange(),
            title="**` /purge` Command**",
            description=f"{inter.user.name} purged {len(deleted_messages)} messages in {inter.channel.mention}."
        )
        
        # Add the autor and contents of the deleted messages to the log
        if variables.send_log_messages_as_embed: # as an embed
            for messages in deleted_messages:
                log_embed.add_field(name="Autor", value=messages.author.name, inline=False)
                log_embed.add_field(name="Content", value=messages.content, inline=False)
        else: # as a txt file
            file_content = io.StringIO()
            for messages in deleted_messages:
                file_content.write(f"Author: {messages.author.name}\nContent: {messages.content}\n\n")

            file_content.seek(0)
            file = File(fp=file_content, filename="purged messages.txt")
            

        log_channel_id = variables.logs
        log_channel = await inter.guild.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=log_embed, file=file)

        # Confirm the purge
        await inter.response.send_message(f"{len(deleted_messages)} messages have been deleted", ephemeral=True)
