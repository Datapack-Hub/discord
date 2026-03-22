import discord

class SpamMessageView(discord.ui.DesignerView):
    def __init__(self):
        super().__init__(timeout=None)

        container = discord.ui.Container(color=discord.Color.from_rgb(222, 40, 65))
    
        container.add_text("## You were flagged for spamming multiple channels.")

        container.add_text("Your account was flagged by our automatic spam detection system for sending multiple messages across multiple channels in a short period of time. This is a common pattern with compromised or bot accounts, so your account has been kicked from Datapack Hub.")

        container.add_text("If this was an error, or if you have since regained access to your account, then feel free to rejoin the server. https://discord.gg/aEXsdjjdu4")

        container.add_text("-# This action was done automatically by our moderation bot.")

        self.add_item(container)