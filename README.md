# Datapack Hub Server Bot
This Discord bot is made to power the moderation, help systems, and more within the Datapack Hub server. Although the invite link is private, the code for this bot is completely open source.

## Setup
1. Install the packages. Just run `pip install -r requirements.txt`.
   > _(You may also use `pip3 install -r requirements.txt` depending on os and Python installation)_
2. Create a `variables.py`. This file will have all of your guild-specific data.
3. Create a `bottoken.py`, with your bot's token in the `TOKEN` variable.
4. Create a `automod.py`, with a `terms` string list.
5. Start the bot using `python index.py`.
   > _(You may also use `py index.py` or `python3 index.py` depending on os and Python installation)_

## Variables
`variables.py` should follow this structure:
```py
#! Logs

# logs: the id of the channel where general server logs should be posted to
logs = 12345

# modlogs: the id of the channel where moderation actions should be logged to
modlogs = 12345

# userlogs: the id of the channel where members joining/leaving should be logged to
userlogs = 12345

# automodlogs: the id of the channel where automod actions will be logged to
automodlogs = 12345

#! Channels

# help_channels: array of forum thread ids for the help channel system to work in
help_channels = [12345, 12345]

# stats_asked: the id of the channel to display "Questions Asked"
stats_asked = 12345

# new_member_channel: the id of the channel to post new member notices to
new_member_channel = 12345

# intro: the id of the channel where members post their introductions in
intro = 12345

# report_channel: the id of the channel where reports are posted to
report_channel = 12345

#! Roles

# helper: the id of the official helper role which is pinged when the "Summon Helpers" button is clicked
helper = 12345

# comm_helper_C: the id of the role to ping when a help post is created
comm_helper_C = 12345

# comm_helper_B: the id of the role to ping when the "Summon Helpers" button is clicked
comm_helper_B = 12345

# report_ping: the id of the role to ping when a report is created
report_ping = 12345

#! Misc

# guild: the id of the active guild
guild = 12345

# uwu_trigger: the word which triggers the uwufier
uwu_trigger = "abcde"
```
