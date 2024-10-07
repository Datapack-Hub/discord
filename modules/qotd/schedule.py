import datetime
import asyncio
from disnake.ext.commands.bot import InteractionBot
from disnake import ForumChannel, AllowedMentions
from variables import qotd_channel, qotd_input_channel, qotd_role

def _seconds_until_oclock(hour: int):
    now = datetime.datetime.now()
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if now > target:
        target += datetime.timedelta(days=1)
    return (target - now).total_seconds()

async def schedule_qotd(bot: InteractionBot):
    while True:
        await asyncio.sleep(_seconds_until_oclock(13))

        # Find QOTD template to post
        input_channel = bot.get_channel(qotd_input_channel)
        question_short, question_long, question_author = None, None, None
        
        async for message in input_channel.history(limit=200):
            # If already posted, skip
            if (
                any(reaction.emoji == '✅' for reaction in message.reactions) or 
                any(reaction.emoji == '⛔' for reaction in message.reactions) or 
                type(message.content) != str 
                or message.author.bot
            ):
                continue
            
            # Check it follows the correct format
            content = str(message.content).split('\n')
            if len(content) != 2:
                await message.add_reaction("❌")
                continue
            
            # Store in variables
            question_short, question_long = content[0], content[1]
            question_author = message.author
            
            # Add reaction to mark it as posted
            await message.add_reaction('✅')
            
            # End here
            break
        if question_short is None or question_long is None or question_author is None:
            await input_channel.send("Help, I couldn't post a QOTD today! @everyone")
            continue

        # Create QOTD thread including embed and ping
        channel: ForumChannel = bot.get_channel(qotd_channel)
        qotd_day = int(channel.last_thread.name.split('.')[0]) + 1
        await channel.create_thread(
            name=f'{qotd_day}. {question_short}',
            content=f"##{question_long}\n<@&{qotd_role}>\n-# Suggested by {question_author.name}",
            allowed_mentions=AllowedMentions(everyone=False,roles=True,users=False)
        )
