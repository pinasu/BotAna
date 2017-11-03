#Main application file

#Useful imports
import socket, functions, config, time

#First, we need to create the socket to connect to the chat
socket = socket.socket()

#Chat connection
socket.connect((config.HOST, config.PORT))

#Send to Twitch some usefuli nformations
#Bot OAuth, so he can write in chat
socket.send(bytes("PASS " + config.BOT_OAUTH + "\r\n", "UTF-8"))

#Channel to join
socket.send(bytes("NICK " + config.NICK + "\r\n", "UTF-8"))
socket.send(bytes("JOIN " + config.CHAN + "\r\n", "UTF-8"))

#Write to stdout to check if bot is connected
print("I'm now connected to "+ config.NICK + ".")

functions.check_online()

#Send first bot message to the chat he's connected to
functions.send_message(socket, "Don't even worry guys, Bottana is here anaLove")

#Bot main while loop
while True: #"while 1" if you prefere *lennyface*
	#Get Twitch chat current message
	rec = str(socket.recv(1024)).split("\\r\\n")

	if rec:
		#Parse received message
		for line in rec:
			#Response to Twitch, checking if the Bot is still woke
			if "PING" in line:
				s.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))
			else:
				#Get actual message and chatter username
				parts = line.split(':')
				if len(parts) < 3: continue
				if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
					config.message = parts[2]

				usernamesplit = parts[1].split("!")
				config.username = usernamesplit[0]

				#Print to stdout user's nick and message
				print(config.username+": "+config.message)

				message_list = config.message.split(' ');

				#Get command from message
				config.message = message_list[0]
				
				#Get message arguments, if there are any
				arguments = ' '.join(message_list[1:])

				#Check user message, if he's screaming he'll be warned by bot or banned
				if config.message.isupper() and len(config.message)-config.message.count(' ') > 15:
					functions.check_ban(s)
				
				elif config.message.startswith('!'):
					
	#Prevent Bot to use too much CPU
	time.sleep(1/config.RATE)
