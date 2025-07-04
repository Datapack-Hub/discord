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

def info(message: str):
    print(f"{Colour.text.BLUE}INFO{Colour.RESET}  | " + str(message))
    
def debug(message: str):
    print(f"{Colour.text.bright.BLACK}DEBUG{Colour.RESET} | " + str(message))
    
def warn(message: str):
    print(f"{Colour.text.YELLOW}WARN{Colour.RESET}  | " + str(message))

def error(message: str):
    print(f"{Colour.text.RED}ERROR{Colour.RESET} | " + str(message))
    
def fatal(message: str):
    print(f"{Colour.bg.RED}FATAL{Colour.RESET} | " + str(message))