from disnake import ApplicationCommandInteraction, Option
from disnake.ext import commands


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
    @commands.has_role('Moderator', 'Project Manager')
    async def purge(self, inter: ApplicationCommandInteraction, limit: int):
        """Deletes a specified number of messages from the channel."""
        if limit > 100:
            await inter.response.send_message("You cannot delete more than 100 messages at once", ephemeral=True)
            return

        deleted = await inter.channel.purge(limit=limit)
        await inter.response.send_message(f"{len(deleted)} messages have been deleted")



def setup(bot):
    bot.add_cog(PurgeCommand(bot))