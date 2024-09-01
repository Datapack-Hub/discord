import disnake
import variables
import json
import utils.log as log

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

async def update(thread: disnake.Thread):
    if thread.parent.id == variables.help_channels[0]: return True
    
    fp = open("data/questions.json","r")
    data = json.load(fp)
    fp.close()
    
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
        
        wfp = open("data/questions.json","w")
        json.dump(data,wfp)
        wfp.close()
    except Exception as e:
        log.error(">> [[SOMETHING WENT WRONG]] << | " + " ".join(e.args))
        
async def remove(id: int):
    try:
        fp = open("data/questions.json","r")
        data = json.load(fp)
        fp.close()
        
        data = [d for d in data if d["id"] != id]

        wfp = open("data/questions.json","w")
        json.dump(data,wfp)
        wfp.close()
    except Exception as e:
        log.error(">> [[SOMETHING WENT WRONG]] << | " + " ".join(e.args))