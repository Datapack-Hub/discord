import discord
import variables
from modules.help_channels.res_thread import resolve_thread

class SummonHelpersButton(discord.ui.Button):
    def __init__(self, enabled = True):
        super().__init__(
            label="Summon Helpers",
            custom_id="summon_helpers_button",
            style=discord.ButtonStyle.blurple,
            emoji="🙇",
            disabled=enabled
        )
        
    async def callback(self, inter: discord.Interaction):
        from modules.help_channels.components.views import HelpChannelMessageView, SummonedHelpersView
        
        # Get helper role
        role = inter.guild.get_role(variables.helper)
        
        # Check user has permission
        if not (
            inter.channel.owner_id == inter.user.id or 
            role in inter.user.roles
        ):
            return await inter.respond("Only the original poster and staff members do this!",ephemeral=True)
        
        # Check that it has been half an hour
        time_difference = discord.utils.utcnow() - inter.message.channel.created_at
        time_difference_minutes = time_difference.total_seconds() / 60
        
        if time_difference_minutes < 2 and (not role in inter.user.roles):
            return await inter.respond("**Please be patient!** It has not been long enough to summon helpers. Please wait a bit more before trying again.",ephemeral=True)
        
        # Ping helpers
        await inter.respond(
            view=SummonedHelpersView(),
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        
        await inter.respond("Done!",ephemeral=True)
        
        # Edit the thing out
        await inter.message.edit(view=HelpChannelMessageView(created_at=inter.message.created_at, summoned=True))
        
class ResolveQuestionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Close Question",
            custom_id="resolve_question_button",
            style=discord.ButtonStyle.green,
            emoji="✅"
        )
        
    async def callback(self, inter: discord.Interaction):
        role = inter.guild.get_role(variables.helper)
        if (inter.channel.owner_id == inter.user.id) or (role in inter.user.roles):
            await resolve_thread(inter.channel, inter.response)
        else:
            await inter.respond("Only the original poster and staff members do this!",ephemeral=True)