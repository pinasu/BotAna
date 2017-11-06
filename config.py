#Bot config file

#Imports
    
#Function to read from file "bot_OAuth.txt" Bot Oauth
def get_bot_oauth():
    file = open("bot_OAuth.txt")
    oauth = file.read()
    print("\nBot OAuth was read correctly.\n")
    return oauth

#Function to read from tile "username" user's nickname
def get_nick():
    file = open("username.txt")
    nick = file.read()
    print("User's nickname was read correctly.\nConnecting to "+nick+"...\n")
    return nick

def get_clientID():
    file = open("clientID.txt")
    clientID = file.read()
    print("Client-ID was read correctly.\n")
    return clientID

#Twitch Host, always this
HOST = "irc.twitch.tv"

#Twitch port, always this
PORT = 6667

#Bot OAuth
BOT_OAUTH = get_bot_oauth()

#NICK and CHAN are basically the same, but CHAN comes with a "#" before the channel name
#Channel name
NICK = get_nick()

#Channel to join
CHAN = "#"+NICK

CLIENT_ID = get_clientID()

#Chatter's name
username = ""

#Current message
message = ""

#Current message arguments
arguments = ""

#Bot message rate to prevent excessive CPU usage
RATE = 20/30

#Mods list
mods = ["boomtvmod", "botana__", "boxyes", "frankiethor", "gurzo06", "ilmarcana", "iltegame", "khaleesix90", "moobot", "nightbot", "pinasu", "revlobot", "stockazzobot", "stockhausen_l2p", "tubbablubbah", "urza2k", "vivbot", "xuneera"]

#Chatter to ban, he's screaming too much.
to_ban = ""

#Mod commands
mods_commands = dict()

#Bot control
mods_commands ["!restart"   ] = ""
mods_commands ["!stop"              ] = ""
#Raffle related commands
mods_commands ["!clean"         ] = ""
mods_commands ["!raffle"        ] = ""
mods_commands ["!pickone"   ] = ""
#Warns a user if he's being a dick
mods_commands ["!warn"              ] = ""

#List of players that want to play
players = []

#Chat commands the bot responds to
commands = dict()

#Direct response to command
commands ["!alessiana"          ] = "Alessiana is toxic monkaS"
commands ["!energia"                    ] = "༼ つ ◕_◕ ༽つ ALESSIANA PRENDI LA MIA ENERGIA ༼ つ ◕_◕ ༽つ"
commands ["!tiltana"                    ] = "Quando le cose vanno male Alessiana si trasforma nel suo alterego Tiltana. Partono madonne e non riesce a non tiltare per qualsiasi cosa. Lo spam di LUL alimenta la sua ira che probabilmente lo porterà a ragequittare LUL"
commands ["!aim"                                    ] = "Nice aim bro LUL"
commands ["!battuta"                    ] = "haHAA Ha fatto la battuta haHAA Divertentissimo haHAA"
commands ["!fortnite"               ] = "Aggiungimi su Fortnite: Alessiana KappaPride"
commands ["!discord"                    ] = "Attaccate a StoDiscord: https://goo.gl/2QSx3V KappaPride"

#Response must be computed
commands ["!suoni"                          ] = ""
commands ["!8ball"                          ] = ""
commands ["!roulette"               ] = ""
commands ["!ban"                                    ] = ""
commands ["!love"                               ] = ""
commands ["!maledizione"    ] = ""
commands ["!play"                               ] = ""
commands ["!players"                    ] = ""

#Used commands
used = {}

#Users that want to play
players = []

#8ball choices
ball_choices = ["Non pensarci nemmeno LUL",
                                                                "Ma in che pianeta vivi LUL",
                                                                "Ma proprio no DansGame",
                                                                "Ti piacerebbe Kappa",
                                                                "Ma ovviamente PogChamp",
                                                                "Vai tranqui Kreygasm"
]

#Trick random
old_ball = ""

#Sounds list
