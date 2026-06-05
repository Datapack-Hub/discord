import discord
from datetime import datetime, timedelta
import variables
import io
import utils
import utils.log as Log
from modules.moderation.components.views import UserModPanelView, UnableToModerateView, FeedbackView

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

class ModCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    mod = discord.SlashCommandGroup(name="mod")
    
    @mod.command(description="Opens the moderation menu for a user")
    async def user(self, inter: discord.ApplicationContext, user: discord.Member):
        if user.bot or (inter.guild.get_role(variables.staff) in user.roles):
            return await inter.respond(view=UnableToModerateView(), ephemeral=True)
        
        if not (inter.guild.get_role(variables.moderator) in inter.author.roles):
            return await inter.respond(view=UserModPanelView(user=user, helper_only=True), ephemeral=True)

        return await inter.respond(view=UserModPanelView(user=user), ephemeral=True)
    
    @mod.command(description="Locks all server channels",)
    async def lockdown(self, inter: discord.ApplicationContext):
        if not inter.guild.get_role(variables.moderator) in inter.author.roles:
            return await inter.respond(view=UnableToModerateView(), ephemeral=True)
        
        await inter.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = False
        current_perms.send_messages_in_threads = False
        current_perms.create_public_threads = False
        current_perms.add_reactions = False
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.respond("🔒 **All server channels have been locked**")
        
        Log.info("triggered server lockdown", inter.author.name)
        
    @mod.command(description="Unlocks all server channels",)
    async def unlockdown(self, inter: discord.ApplicationContext):
        if not inter.guild.get_role(variables.moderator) in inter.author.roles:
            return await inter.respond(view=UnableToModerateView(), ephemeral=True)
        
        await inter.defer()
        
        current_perms = inter.guild.default_role.permissions
        
        current_perms.send_messages = True
        current_perms.send_messages_in_threads = True
        current_perms.create_public_threads = True
        current_perms.add_reactions = True
        
        await inter.guild.default_role.edit(permissions=current_perms)
                
        await inter.respond("🔓 **All server channels have been unlocked**")

        Log.info("ended server lockdown", inter.author.name)
            
        
    @mod.command(description="Bulk delete some messages")
    async def purge(
        self, 
        inter: discord.ApplicationContext, 
        limit: int = discord.Option(description="How many messages to remove. (not how many messages to search)"), 
        user: discord.User = discord.Option(description="If specified, only deletes messages from this user", required=False)
    ):
        if not inter.guild.get_role(variables.moderator) in inter.author.roles:
            return await inter.respond(view=UnableToModerateView(), ephemeral=True)
        
        await inter.response.defer(ephemeral=True)
        limit = int(limit)
        
        # Stops the purge if the purge amount is over the API's limit
        if limit > 100:
            await inter.send_followup("You cannot delete more than 100 messages at once")
            return

        def is_user(m: discord.Message):
            if m.author != user:
                return False
            return True

        # Deletes the messages
        if user:
            deleted_messages = await inter.channel.purge(limit=limit, check=is_user, before=inter.interaction.created_at)
        else:
            deleted_messages = await inter.channel.purge(limit=limit, before=inter.interaction.created_at)

        # Logs the purge action
        deleted_messages.reverse()
        first_message = deleted_messages[0]
        last_message = deleted_messages[-1]

        log_embed = discord.Embed(
            title="Messages purged",
            description=f"{len(deleted_messages)!s} were deleted in {inter.channel.mention}.",
            colour=discord.Colour.red(),
        )
        log_embed.set_author(name=inter.user.global_name, icon_url=inter.user.avatar.url)

        log_embed.add_field(name="First message",value=utils.reference_message(first_message),inline=False)
        log_embed.add_field(name="Last message",value=utils.reference_message(last_message),inline=False)

        modlog_channel = inter.guild.get_channel(variables.modlogs)
        await modlog_channel.send(embed=log_embed)


        # Send deletion log to message log
        file_content = io.StringIO()
        file_content.write(f"The following {len(deleted_messages)!s} messages were purged at [{datetime.now().strftime('%d/%m/%y %H:%M:%S')}]:\n")
        for message in deleted_messages:
            file_content.write(
                f"[{message.created_at.strftime('%d/%m/%y %H:%M:%S')}] @{message.author.name}: {message.content}\n"
            )

        file_content.seek(0)
        file = discord.File(fp=file_content, filename="purged messages.txt")

        log_channel = inter.guild.get_channel(variables.logs)
        await log_channel.send(file=file)

        # Confirm the purge
        await inter.send_followup(view=FeedbackView(f"Bulk deleted {len(deleted_messages)} messages."))

        Log.info(f"removed ~{limit} messages in channel #{inter.channel.name}", inter.author.name)

        
    @mod.command(description="Ban literally everyone",)
    async def banall(self, inter: discord.ApplicationContext):
        if not inter.guild.get_role(variables.moderator) in inter.author.roles:
            return await inter.respond(view=UnableToModerateView(), ephemeral=True)
        
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
        if not inter.guild.get_role(variables.moderator) in inter.author.roles:
            return await inter.respond(view=UnableToModerateView(), ephemeral=True)
        
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

        Log.info("modified roles", inter.author.name)
