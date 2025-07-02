import discord
from modules.help_channels.components.buttons import SummonHelpersButton, ResolveQuestionButton
from datetime import datetime

def format_duration_between(date_time_start, date_time_end):
    time_difference = date_time_end - date_time_start

    # Calculate days, hours, and minutes
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Build the human-readable string
    formatted_duration = ""
    if days > 0:
        formatted_duration += f"{days}d"
    if hours > 0:
        formatted_duration += f"{hours}h"
    if minutes > 0:
        formatted_duration += f"{minutes}m"

    return formatted_duration if formatted_duration else "0m"

class HelpChannelMessageView(discord.ui.View):
    def __init__(self, created_at: datetime = discord.utils.utcnow(), threads: list[discord.Thread] = [],  summoned = False):
        super().__init__(timeout=None)
        
        container = discord.ui.Container()
        
        container.add_text("## Someone will come and help soon!")
        container.add_text("While you're waiting, please provide any more details to help us help you. What code have you tried already? What's your end goal?")
        
        container.add_separator(spacing=discord.SeparatorSpacingSize.small)
        
        sect1 = discord.ui.Section(accessory=SummonHelpersButton(enabled=summoned))
        sect1.add_item(discord.ui.TextDisplay("If nobody has come to help within half an hour, you can summon the helpers. Note that you can only do this once!"))
        container.add_item(sect1)
        
        container.add_separator(spacing=discord.SeparatorSpacingSize.small)
        
        sect2 = discord.ui.Section(accessory=ResolveQuestionButton())
        sect2.add_item(discord.ui.TextDisplay("Once you're done, close the post, either by running `/resolve`, closing it in the menu, or clicking this button."))
        container.add_item(sect2)
        
        container.add_text(f"-# You opened this help thread {discord.utils.format_dt(created_at, style='R')}")
        
        self.add_item(container)
        
        if len(threads) > 0:
            warning_container = discord.ui.Container(color=discord.Color.red())
            
            warning_container.add_text("### You have open threads!")
            warning_container.add_text("Please make sure to close your open threads if you're done with them:")
            
            for thread in threads:
                sect = discord.ui.Section(accessory=discord.ui.Button(label="Go to thread",url=thread.jump_url))
                sect.add_text("- `" + thread.name.replace('`', '\`') + f"` opened {discord.utils.format_dt(thread.created_at, style='R')}")
                warning_container.add_item(sect)
                
            self.add_item(warning_container)
            
class ResolvedThreadView(discord.ui.View):
    def __init__(self, thread: discord.Thread):
        super().__init__(timeout=None)
        
        container = discord.ui.Container()
        
        container.add_text("## Question closed!")
        container.add_text(f"Your question, <#{thread.id}> ({thread.name}), was resolved!")
        
        if thread.starting_message:
            sect1 = discord.ui.Section(accessory=discord.ui.Button(label="Jump to top", url=thread.starting_message.jump_url))
            sect1.add_text(f"This thread was open for {format_duration_between(thread.created_at,discord.utils.utcnow())}")
            container.add_item(sect1)
        else:
            container.add_text(f"This thread was open for {format_duration_between(thread.created_at,discord.utils.utcnow())}")
        
        container.add_text("React to this message with 🔓 to unlock the thread, if you have any other questions or if you closed it by mistake.")
        
        container.add_text(f"-# You closed this help thread {discord.utils.format_dt(discord.utils.utcnow(), style='R')}")
        
        self.add_item(container)