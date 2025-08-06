import discord, json, asyncio
import variables
import utils.log as Log

def format_duration_between(date_time_start, date_time_end):
    time_difference = date_time_end - date_time_start

    # Calculate days, hours, and minutes
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Build the human-readable string
    formatted_duration = ""
    if days > 0:
        formatted_duration += f"{days}d"
    if hours > 0:
        formatted_duration += f"{hours}h"
    if minutes > 0:
        formatted_duration += f"{minutes}m"

    return formatted_duration if formatted_duration else "0m"

class StatsAdminCommand(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    stad = discord.SlashCommandGroup(name="stats-admin")
    
    @stad.command(description="Refreshes all stats. Only run this if you know what you're doing!")
    async def stats(inter: discord.ApplicationContext, channel: discord.ForumChannel):
        await inter.defer()
        data = []
        if channel.type.value == 15:
            i = 0
            threads = [thread async for thread in channel.archived_threads(limit=None)]
            
            print(f"{len(threads)!s} threads found.")

            # Use asyncio.gather to process threads concurrently, but limit concurrency to avoid rate limits
            semaphore = asyncio.Semaphore(6)  # Adjust concurrency as needed

            async def process_thread(thread: discord.Thread, idx):
                async with semaphore:
                    print(f"{idx!s}: Processing thread '{thread.name}'...")
                    try:
                        messages = [msg async for msg in thread.history(limit=None, oldest_first=True) if not msg.author.bot]
                        if len(messages) == 0:
                            print("This thread has no messages. Skipping.")
                            return None

                        first_answer = next(
                            (message for message in messages if not message.author.bot and message.author.id != thread.owner_id),
                            messages[0]
                        )

                        this = {
                            "name": thread.name,
                            "id": thread.id,
                            "tags": [tag.name for tag in thread.applied_tags],
                            "first_answer": {
                                "when": {
                                    "friendly": first_answer.created_at.strftime("%H:%M | %d/%m/%Y"),
                                    "timestamp": thread.created_at.timestamp()
                                },
                                "author": {
                                    "id": first_answer.author.id,
                                    "name": getattr(first_answer.author, "global_name", first_answer.author.name)
                                }
                            },
                            "asker": {
                                "id": thread.owner_id if thread.owner_id else 0,
                                "name": thread.owner.name if thread.owner else "???"
                            },
                            "duration": {
                                "friendly": format_duration_between(thread.created_at, thread.archive_timestamp),
                                "seconds": abs((thread.created_at - thread.archive_timestamp).total_seconds()),
                                "minutes": abs((thread.created_at - thread.archive_timestamp).total_seconds() / 60)
                            },
                            "created_at": {
                                "friendly": thread.created_at.strftime("%H:%M | %d/%m/%Y"),
                                "timestamp": thread.created_at.timestamp()
                            },
                            "archived_at": {
                                "friendly": thread.archive_timestamp.strftime("%H:%M | %d/%m/%Y"),
                                "timestamp": thread.archive_timestamp.timestamp()
                            },
                            "total_messages": len(messages)
                        }

                        # Count messages per person
                        participants = {}
                        for message in messages:
                            author = message.author
                            if author.id not in participants:
                                participants[author.id] = {
                                    "username": author.name,
                                    "id": author.id,
                                    "count": 1
                                }
                            else:
                                participants[author.id]["count"] += 1

                        this["participants"] = list(participants.values())
                    except Exception as e:
                        print("ERROR: " + " ".join(map(str, e.args)))
                        return None

                    print(f"{idx!s}: Finished processing thread '{thread.name}'.")
                    return this

            results = await asyncio.gather(
                *(process_thread(thread, idx + 1) for idx, thread in enumerate(threads))
            )
            data.extend([r for r in results if r is not None])

            # Write questions data
            with open("data/questions.json", "w") as f:
                json.dump(sorted(data, key=lambda d: d["total_messages"], reverse=True), f, indent=3)
            print("Saved Channel Data")

        # Process User Data
        users = {}
        for obj in data:
            print(obj["name"])
            for p in obj["participants"]:
                if p["id"] not in users:
                    users[p["id"]] = {
                        "username": p["username"],
                        "id": p["id"],
                        "data": {"messages": p["count"], "threads": 1}
                    }
                else:
                    users[p["id"]]["data"]["messages"] += p["count"]
                    users[p["id"]]["data"]["threads"] += 1

        users_list = sorted(users.values(), key=lambda d: d["data"]["messages"], reverse=True)
        with open("data/users.json", "w") as f:
            json.dump(users_list, f, indent=3)
        print("Saved User Data")
    
    @stad.command(name="update",description="force-update recently missed questions")
    async def cmd_update(self, inter: discord.ApplicationContext):
        channel: discord.ForumChannel = self.bot.get_channel(variables.help_channels[0])
        await inter.defer()
        
        with open("data/questions.json","r") as fp:
            data = json.load(fp)
            
        i=0
        
        async for thread in channel.archived_threads(limit=50):
            # Exclude threads which have already been processed
            if any(item["id"] == thread.id for item in data): continue
            
            i += 1
            
            try:
                messages = [msg async for msg in thread.history(limit=None, oldest_first=True) if not msg.author.bot]
                if len(messages) == 0:
                    print("This thread has no messages. Skipping.")
                    return None

                first_answer = next(
                    (message for message in messages if not message.author.bot and message.author.id != thread.owner_id),
                    messages[0]
                )

                this = {
                    "name": thread.name,
                    "id": thread.id,
                    "tags": [tag.name for tag in thread.applied_tags],
                    "first_answer": {
                        "when": {
                            "friendly": first_answer.created_at.strftime("%H:%M | %d/%m/%Y"),
                            "timestamp": thread.created_at.timestamp()
                        },
                        "author": {
                            "id": first_answer.author.id,
                            "name": getattr(first_answer.author, "global_name", first_answer.author.name)
                        }
                    },
                    "asker": {
                        "id": thread.owner_id if thread.owner_id else 0,
                        "name": thread.owner.name if thread.owner else "???"
                    },
                    "duration": {
                        "friendly": format_duration_between(thread.created_at, thread.archive_timestamp),
                        "seconds": abs((thread.created_at - thread.archive_timestamp).total_seconds()),
                        "minutes": abs((thread.created_at - thread.archive_timestamp).total_seconds() / 60)
                    },
                    "created_at": {
                        "friendly": thread.created_at.strftime("%H:%M | %d/%m/%Y"),
                        "timestamp": thread.created_at.timestamp()
                    },
                    "archived_at": {
                        "friendly": thread.archive_timestamp.strftime("%H:%M | %d/%m/%Y"),
                        "timestamp": thread.archive_timestamp.timestamp()
                    },
                    "total_messages": len(messages)
                }
                
                # Count messages per person
                participants = {}
                for message in messages:
                    author = message.author
                    if author.id not in participants:
                        participants[author.id] = {
                            "username": author.name,
                            "id": author.id,
                            "count": 1
                        }
                    else:
                        participants[author.id]["count"] += 1

                this["participants"] = list(participants.values())
                
            except Exception as err:
                Log.error(f"couldn't force update thread {thread.id}: {' '.join(err.args)}")
                
            else:
                data.append(this)
        
        with open("data/questions.json","w") as fp:
            json.dump(sorted(data, key=lambda d: d["total_messages"], reverse=True), fp)
        
        return await inter.respond(f"Force-updated {i} of the past 50 questions. If that number is more than 0, please contact Silabear.")
