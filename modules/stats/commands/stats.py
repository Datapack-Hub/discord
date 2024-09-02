import disnake
from disnake.ext import commands
import utils.log as Log
import json
import variables
from datetime import datetime, date, time, timedelta
from defs import ROOT_DIR
import os

def open_stats(flags: str = "r"):
    os.chdir(ROOT_DIR)
    directory = os.getcwd()
    data_path = os.path.join(directory, "data", "questions.json")
    
    return open(data_path, flags)
    
def format_duration_between(date_time_start, date_time_end, include_seconds=False):
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

TIMEFRAME_OPTIONS = [
    {"friendly": "Last 7 days", "days": 7},
    {"friendly": "Last 30 days", "days": 30},
    {"friendly": "Last 90 days", "days": 90},
    {"friendly": "Last 365 days", "days": 365}
]

LEADERBOARD_OPTIONS = [
    "Top Helpers (messages)",
    "Top Helpers (threads)",
    "Top Askers",
    "Longest Questions",
    "Shortest Questions",
    "Quickest Responses"
]

def parse_timeframe(option: str):
    for opt in TIMEFRAME_OPTIONS:
        if option.lower() == opt["friendly"].lower():
            return opt["days"]
    
    return None

def parse_date_range(date_range: str):
    try:
        # Define the date format we're expecting
        date_format = "%d/%m/%Y"
        
        # Check for "since dd/mm/yyyy" format
        if date_range.startswith("since "):
            start_str = date_range.replace("since ", "")
            start_date = datetime.strptime(start_str, date_format)
            end_date = datetime.now()  # Set the end date as the current date and time
        
        # Check for "before dd/mm/yyyy" format
        elif date_range.startswith("before "):
            end_str = date_range.replace("before ", "")
            start_date = datetime(1970, 1, 1)  # Set the start date as the Unix epoch (Jan 1, 1970)
            end_date = datetime.strptime(end_str, date_format)
        
        # Check for "dd/mm/yyyy to dd/mm/yyyy" format
        elif " to " in date_range:
            start_str, end_str = date_range.split(" to ")
            start_date = datetime.strptime(start_str, date_format)
            end_date = datetime.strptime(end_str, date_format)
        
        # Check for "last x days" format
        elif date_range.startswith("last "):
            days_str = date_range.replace("last ", "").strip().split()[0]
            days = int(days_str)
            end_date = datetime.now()  # Set the end date as the current date and time
            start_date = end_date - timedelta(days=days)  # Calculate the start date by subtracting x days
        
        else:
            raise ValueError("Invalid format. Expected 'since', 'before', 'last', or 'dd/mm/yyyy to dd/mm/yyyy'.")

        # Ensure that the start date is always earlier than the end date
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        return start_date, end_date

    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")

