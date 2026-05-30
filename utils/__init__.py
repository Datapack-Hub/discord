import discord
from datetime import datetime, timedelta

def generate_future_timestamp(seconds: int, type: str = "R"):
    future_timestamp = int((datetime.now() + timedelta(seconds=seconds)).timestamp())
    formatted_timestamp = f"<t:{future_timestamp}:{type}>"
    return formatted_timestamp

def reference_message(message: discord.Message, char_limit: int = 100):
    author_name = message.author.name
    sent_at = int(message.created_at.timestamp())
    attachments = message.attachments

    return f'{author_name} (<t:{sent_at}:f>)```\n{message.content[:char_limit]}{"..." if len(message.content) > char_limit else ""} {f"[{len(attachments)} attachments]" if len(attachments) > 0 else ""}```'
