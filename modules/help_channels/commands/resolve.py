import disnake
from disnake.ext import commands
import variables
import utils.log as Log
from utils.res_thread import resolve_thread


class ResolveCommand(commands.Cog, name="resolve"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(title="resolve", description="Marks question as resolved")
    async def resolve(self, inter: disnake.ApplicationCommandInteraction):
        role = inter.guild.get_role(variables.helper)
        
        # Try and get parent channel
        try:
            channel = inter.channel.parent.id
        except:
            await inter.response.send_message("Invalid",ephemeral=True)
            return False
        
        if (inter.channel.owner_id == inter.author.id) or (role in inter.author.roles) and channel in variables.help_channels:
            await inter.delete_original_message()
            if len(inter.channel.applied_tags) == 5:
                await inter.response.send_message("This post has too many tags and the resolved tag cannot be applied. Please remove the least important one to properly resolve it.")
            else:
                await inter.response.send_message("Done.")
                await resolve_thread(inter.channel,inter.author)
        else:
            await inter.response.send_message("You aren't allowed to do this here.", ephemeral=True)
            Log.info(f"{inter.author.name} tried to resolve a thread which wasn't theirs")