class StatsCommand(commands.Cog, name="stats"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="stats")
    async def stats(self, inter: disnake.ApplicationCommandInteraction):
        return
    
    @stats.sub_command(
        name="leaderboard",
        description="Shows leaderboards from help channels (default: past 7 days of helpers)"
    )
    async def cmd_leaderboard(
        inter: disnake.ApplicationCommandInteraction, 
        timeframe: str = commands.Param(
            description="Accepts: 'last _ days', 'since/before dd/mm/yyyy', 'dd/mm/yyyy to dd/mm/yyyy'",
            default="last 7 days"
        ),
        leaderboard: str = commands.Param(
            description="The leaderboard to show, based on #datapack-help data.",
            default="top helpers (messages)",
            choices=LEADERBOARD_OPTIONS
        )
    ):
        # Defer the response in case it takes forever
        await inter.response.defer()
        
        # Load Question Data
        qn_data = json.load(open_stats())
        
        # Get all threads made within the timeframe
        timeframe = timeframe.lower()
        daterange = parse_date_range(timeframe)
        if daterange:
            dates = parse_date_range(timeframe)
            threads = [thread for thread in qn_data if (thread["created_at"]["timestamp"] > dates[0].timestamp() and thread["created_at"]["timestamp"] < dates[1].timestamp())]
        else:
            return await inter.edit_original_message("Invalid dateframe")
        
        out = ""
        
        if leaderboard.lower() == "top helpers (messages)" or leaderboard.lower() ==  "top helpers (threads)":
            users = []
            
            def update_u_count(user: dict):
                for member in users:
                    if member["id"] == user["id"]:
                        member["data"]["messages"] += user["count"]
                        member["data"]["threads"] += 1
                        return
                
                users.append({"username": user["username"], "id":user["id"], "data":{"messages":user["count"],"threads":1}})
                
            for object in threads:
                for p in object["participants"]:
                    if p["id"] != object["asker"]["id"] and not any(c.isupper() for c in p["username"]):
                        update_u_count(p)
            
            # Sort data
            if leaderboard.lower() == "top helpers (messages)":
                lb = sorted(users, key=lambda d: d["data"]["messages"], reverse=True)
            else:
                lb = sorted(users, key=lambda d: d["data"]["threads"], reverse=True)
            
            # Generate leaderboard
            i = 0
            for user in lb[:20]:
                i += 1
                out += f'{i!s}. **{user["username"]}**: `{user["data"]["messages"]}` messages across `{user["data"]["threads"]}` threads\n'
                
        elif leaderboard.lower() == "top askers":
            users = []
            
            def update_u_count(asker: dict):
                for member in users:
                    if member["id"] == asker["id"]:
                        member["data"]["threads"] += 1
                        return
                
                users.append({"username": asker["name"], "id":asker["id"], "data":{"threads":1}})
                
            for object in threads:
                update_u_count(object["asker"])
                
            # Sort data
            lb = sorted(users, key=lambda d: d["data"]["threads"], reverse=True)
                
            # Generate leaderboard
            i = 0
            for user in lb[:20]:
                i += 1
                out += f'{i!s}. **{user["username"]}**: `{user["data"]["threads"]}` questions asked\n'
                
        elif leaderboard.lower() == "longest questions" or leaderboard.lower() == "shortest questions":
            # Sort data
            lb = sorted(threads, key=lambda d: d["total_messages"], reverse=True if leaderboard.lower() == "longest questions" else False)
            
            # Generate leaderboard
            i = 0
            for thread in lb[:20]:
                i += 1
                out += f'{i!s}. **{thread["name"]}** asked by {thread["asker"]["name"]}: `{thread["total_messages"]}` total messages\n'
        elif leaderboard.lower() == "quickest responses":
            new_threads = []
            
            for thread in threads:
                if not thread["first_answer"]["author"]["id"] == thread["asker"]["id"]:
                    thread["time"] = thread["first_answer"]["when"]["timestamp"] - thread["created_at"]["timestamp"]
                    print(thread["time"])
                    new_threads.append(thread)
                
            # Sort leaderboard
            lb = sorted(new_threads, key=lambda d: d["time"], reverse=True if leaderboard.lower() == "longest questions" else False)
            
            # Generate leaderboard
            i = 0
            for thread in lb[:20]:
                i += 1
                out += f'{i!s}. **{format_duration_between(thread["created_at"]["timestamp"], thread["first_answer"]["when"]["timestamp"],include_seconds=True)}** in the question `{thread["name"]}` (answered by {thread["first_answer"]["author"]["name"]})\n'
                
        else:
            return await inter.response.edit_message(f"{leaderboard.lower()} is an invalid leaderboard type.")
            
        out_embed = disnake.Embed(
            title=f"Leaderboard for {leaderboard.lower()}",
            description=f"Timeframe: `{timeframe.lower()}`\n" + out + "-# Updates in real-time. Only includes data from closed and archived threads in #datapack-help. Excludes bots.",
            colour=disnake.Colour.orange()
        )
        
        await inter.edit_original_message(embed=out_embed)
        
    @cmd_leaderboard.autocomplete("timeframe")
    async def autocomplete_timeframe(inter: disnake.ApplicationCommandInteraction, string: str):
        string = string.lower()
        opts = [i["friendly"] for i in TIMEFRAME_OPTIONS]
        return [opt for opt in opts if string in opt.lower()]
    
    ## STATS ADMIN BELOW ONLY
    
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
            if len([i for i in data if i["id"] == thread.id]) != 0: continue
            
            i += 1
            try:
                messages = await thread.history(limit=None, oldest_first=True).flatten()
                
                if messages.__len__() == 0:
                    print("what the fuck")
                    pass
                
                first_answer = next((message for message in messages if message.author.id != 1121129295868334220 and message.author.id != (thread.owner_id if thread.owner_id else 000)), messages[0])
                
                this = {
                    "name":thread.name,
                    "id":thread.id,
                    "first_answer":{
                        "when":{
                            "friendly":first_answer.created_at.strftime("%H:%M | %d/%m/%Y"),
                            "timestamp":thread.created_at.timestamp()
                        },
                        "author":{
                            "id":first_answer.author.id,
                            "name":first_answer.author.global_name
                        }
                    },
                    "asker":{
                        "id":thread.owner_id if thread.owner_id else 000,
                        "name":thread.owner.name if thread.owner else "unnamed"
                    },
                    "duration":{
                        "friendly":format_duration_between(thread.create_timestamp,thread.archive_timestamp),
                        "seconds":abs((thread.create_timestamp - thread.archive_timestamp).total_seconds()),
                        "minutes":abs((thread.create_timestamp - thread.archive_timestamp).total_seconds() / 60)
                    },
                    "created_at":{
                        "friendly":thread.created_at.strftime("%H:%M | %d/%m/%Y"),
                        "timestamp":thread.created_at.timestamp()
                    },
                    "archived_at":{
                        "friendly":thread.archive_timestamp.strftime("%H:%M | %d/%m/%Y"),
                        "timestamp":thread.archive_timestamp.timestamp()
                    },
                    "total_messages":messages.__len__()
                }
                
                participants = []
                
                def update_p_count(user: disnake.Member):
                    for member in participants:
                        if member["id"] == user.id:
                            member["count"] += 1
                            return
                    
                    participants.append({"username": user.name, "id":user.id, "count": 1})
                
                for message in messages:
                    update_p_count(message.author)
                
                this["participants"] = participants
                
                data.append(this)
            except Exception as e:
                print(">> [[SOMETHING WENT WRONG]] << | " + " ".join(e.args))
        
        json.dump(sorted(data, key=lambda d: d["total_messages"], reverse=True), open_stats("w"), indent=3)
        
        return await inter.edit_original_message(f"Force-updated {i} of the past 50 questions.")
    
    @statsadm.sub_command(name="regen",description="Regenerate all stats (DO NOT RUN UNLESS YOU KNOW WHAT YOU ARE DOING)")
    async def cmd_regen(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        channel = self.bot.get_channel(variables.help_channels[0])
        
        data = []
        i = 0
        
        async for thread in channel.archived_threads(limit=None):
            i += 1
            try:
                messages = await thread.history(limit=None, oldest_first=True).flatten()
                
                if messages.__len__() == 0:
                    print("what the fuck")
                    pass
                
                first_answer = next((message for message in messages if message.author.id != 1121129295868334220 and message.author.id != (thread.owner_id if thread.owner_id else 000)), messages[0])
                
                this = {
                    "name":thread.name,
                    "id":thread.id,
                    "first_answer":{
                        "when":{
                            "friendly":first_answer.created_at.strftime("%H:%M | %d/%m/%Y"),
                            "timestamp":first_answer.created_at.timestamp()
                        },
                        "author":{
                            "id":first_answer.author.id,
                            "name":first_answer.author.global_name
                        }
                    },
                    "asker":{
                        "id":thread.owner_id if thread.owner_id else 000,
                        "name":thread.owner.name if thread.owner else "unnamed"
                    },
                    "duration":{
                        "friendly":format_duration_between(thread.create_timestamp,thread.archive_timestamp),
                        "seconds":abs((thread.create_timestamp - thread.archive_timestamp).total_seconds()),
                        "minutes":abs((thread.create_timestamp - thread.archive_timestamp).total_seconds() / 60)
                    },
                    "created_at":{
                        "friendly":thread.created_at.strftime("%H:%M | %d/%m/%Y"),
                        "timestamp":thread.created_at.timestamp()
                    },
                    "archived_at":{
                        "friendly":thread.archive_timestamp.strftime("%H:%M | %d/%m/%Y"),
                        "timestamp":thread.archive_timestamp.timestamp()
                    },
                    "total_messages":messages.__len__()
                }
                
                participants = []
                
                def update_p_count(user: disnake.Member):
                    for member in participants:
                        if member["id"] == user.id:
                            member["count"] += 1
                            return
                    
                    participants.append({"username": user.name, "id":user.id, "count": 1})
                
                for message in messages:
                    update_p_count(message.author)
                
                this["participants"] = participants
                
                data.append(this)
            except Exception as e:
                print(">> [[SOMETHING WENT WRONG]] << | " + " ".join(e.args))
        
        json.dump(sorted(data, key=lambda d: d["total_messages"], reverse=True), open_stats("w"), indent=3)
        
        return await inter.edit_original_message(f"Regenerated {i} questions. It took a while.")
    
    @statsadm.sub_command(name="remove-duplicates",description="Remove any duplicate questions in the data")
    async def cmd_remove_dupes(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        channel = self.bot.get_channel(variables.help_channels[0])
        
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