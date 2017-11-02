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

#Bot message rate to prevent excessive CPU usage
RATE = 20/30

#Mods list
mods = ["a"]

#Chatter to ban, he's screaming too much.
#First time is empty string
to_ban = ""