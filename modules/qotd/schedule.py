import datetime
import asyncio
from disnake.ext.commands.bot import InteractionBot
from disnake import ForumChannel, Embed, Colour
from variables import qotd_channel, qotd_input_channel, qotd_role

def _seconds_until_oclock(hour: int):
    now = datetime.datetime.now()
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if now > target:
        target += datetime.timedelta(days=1)
    return (target - now).total_seconds()

async def schedule_qotd(bot: InteractionBot):
    while True:
        await asyncio.sleep(_seconds_until_oclock(18))
        # Everything past here will only be execute once a day at 18:00 (I don't know the timezone though)

        # Find QOTD template to post
        input_channel = bot.get_channel(qotd_input_channel) #! replace with actual QOTD input channel
        template_message = None
        async for message in input_channel.history(limit=200):
            if '✅' in message.reactions or type(message.content) != str:
                continue
            template_message = message
            await message.add_reaction('✅')
            break

        template_text = str(template_message.content).split('\n')
        qotd_short, qotd_full = template_text[0], template_text[1]

        # Create QOTD thread including embed and ping
        channel: ForumChannel = bot.get_channel(qotd_channel) #! QOTD Channel -> put into variables.py?
        qotd_day = int(channel.last_thread.name.split('.')[0]) + 1
        channel.create_thread(
            name=f'{qotd_day}. {qotd_short}',
            embed=Embed(
                colour=Colour.orange(),
                title=qotd_full,
                description=f'<@&{qotd_role}>', #! replace with QOTD ping role id
            ).set_footer(
                text=("Suggested by " + template_message.author.name),
                icon_url=template_message.author.avatar.url,
            )
        )
