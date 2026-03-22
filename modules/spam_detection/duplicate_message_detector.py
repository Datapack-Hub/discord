import discord
import variables
import time
from modules.spam_detection.components.views import SpamMessageView

class DuplicateMessageDetector(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.message_cache = []

    @discord.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or not msg.guild:
            return
        
        # get basic info
        user_id = msg.author.id
        current_time = time.time()
        channel_id = msg.channel.id
        content = msg.content.strip().lower()

        # remove old messages from cache
        self.message_cache = list(filter(lambda m: (current_time - m['time']) <= 7, self.message_cache))

        # add new message to cache
        self.message_cache.append({
            "user_id":user_id,
            "time":current_time,
            "channel_id":channel_id
        })

        # detect spam (3+ messages in 3+ channels in cache)
        from_user = list(filter(lambda m: m["user_id"] == user_id, self.message_cache))
        
        if len(from_user) < 3: # skip if less than 3 recent messages
            return
        
        different_channels = len({item['channel_id'] for item in from_user}) == len(from_user) # if amount of channels is equal to amount of messages then they are all in different channels

        if not different_channels: # skip if they're in the same channel
            return
        
        try:
            await msg.author.send(view=SpamMessageView()) # send user notice
        except: pass

        # remove users messages from cache
        self.message_cache = list(filter(lambda m: m["user_id"] != user_id, self.message_cache))

        # softban to remove messages
        try:
            await msg.author.ban(delete_message_seconds=30,reason="Spam detection system")
            await msg.author.unban(reason="Spam detection system")
        except:
            await msg.reply("-# <@&935629680520855552> Automatic spam detection system failed to softban this user.",allowed_mentions=discord.AllowedMentions(replied_user=False, roles=True))

        try:
            await msg.guild.get_channel(variables.modlogs).send(embed=discord.Embed(
                title="User Softbanned",
                description=f"{msg.author.name} (UID {msg.author.id}) was softbanned.",
                colour=discord.Colour.red(),
            )
            .set_author(name="Spam detection system")
            .add_field(name="Reason",value="Flagged by spam detection system for sending 3 messages across 3 channels within 7 seconds.",inline=False)
            .add_field(name="Message",value=f"```\n{content}\n\n({len(msg.attachments)} attachments)```",inline=False)
            )
        except:
            pass