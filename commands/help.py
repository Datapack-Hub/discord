import disnake
from disnake.ext import commands

OPTIONS = [
    {
        "label":"Staff",
        "content":
        """
        We've got a staff team of loads of nerdy datapack people. Here are the roles:
        
        **Managers**: Managers collaboratively own the server and administrate it. We're the people you should come to if you have any concern with the server, ideas, feedback, or more. Our DMs are open!
        
        **Moderators**: We pick Official Helpers who are especially active and helpful to be on our moderation team. You can ping the @Moderators role if anyone is breaking the rules.
        
        **Official Helpers**: 
        """
    },
    {
        "label":"Help Channels",
        "content":""""""
    },
    {
        "label":"External links",
        "content":""""""
    }
]

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description="View all the information")
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="<:datapackhelper:1129499893216579614> Welcome to Datapack Hub",
            description=f"We're a Discord community around **Minecraft Datapacks**. You're one of **{inter.guild.member_count}** members here. Thanks for joining us!\n\nUse the dropdown to select an area you need help with."
        )
        
        await inter.response.send_message(embed=embed,view=HelpView())

class HelpDropdown(disnake.ui.StringSelect):
    def __init__(self):
        options = [
            disnake.SelectOption(label=option["label"])
            for option in OPTIONS
        ]

        super().__init__(
            placeholder="What do you wanna find out about?",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        option = next(x for x in OPTIONS if x["label"] == self.values[0])
        await inter.response.edit_message(embed=disnake.Embed(
            title=f"<:datapackhelper:1129499893216579614> {option['label']}",
            description=option["content"]
        ))
        
class HelpView(disnake.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(HelpDropdown())