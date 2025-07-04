import discord

import utils.log as Log


class TopCommand(discord.Cog, name="top"):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(title="top", description="Jump to the top of the thread or channel!")
    async def top(self, inter: discord.ApplicationContext):
        message = await inter.channel.history(limit=1, oldest_first=True).flatten()

        await inter.response.send_message(
            components=[discord.ui.Button(label="Jump to top", url=message[0].jump_url)],
            ephemeral=True
        )

        Log.info(f"{inter.author.name} jumped to the top of channel #{inter.channel.name}")