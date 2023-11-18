import disnake
from disnake.ext import commands
import variables
import asyncio


class OnThreadCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: disnake.Thread):
        await asyncio.sleep(1)
        if thread.parent_id in variables.help_channels:
            embed = disnake.Embed(
                color=disnake.Colour.orange(),
                title=("**Someone will come and help soon!**"),
                description=(
                    "💬 While you wait, take this time to provide more context and details. What are you trying to achieve overall - maybe there's an easier way to solve this problem\n\n🙇 If it's been 30 minutes and you're still waiting for someone to help, hit the __Summon Helpers__ button to call the official helpers here\n\n✅ Once your question has been resolved (or you no longer need it), hit the __Resolve Question__ button or run /resolve"
                ),
            )
            summon_helpers_button = disnake.ui.Button(
                label="Summon Helpers",
                custom_id="summon_helpers_button",
                style=disnake.ButtonStyle.blurple,
                emoji="🙇",
            )
            resolve_question_button = disnake.ui.Button(
                label="Resolve Question",
                custom_id="resolve_question_button",
                style=disnake.ButtonStyle.green,
                emoji="✅",
            )
            close_button = disnake.ui.Button(
                label="🛡️", custom_id="close_button", style=disnake.ButtonStyle.red
            )

            messages = await thread.history(oldest_first=True, limit=1).flatten()
            await messages[0].pin()

            await thread.send(
                embed=embed,
                components=[
                    summon_helpers_button,
                    resolve_question_button,
                    close_button,
                ],
            )

            parent = thread.parent
            for t in parent.threads:
                if (
                    t.owner_id == thread.owner_id
                    and not t.archived
                    and thread.parent.get_tag_by_name("RESOLVED") not in t.applied_tags
                    and not t.id == thread.id
                ):
                    await thread.send(
                        embed=disnake.Embed(
                            title="⚠️ You already have a question open!",
                            description=f"Don't forget to close or resolve your old questions once you're done with them. It makes our lives much easier! :D\n\n**Open question**: <#{t.id}>",
                            color=disnake.Color.red(),
                        )
                    )
