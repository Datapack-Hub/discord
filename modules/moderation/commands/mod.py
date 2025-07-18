import discord
from pytimeparse.timeparse import timeparse
from datetime import datetime, timedelta
import variables
import io
from utils.uwufier import Uwuifier
import utils.modlogs as modlogs
from modules.moderation.components.views import UserModPanelView

REASONS = [
    {
        "label": "Excessive Swearing",
        "description": "You've been swearing a lot. We have a no swearing rule in this server.",
    },
    {
        "label": "Spam",
        "description": "Please don't spam in the channels - it's unnecessary and bad.",
    },
    {
        "label": "Inappropriate",
        "description": "This server is meant to be friendly for all ages. Please don't post inappropriate things.",
    },
    {
        "label": "Self Promotion",
        "description": "Please keep self promo to a minimum - it can get very annoying.",
    },
    {
        "label": "Homophobia",
        "description": "Homophobia is strictly not tolerated in Datapack Hub.",
    },
]

def generate_discord_relative_timestamp(seconds):
    # Calculate the future Unix timestamp
    future_timestamp = int((datetime.now() + timedelta(seconds=seconds)).timestamp())

    # Format the relative timestamp in the Discord style
    formatted_timestamp = f"<t:{future_timestamp}:R>"

    return formatted_timestamp


class ModCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    mod = discord.SlashCommandGroup(name="mod")
    
    @mod.command(description="Opens the moderation menu for a user")
    async def user(self, inter: discord.ApplicationContext, user: discord.Member):
        await inter.respond(view=UserModPanelView(user=user), ephemeral=True)
    
    @mod.command(description="Locks all server channels",)
    async def lockdown(self, inter: discord.ApplicationContext):
        await inter.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = False
        current_perms.send_messages_in_threads = False
        current_perms.create_public_threads = False
        current_perms.add_reactions = False
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.respond("🔒 **All server channels have been locked**")
        
    @mod.command(description="Unlocks all server channels",)
    async def unlockdown(self, inter: discord.ApplicationContext):
        await inter.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = True
        current_perms.send_messages_in_threads = True
        current_perms.create_public_threads = True
        current_perms.add_reactions = True
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.respond("🔓 **All server channels have been unlocked**")
            
        
    @mod.command(description="Bulk delete some messages")
    async def purge(
        self, 
        inter: discord.ApplicationContext, 
        limit: int = discord.Option(description="How many messages to remove"), 
        user: discord.User = discord.Option(description="User to delete messages from", required=False)
    ):
        # Stops the purge if the purge amount is over the API's limit
        if limit > 100:
            await inter.response.send_message(
                "You cannot delete more than 100 messages at once", ephemeral=True
            )
            return

        def is_user(m: discord.Message):
            if m.author != user:
                return False
            return True

        # Deletes the messages
        if user:
            deleted_messages = await inter.channel.purge(limit=limit, check=is_user)
        else:
            deleted_messages = await inter.channel.purge(limit=limit)

        # Logs the purge action
        log_embed = discord.Embed(
            colour=discord.Colour.orange(),
            title="`/purge` Command",
            description=f"{inter.user.name} purged {len(deleted_messages)} messages in {inter.channel.mention}.",
        )

        # Add the author and contents of the deleted messages to the log
        file_content = io.StringIO()
        for messages in deleted_messages:
            file_content.write(
                f"[{datetime.now().strftime('%d/%m/%y %H:%M:%S')}] @{messages.author.name}: {messages.content}\n"
            )

        file_content.seek(0)
        file = discord.File(fp=file_content, filename="purged messages.txt")

        log_channel = inter.guild.get_channel(variables.logs)

        await log_channel.send(embed=log_embed, file=file)

        # Confirm the purge
        await inter.response.send_message(
            f"{len(deleted_messages)} messages have been deleted", ephemeral=True
        )
        
    @mod.command(description="Ban literally everyone",)
    async def banall(self, inter: discord.ApplicationContext):
        #legi go away
        emb = discord.Embed(
            title="⚠️ BAN ALL MEMBERS",
            description="Are you sure? This action is IRREVERSIBLE. Flyne is going to be very angry if you run this command. ONLY USE THIS IN EMERGENCIES. You have been warned.",
            colour=discord.Colour.dark_red()
        )
        await inter.response.send_message(embed=emb,components=[discord.ui.Button(style=discord.ButtonStyle.red,label="CONFIRM")])

    def role_list(self):
        return [discord.OptionChoice(name=role.name,value=role.id) for role in self.bot.guild.roles if role.id in variables.mod_edit_roles]

    @mod.command(description="Grants or removes a (non-vital) role")
    async def role(
        self,
        inter: discord.ApplicationContext,
        user: discord.Member,
        role: discord.Role = discord.Option(discord.Role),
        modification: str = discord.Option(
            default = "add",
            choices = ["add", "remove"]
        )
    ):
        if not role.id in variables.mod_edit_roles:
            await inter.response.send_message(f"Role `{role.name}` is not allowed in this command", ephemeral=True)
            return

        try:
            if modification == "add":
                if role in user.roles:
                    await inter.response.send_message(f"User {user.name} already has the role {role}.", ephemeral=True)
                else:
                    await user.add_roles(role)
            else:
                if role in user.roles:
                    await user.remove_roles(role)
                else:
                    await inter.response.send_message(f"User {user.name} doesn't have the role {role}.", ephemeral=True)
        except:
            await inter.response.send_message(f"Failed to {modification} role {role.name}, to user {user.name}", ephemeral=True)
        await inter.response.send_message(f"Role {modification + ('ed' if modification == 'add' else 'd')}", ephemeral=True)
