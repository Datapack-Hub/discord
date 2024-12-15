import disnake
from disnake.ext import commands
import utils.log as Log
from utils.stats import gen_json
import json
import variables
from datetime import datetime
from defs import ROOT_DIR
import os

def open_stats(flags: str = "r"):
    os.chdir(ROOT_DIR)
    directory = os.getcwd()
    data_path = os.path.join(directory, "data", "questions.json")
    
    return open(data_path, flags)
    
def format_duration_between(timestamp_start, timestamp_end, include_seconds=False):
    date_time_start = datetime.fromtimestamp(timestamp_start)
    date_time_end = datetime.fromtimestamp(timestamp_end)
    time_difference = date_time_end - date_time_start

    # Calculate days, hours, minutes, and seconds
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Build the human-readable string
    formatted_duration = ""
    if days > 0:
        formatted_duration += f"{days}d"
    if hours > 0:
        formatted_duration += f"{hours}h"
    if minutes > 0:
        formatted_duration += f"{minutes}m"

    if include_seconds:
        if minutes == 0 and hours == 0 and days == 0:
            formatted_duration += f"{seconds}s"
        elif seconds > 0:
            formatted_duration += f"{seconds}s"

    return formatted_duration if formatted_duration else "0m"

class StatsAdminCommand(commands.Cog, name="stats-admin"):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="stats-admin")
    async def statsadm(self, inter: disnake.ApplicationCommandInteraction):
        return
    
    @statsadm.sub_command(name="update",description="Force update stats to include any missed questions")
    async def cmd_update(self, inter: disnake.ApplicationCommandInteraction):
        channel = self.bot.get_channel(variables.help_channels[0])
        
        await inter.response.defer()
        
        data = json.load(open_stats())
        
        i = 0
        async for thread in channel.archived_threads(limit=50):
            # Exclude threads which have already been processed
            if len([item for item in data if item["id"] == thread.id]) != 0: continue
            i += 1
            
            try:
                this = await gen_json(thread)
            except Exception as e:
                Log.error(f"Error generating json for thread {thread}: {' '.join(e.args)}")
                continue
            else:
                data.append(this)
        
        json.dump(sorted(data, key=lambda d: d["total_messages"], reverse=True), open_stats("w"), indent=3)
        
        return await inter.edit_original_message(f"Force-updated {i} of the past 50 questions. If that number is more than 0, please contact Silabear.")
    
    @statsadm.sub_command(name="regen",description="Regenerate all stats (DO NOT RUN UNLESS YOU KNOW WHAT YOU ARE DOING)")
    async def cmd_regen(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        channel = self.bot.get_channel(variables.help_channels[0])
        
        data = []
        i = 0
        
        async for thread in channel.archived_threads(limit=None):
            i += 1
            
            # Exclude threads which have already been processed
            if len([item for item in data if item["id"] == thread.id]) != 0: continue
            i += 1
            
            try:
                this = await gen_json(thread)
            except Exception as e:
                Log.error(f"Error generating json for thread {thread}: {' '.join(e.args)}")
                continue
            else:
                data.append(this)
        
        json.dump(sorted(data, key=lambda d: d["total_messages"], reverse=True), open_stats("w"), indent=3)
        
        return await inter.edit_original_message(f"Regenerated {i} questions. It took a while.")
    
    @statsadm.sub_command(name="remove-duplicates",description="Remove any duplicate questions in the data")
    async def cmd_remove_dupes(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        data = json.load(open_stats("r"))
        
        i = 0
        
        unique_data = []
        seen_ids = set()

        for item in data:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                unique_data.append(item)
            else:
                i += 1

        data = unique_data
        
        json.dump(sorted(data, key=lambda d: d["total_messages"], reverse=True), open_stats("w"), indent=3)
        
        return await inter.edit_original_message(f"Removed {i} duplicate entries from the data.")