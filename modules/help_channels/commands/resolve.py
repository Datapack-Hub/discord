import discord
from discord.ext import commands
import variables
import utils.log as Log
from utils.res_thread import resolve_thread


class ResolveCommand(commands.Cog, name="resolve"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(title="resolve", description="Marks question as resolved")
    async def resolve(self, inter: discord.ApplicationContext):
        role = inter.guild.get_role(variables.helper)
        
        # Try and get parent channel
        try:
            channel = inter.channel.parent.id
        except:
            await inter.response.send_message("Invalid",ephemeral=True)
            return False
        
        if (inter.channel.owner_id == inter.author.id) or (role in inter.author.roles) and channel in variables.help_channels:
            await resolve_thread(inter.channel, inter.response, inter.author)
        else:
            await inter.response.send_message("You aren't allowed to do this here.", ephemeral=True)
            Log.info(f"{inter.author.name} tried to resolve a thread which wasn't theirs")
