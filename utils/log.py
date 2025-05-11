import discord
import variables

class Colour:
    class text:
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        class bright:
            BLACK = '\033[90m'
            RED = '\033[91m'
            GREEN = '\033[92m'
            YELLOW = '\033[93m'
            BLUE = '\033[94m'
            MAGENTA = '\033[95m'
            CYAN = '\033[96m'
            WHITE = '\033[97m'

    class bg:
        BLACK = '\033[40m'
        RED = '\033[41m'
        GREEN = '\033[42m'
        YELLOW = '\033[43m'
        BLUE = '\033[44m'
        MAGENTA = '\033[45m'
        CYAN = '\033[46m'
        WHITE = '\033[47m'
        class bright:
            BLACK = '\033[100m'
            RED = '\033[101m'
            GREEN = '\033[102m'
            YELLOW = '\033[103m'
            BLUE = '\033[104m'
            MAGENTA = '\033[105m'
            CYAN = '\033[106m'
            WHITE = '\033[107m'

    # Reset code
    RESET = '\033[0m'
    
def _discord(message: str):
    # wh = discord.SyncWebhook.from_url("https://discord.com/api/webhooks/1280943139561013419/uOBxWfApyCitRmcvnqzZjTafAIJAwspT7ndB9-sIMc2I7mVEOxfFv8sWyU13zRXny_tl")
    # wh.send(message)
    pass

def info(message: str):
    print(f"{Colour.text.BLUE}INFO{Colour.RESET}  | " + message)
    _discord("**INFO** | " + message)
    
def debug(message: str):
    print(f"{Colour.text.bright.BLACK}DEBUG{Colour.RESET} | " + message)
    
def warn(message: str):
    print(f"{Colour.text.YELLOW}WARN{Colour.RESET}  | " + message)
    _discord("**WARN** | " + message)

def error(message: str):
    print(f"{Colour.text.RED}ERROR{Colour.RESET} | " + message)
    _discord("**ERROR** | " + message + " <@543741360478355456>")
    
def fatal(message: str):
    print(f"{Colour.bg.RED}FATAL{Colour.RESET} | " + message)
    _discord("**FATAL** | " + message + " <@543741360478355456>")