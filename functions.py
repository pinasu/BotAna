#Bot useful functions

#Useful imports
import config, socket, time, json

#Function to send given message to the chat
def send_message(socket, message):
	socket.send(bytes("PRIVMSG "+config.CHAN+" :"+str(message)+"\r\n","UTF-8"))

#Function to send whisper to user
#Watch out, if you abuse using whispers Twitch will ban your Bot's account
def send_whisper(socket, message):
	socket.send(bytes("PRIVMSG #"+config.username+" "+message+"#\r\n", "UTF-8"))

#Function to check if user needs to be banned
def check_ban(socket):
	if config.username not in config.mods:
		if config.username == to_ban:
			#Ban user for 5 seconds, with no parameter is 600 seconds
			functions.send_message(socket , "/timeout "+config.username+" 5")
		else:
			to_ban = config.username
			functions.send_message(socket, config.username+", hai davvero bisogno di tutti queli caps? <warning>")

#Function to check if channel is online
def check_online(socket):
	offline = True
	url = "https://api.twitch.tv/kraken/streams/stockhausen_l2p"
	params = {"Client-ID" : ""+config.CLIENT_ID+""}
	resp = requests.get(url=url, headers=params)
	is_online = json.loads(resp.text)
	#Check if stream is offline or is a Vodcast
	while online["stream"] == None or online["stream"]["stream_type"] == "watch_party":
		#It's a vodcast
		if online["stream"]:
			if online["stream"]["stream_type"] == "watch_party":
				#Get user message
				rec = str(socket.recv(1024)).split("\\r\\n")
				if rec:
					for line in rec:
						parts = line.split(':')
						if len(parts) < 3: continue
						if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
							config.message = parts[2][:len(parts[2])]
						
						usernamesplit = parts[1].split("!")
						config.username = usernamesplit[0]

						if "tmi.twitch.tv" not in config.username:
							functions.send_message(s, "Ciao "+config.username+"! Questo è solo un Vodcast, ma Stockhausen_L2P torna (quasi) tutte le sere alle 20:00! PogChamp")
							time.sleep(0.5)
							functions.send_message(s, "PS: puoi comunque attaccarte a StoDiscord nel frattempo: https://goo.gl/2QSx3V KappaPride")
							time.sleep(300)

		resp = requests.get(url=url, headers=params)
		online = json.loads(resp.text)

		#Stockhausen always stream at 20, set for how much time will the Bot sleep
		if datetime.datetime.now().time.strftime('%H') == "19":
			offline = False

		if offline:
			time.sleep(900)
		else:
			time.sleep(300)
