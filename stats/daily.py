import disnake
from disnake.ext import commands, tasks
from datetime import datetime
import variables as v
import json
import matplotlib.pyplot as plt


class DailyStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="daily", description="Show the daily stats")
    async def daily(inter: disnake.ApplicationCommandInteraction):
        past_data = json.loads(open("member_data.json", "r").read())
        today = datetime.now().date()
        joined_today = len(
            [
                member
                for member in inter.guild.members
                if member.joined_at.date() == today
            ]
        )
        increase_today = len(inter.guild.members) - past_data[-1]["Amount"]
        weekly_increase = increase_today * 7

        threads = 0
        for channel in v.help_channels:
            channel = inter.guild.get_channel(channel)
            threads += len(
                [
                    thread
                    for thread in channel.threads
                    if thread.created_at.date() == today
                ]
            )

        current_date_as_text = today.strftime("%d/%m/%y")
        past_data.append(
            {"Date": current_date_as_text, "Amount": len(inter.guild.members)}
        )

        # Graph
        recent_data = past_data[-7:]
        dates = [datetime.strptime(entry["Date"], "%d/%m/%y") for entry in recent_data]
        amounts = [entry["Amount"] for entry in recent_data]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, amounts, linestyle="-")

        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.title("Past Week Members")

        plt.savefig("out.png")

        output_embed = disnake.Embed(
            title=f"Datapack Hub Server Stats for <t:{int(datetime.now().timestamp())}:d>",
            description=f"""
            __**Member Stats**__
            **Joined Today**: `{joined_today}`
            **Increase Today**: `{increase_today}`
            **Averaged Weekly Increase**: `{weekly_increase}`
            
            __**Thread Stats**__
            **Posted Today**: `{threads}`""",
            color=disnake.Color.orange(),
        )

        await inter.response.send_message(embed=output_embed)
        await inter.send(file=disnake.File(open("out.png", "rb")))

        # json.dump(past_data,open("member_data.json","w"))

    @tasks.loop(hours=24)
    async def each_day(self):
        members = self.bot.get_guild(v.guild).members
        past_data = json.loads(open("member_data.json", "r").read())
        today = datetime.now().date()
        joined_today = len(
            [member for member in members if member.joined_at.date() == today]
        )
        increase_today = len(members) - past_data[-1]["Amount"]
        weekly_increase = increase_today * 7

        threads = 0
        for channel in v.help_channels:
            channel = self.bot.get_guild(v.guild).get_channel(channel)
            threads += len(
                [
                    thread
                    for thread in channel.threads
                    if thread.created_at.date() == today
                ]
            )

        current_date_as_text = today.strftime("%d/%m/%y")
        past_data.append({"Date": current_date_as_text, "Amount": len(members)})

        # Graph
        recent_data = past_data[-7:]
        dates = [datetime.strptime(entry["Date"], "%d/%m/%y") for entry in recent_data]
        amounts = [entry["Amount"] for entry in recent_data]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, amounts, linestyle="-")

        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.title("Past Week Members")

        plt.savefig("out.png")

        output_embed = disnake.Embed(
            title=f"Datapack Hub Server Stats for <t:{int(datetime.now().timestamp())}:d>",
            description=f"""
            __**Member Stats**__
            **Joined Today**: `{joined_today}`
            **Increase Today**: `{increase_today}`
            **Averaged Weekly Increase**: `{weekly_increase}`
            
            __**Thread Stats**__
            **Posted Today**: `{threads}`""",
            color=disnake.Color.orange(),
        )

        await (
            self.bot.get_guild(v.guild)
            .get_channel(1201576651746717696)
            .send(embed=output_embed)
        )
        await (
            self.bot.get_guild(v.guild)
            .get_channel(1201576651746717696)
            .send(file=disnake.File(open("out.png", "rb")))
        )

        json.dump(past_data, open("member_data.json", "w"))

    @commands.Cog.listener()
    async def on_ready(self):
        self.each_day.start()
