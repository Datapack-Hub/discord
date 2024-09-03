import disnake
from disnake.ext import commands
import json
from datetime import datetime, timedelta, time
from defs import ROOT_DIR
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
from collections import Counter
from dateutil import rrule

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

TIMEFRAME_OPTIONS = [
    {"friendly": "Last 7 days", "days": 7},
    {"friendly": "Last 30 days", "days": 30},
    {"friendly": "Last 90 days", "days": 90},
    {"friendly": "Last 365 days", "days": 365},
    {"friendly": "All Time", "days": 10000}
]

LEADERBOARD_OPTIONS = [
    "Top Helpers (messages)",
    "Top Helpers (threads)",
    "Top Askers",
    "Longest Questions",
    "Shortest Questions",
    "Quickest Responses"
]

DATA_OPTIONS = [
    "Time before response",
    "Total messages",
    "Amount of helpers",
    "Time question was asked"
]

GRAPH_OPTIONS = [
    "Questions Asked"
]

async def autocomplete_timeframe(inter: disnake.ApplicationCommandInteraction, string: str):
    string = string.lower()
    opts = [i["friendly"] for i in TIMEFRAME_OPTIONS]
    out = [opt for opt in opts if string in opt.lower()]
    if len(out) == 0: return [string]
    else: return out

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
            end_date = datetime.now()  
        
        # Check for "before dd/mm/yyyy" format
        elif date_range.startswith("before "):
            end_str = date_range.replace("before ", "")
            start_date = datetime(2022, 12, 11)  
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
            end_date = datetime.now()  
            start_date = end_date - timedelta(days=days)  
        
        # Check for "all time" format
        elif date_range == "all time":
            start_date = datetime(2022, 12, 11) 
            end_date = datetime.now()
            
        else:
            raise ValueError("Invalid format. Expected 'since', 'before', 'last', or 'dd/mm/yyyy to dd/mm/yyyy'.")

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
            default="last 7 days",
            autocomplete=autocomplete_timeframe
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
    
    @stats.sub_command(
        name="average",
        description="Shows averages of various data from help channels"
    )
    async def cmd_averages(
        inter: disnake.ApplicationCommandInteraction, 
        stat: str = commands.Param(
            description="The statistic to average",
            choices=DATA_OPTIONS
        ),
        timeframe: str = commands.Param(
            description="Accepts: 'last _ days', 'since/before dd/mm/yyyy', 'dd/mm/yyyy to dd/mm/yyyy'",
            default="last 7 days",
            autocomplete=autocomplete_timeframe
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
        
        stat = stat.lower()
        
        if stat == "time before response":
            avg = []

            for question in threads:
                avg.append(question["first_answer"]["when"]["timestamp"] - question["created_at"]["timestamp"])
                
            out = format_duration_between(0, sum(avg) / len(avg), True)
        elif stat == "total messages":
            avg = []

            for question in threads:
                avg.append(question["total_messages"])
                
            out = int(sum(avg) / len(avg))
        elif stat == "amount of helpers":
            avg = []

            for question in threads:
                avg.append(len([helper for helper in question["participants"] if helper["id"] != question["asker"]["id"]]))
                
            out = int(sum(avg) / len(avg))
        elif stat == "time question was asked":
            # TODO: make this return as a discord timestamp of today
            avg = []

            timestamps = [qn["created_at"]["timestamp"] for qn in threads]
            times_of_day = [datetime.fromtimestamp(ts).time() for ts in timestamps]
            times_in_seconds = [time.hour * 3600 + time.minute * 60 + time.second for time in times_of_day]
            avg_seconds = np.mean(times_in_seconds)
            avg_time_of_day = timedelta(seconds=avg_seconds)
            today = datetime.today()
            average_timestamp_today = datetime.combine(today, (datetime.min + avg_time_of_day).time())
            average_posix_timestamp = int(average_timestamp_today.timestamp())
                
            out = f"<t:{average_posix_timestamp}:t>"
        else:
            await inter.edit_original_message("Invalid statistic")
            
        out_embed = disnake.Embed(
            description=f"The average for `{stat}` during the timeframe `{timeframe}` is **{out}**.\n\n-# Updates in real-time. Only includes data from closed and archived threads in #datapack-help. Excludes bots.",
            color=disnake.Colour.orange()
        )
        
        await inter.edit_original_message(embed=out_embed)
        
    @stats.sub_command(
        name="graph",
        description="Shows a graph of various data from help channels"
    )
    async def cmd_graph(
        inter: disnake.ApplicationCommandInteraction, 
        stat: str = commands.Param(
            description="The statistic to generate a graph from",
            choices=GRAPH_OPTIONS
        ),
        timeframe: str = commands.Param(
            description="Accepts: 'last _ days', 'since/before dd/mm/yyyy', 'dd/mm/yyyy to dd/mm/yyyy'",
            default="last 7 days",
            autocomplete=autocomplete_timeframe
        )
    ):
        # Defer the response in case it takes time
        await inter.response.defer()

        # Load Question Data
        qn_data = json.load(open_stats())

        # Get timeframe
        timeframe = timeframe.lower()
        daterange = parse_date_range(timeframe)
        if daterange:
            start_timestamp, end_timestamp = parse_date_range(timeframe)
            start_timestamp = int(start_timestamp.timestamp())
            end_timestamp = int(end_timestamp.timestamp())
        else:
            return await inter.edit_original_message("Invalid date range")

        # Filter questions within the specified date range
        filtered_questions = [q for q in qn_data if start_timestamp <= q['created_at']['timestamp'] <= end_timestamp]

        # Calculate the total number of days in the date range
        date_range_days = (end_timestamp - start_timestamp) // (24 * 60 * 60)

        # Function to round down timestamp to the start of the day
        def round_to_day(timestamp):
            return datetime.fromtimestamp(timestamp).replace(hour=0, minute=0, second=0, microsecond=0)

        # Include the current time period in the graph
        now = round_to_day(int(datetime.now().timestamp()))  # Rounded to the start of the current day

        if date_range_days <= 14:
            dates = [round_to_day(q['created_at']['timestamp']).strftime('%Y-%m-%d') for q in filtered_questions]
            date_labels = [(round_to_day(start_timestamp) + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(date_range_days + 1)]

            # Add today's date if missing from date_labels
            if now.strftime('%Y-%m-%d') not in date_labels:
                date_labels.append(now.strftime('%Y-%m-%d'))

        elif date_range_days <= 90:
            dates = [round_to_day(q['created_at']['timestamp']).strftime('%Y-%W') for q in filtered_questions]
            week_start_dates = list(rrule.rrule(rrule.WEEKLY, dtstart=round_to_day(start_timestamp), until=round_to_day(end_timestamp)))
            date_labels = [d.strftime('%Y-%m-%d') for d in week_start_dates]

            # Add the start of the current week if not included
            current_week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
            if current_week_start not in date_labels:
                date_labels.append(current_week_start)

        elif date_range_days <= 600:
            dates = [round_to_day(q['created_at']['timestamp']).strftime('%b %y') for q in filtered_questions]
            month_start_dates = list(rrule.rrule(rrule.MONTHLY, dtstart=round_to_day(start_timestamp), until=round_to_day(end_timestamp)))
            date_labels = [d.strftime('%b %y') for d in month_start_dates]

            # Add the start of the current month if not included
            current_month_start = now.replace(day=1).strftime('%b %y')
            if current_month_start not in date_labels:
                date_labels.append(current_month_start)

        else:
            dates = [round_to_day(q['created_at']['timestamp']).strftime('%Y') for q in filtered_questions]
            year_start_dates = list(rrule.rrule(rrule.YEARLY, dtstart=round_to_day(start_timestamp), until=round_to_day(end_timestamp)))
            date_labels = [d.strftime('%Y') for d in year_start_dates]

            # Add the current year if not included
            current_year = now.strftime('%Y')
            if current_year not in date_labels:
                date_labels.append(current_year)

        # Sort the labels to maintain order
        date_labels.sort()

        # Count how many questions were asked in each period
        question_counts = Counter(dates)

        # Prepare data for plotting (if the date isn't in the counter, assume count is 0)
        counts = [question_counts.get(label, 0) for label in date_labels]
        
        # Graph prep
        font_prop = fm.FontProperties(fname=os.path.join(ROOT_DIR,"static","fonts","Lexend.ttf"))
        bold_font_prop = fm.FontProperties(fname=os.path.join(ROOT_DIR,"static","fonts","Lexend-Bold.ttf"))

        # Plotting the graph
        plt.figure(figsize=(10, 5), facecolor='#202020')
        ax = plt.gca()
        ax.set_facecolor('#202020')
        
        ax.spines['top'].set_edgecolor("#444444")
        ax.spines['left'].set_edgecolor("#444444")
        ax.spines['right'].set_edgecolor("#444444")
        ax.spines['bottom'].set_edgecolor("#444444")
        
        plt.tick_params(axis='x', colors='#444444')
        plt.tick_params(axis='y', colors='#444444')
        
        bars = plt.bar(date_labels, counts, color='#FF0081')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{height}',
                ha='center',
                va='bottom',
                fontsize=10,
                color='white'
            )
        
        plt.xlabel('Date', fontproperties=font_prop, color="#BBBBBB")
        plt.ylabel('Number of Questions', fontproperties=font_prop, color="#BBBBBB")
        plt.title('Number of Questions Asked Over Time', fontproperties=bold_font_prop, color="#FFFFFF")
        plt.xticks(rotation=45, fontproperties=font_prop, color="#AAAAAA")
        plt.yticks(fontproperties=font_prop, color="#AAAAAA")
        plt.tight_layout()
        
        plt.savefig(os.path.join(ROOT_DIR,"out.png"))
        
        await inter.edit_original_message(file=disnake.File(os.path.join(ROOT_DIR,"out.png")))