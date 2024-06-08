import json

def log(data: dict):
    modlogs_file = open("modlogs.json","r+")
    modlogs = json.load(modlogs_file)
    modlogs.append(data)
    modlogs_file.truncate()
    modlogs_file.seek(0)
    json.dump(modlogs,modlogs_file)
    modlogs_file.close()

def get_logs(user: int):
    modlogs_file = open("modlogs.json","r")
    modlogs = json.load(modlogs_file)
    logs = [item for item in modlogs if item.get("user") == user]
    modlogs_file.close()
    return logs