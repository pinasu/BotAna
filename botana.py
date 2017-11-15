#Main application file

#Useful imports
import socket, time, json, requests, datetime, command, os, traceback, subprocess, random, csv, pygame
from pygame import mixer
from random import randint
from command import Command
from sound import Sound
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

class BotAna(QtCore.QThread):
	sign = pyqtSignal(str)
	sign2 = pyqtSignal(str)
	def __init__(self):
		super().__init__()
		#First, we need to create the socket to connect to the chat
		self.sock = socket.socket()
		#Twitch Host, always this
		self.HOST = "irc.twitch.tv"
		#Twitch port, always this
		self.PORT = 6667
		#name of Bot
		self.botName = "BotAna__"
		#Bot OAuth
		self.BOT_OAUTH = ""
		#NICK and CHAN are basically the same, but CHAN comes with a "#" before the channel name
		#Channel name
		self.NICK = ""
		#Channel to join
		self.CHAN = ""
		#Appliation Client ID
		self.CLIENT_ID = ""
		#Chatter's name
		self.username = ""
		#Current message
		self.message = ""
		#Current message arguments
		self.arguments = ""
		#Bot message rate to prevent excessive CPU usage
		self.RATE = 20/30
		#Mods list
		self.mods = ["lusyoo", "boomtvmod", "botana__", "boxyes", "frankiethor", "gurzo06", "ilmarcana", "iltegame", "khaleesix90", "nightbot", "pinasu", "stockhausen_l2p", "tubbablubbah", "urza2k", "xuneera"]
		#Chatter to ban, he's screaming too much.
		self.to_ban = ""
		#List of players that want to play
		self.players = []
		#Used commands
		self.used = {}
		#Users that want to play
		self.players = []
		#8ball choices
		self.ball_choices = ["Non pensarci nemmeno LUL",
						"Ma in che pianeta vivi LUL",
						"Ma proprio no DansGame",
						"Ti piacerebbe Kappa",
						"Ma ovviamente PogChamp",
						"Vai tranqui Kreygasm"
		]
		#Collect times of lasts commands calls
		self.timeCommandsModCalled = dict()
		self.timeCommandsPlebCalled = dict()

		self.commandsMod = dict()
		self.commandsPleb = dict()

		self.sounds = dict()
		self.timeSoundCalled = dict()

		self.skippers = []
		self.skip_count = 0

	def run(self):
		try:
			#Bot OAuth
			self.BOT_OAUTH = self.get_bot_oauth()
			#NICK and CHAN are basically the same, but CHAN comes with a "#" before the channel name
			#Channel name
			self.NICK = self.get_nick()
			#Channel to join
			self.CHAN = "#"+self.NICK
			self.CLIENT_ID = self.get_clientID()
			self.loadCommands()
			self.loadSounds()
			
			#Chat connection
			self.sock.connect((self.HOST, self.PORT))

			#Send to Twitch some useful informations
			#Bot OAuth, so he can write in chat
			self.sock.send(bytes("PASS " + self.BOT_OAUTH + "\r\n", "UTF-8"))

			#Channel to join
			self.sock.send(bytes("NICK " + self.NICK + "\r\n", "UTF-8"))
			self.sock.send(bytes("JOIN " + self.CHAN + "\r\n", "UTF-8"))

			#Write to stdout to check if bot is connected
			self.printMessage("I'm now connected to "+ self.NICK + ".")

			self.check_online()

			#Send first bot message to the chat it's connected to
			self.send_message("Don't even worry guys, Bottana is here anaLove")
		
			#Bot main while loop
			while True: #"while 1" if you prefere *lennyface*

				#Get Twitch chat current message
				rec = str(self.sock.recv(1024)).split("\\r\\n")

				#da sistemare
				#rec = rec.decode('utf-8')
				
				if rec:
					#Parse received message
					for line in rec:
						#Response to Twitch, checking if the Bot is still woke
						if "PING" in line:
							self.sock.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))
						else:
							#Get actual message and chatter username
							parts = line.split(':')
							if len(parts) < 3: continue
							if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
								self.message = parts[2]

							usernamesplit = parts[1].split("!")
							self.username = usernamesplit[0]

							#Print to stdout user's nick and message
							self.printMessage(self.username+": "+self.message)

							message_list = self.message.split(' ');

							#Get command from message
							self.message = message_list[0]
							
							#Get message arguments, if there are any
							self.arguments = ' '.join(message_list[1:])

							#Check user message, if he's screaming he'll be warned by bot or banned
							if sum(1 for c in self.message if c.isupper()) + sum(1 for c in self.arguments if c.isupper())> 15:
								self.check_ban()
							
							#Message is a command
							elif self.message.startswith('!'):
								if self.message in self.commandsMod.keys() and self.username in self.mods:
									self.call_command_mod()
								else:
									self.call_command_pleb()

								if self.message in self.sounds.keys():
									self.call_sound()

				#Prevent Bot to use too much CPU
				time.sleep(1/self.RATE)
		except:
			self.printMessage("----------SI E' VERIFICATO UN ERRORE, TI PREGO RIAVVIAMI----------")
			file = open("LogError.txt", "a")
			file.write(time.strftime("[%d/%m/%Y - %I:%M:%S] ") + traceback.format_exc() + "\n")
			traceback.print_exc()

	def __del__(self):
		self.exiting = True
		self.wait()

	def showImage(self, path):
		self.sign2.emit(path)

	def printMessage(self, msg):
		print(msg)
		self.sign.emit(msg)

	def readConfigFile(self, path):
		if os.path.exists(path):
			try:
				with open(path,"r") as f:
					tmp = f.read()
					self.printMessage(path + " was read correctly.")
					return tmp
			except: # whatever reader errors you care about
				self.printMessage("Error reading " + path + "\n")
		else:
			self.printMessage("Error reading " + path + "\n")

	def get_bot_oauth(self):
		return self.readConfigFile("bot_OAuth.txt")

	#Function to read from tile "username" user's nickname
	def get_nick(self):
		return self.readConfigFile("username.txt")

	def get_clientID(self):
		return self.readConfigFile("clientID.txt")

	#Function to send given message to the chat
	def send_message(self, message):
		self.sock.send(bytes("PRIVMSG "+self.CHAN+" :"+str(message)+"\r\n","UTF-8"))
		self.printMessage(self.botName + ": " + message)

	#Function to send whisper to user
	#Watch out, if you abuse using whispers Twitch will ban your Bot's account
	def send_whisper(self, message):
		self.sock.send(bytes("PRIVMSG #"+self.username+" "+message+"#\r\n", "UTF-8"))

	#Function to check if user needs to be banned
	def check_ban(self):
		if self.username not in self.mods:
			if self.username == to_ban:
				#Ban user for 5 seconds, with no parameter is 600 seconds
				self.send_message("/timeout "+self.username+" 5")
			else:
				to_ban = self.username
				self.send_message(self.username+", hai davvero bisogno di tutti queli caps? <warning>")

	#Function to check if channel is online
	def check_online(self):
		'''Momentaneamente commentata per far credere al bot che il canale è live
	##    offline = True
	##    url = "https://api.twitch.tv/kraken/streams/"+self.NICK+""
	##    params = {"Client-ID" : ""+self.CLIENT_ID+""}
	##    resp = requests.get(url=url, headers=params)
	##    online = json.loads(resp.text)
	##    #Check if stream is offline or is a Vodcast
	##    while online["stream"] == None or online["stream"]["stream_type"] == "watch_party":
	##        #It's a vodcast
	##        if online["stream"]:
	##            if online["stream"]["stream_type"] == "watch_party":
	##                #Get user message
	##                rec = str(self.sock.recv(1024)).split("\\r\\n")
	##                if rec:
	##                    for line in rec:
	##                        parts = line.split(':')
	##                        if len(parts) < 3: continue
	##                        if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
	##                            self.message = parts[2]
	##                        
	##                        usernamesplit = parts[1].split("!")
	##                        self.username = usernamesplit[0]
	##
	##                        if "tmi.twitch.tv" not in self.username:
	##                            self.send_message("Ciao "+self.username+"! Questo è solo un Vodcast, ma Stockhausen_L2P torna (quasi) tutte le sere alle 20:00! PogChamp")
	##                            time.sleep(1)
	##                            self.send_message("PS: puoi comunque attaccarte a StoDiscord nel frattempo: https://goo.gl/2QSx3V KappaPride")
	##        time.sleep(10)
	##
	##        resp = requests.get(url=url, headers=params)
	##        online = json.loads(resp.text)
		'''

	def addInTimeout(self, command):
		if command in self.commandsMod.keys():
			self.timeCommandsModCalled[command] = time.time()
		elif command in self.commandsPleb.keys():
			self.timeCommandsPlebCalled[command] = time.time()

	def isInTimeout(self, command):
		if command in self.commandsMod.keys():
			if command not in self.timeCommandsModCalled or (time.time() - self.timeCommandsModCalled[command] >= float(self.commandsMod[command].getCooldown())):
				return False
			else:
				return True
		elif command in self.commandsPleb.keys():
			if command not in self.timeCommandsPlebCalled or (time.time() - self.timeCommandsPlebCalled[command] >= float(self.commandsPleb[command].getCooldown())):
				return False
			else:
				return True

	def soundAddInTimeout(self, sound):
		if sound in self.sounds.keys():
			self.timeSoundCalled[sound] = time.time()

	def soundIsInTimeout(self, sound):
		if sound in self.sounds.keys():
			print(sound+": "+self.sounds[sound].getCooldown())
			if sound not in self.timeSoundCalled or (time.time() - self.timeSoundCalled[sound] >= float(self.sounds[sound].getCooldown())):
				return False
			return True

	def call_command_mod(self):
		raffled = ""
			
		if self.message == "!restart":
			subprocess.Popen("botanaUserInterface.pyw", shell=True)
			os._exit(0)

		elif self.message == "!stop":
			self.send_message("HeyGuys")
			os._exit(0)

		elif self.message == "!clean":
			file = open("players.txt", "w")
			file.write("")
			self.players = []

		elif self.message == "!raffle":
			if len(self.players) > 3:
				raffle = random.sample(self.players, 3)
				raffled = ', '.join(raffle)
				self.players = set(self.players) - set(raffle)
			else:
				raffled = ', '.join(self.players)
				self.players = []
			self.send_message("Ho scelto "+raffled+" PogChamp")
			
		elif self.message == "!pickone":
			if len(self.players) > 0:
				raffle = random.sample(self.players, 1)
				raffled = ", ".join(raffle)
				self.send_message("Ho scelto "+raffled+" PogChamp")
			else:
				self.send_message("Non ci sono persone da scegliere BibleThump")

		elif self.message == "!comandi":
			self.send_message(self.username+", i tuoi comandi sono " + str(set(self.commandsPleb.keys())))
			time.sleep(2)
			self.send_message(self.username+", essendo un mod hai anche: " + str(set(self.commandsMod.keys()).difference(set("!comandi"))))

		elif self.message == "!suoni":
			self.get_sounds()

		elif self.message == "!addcommand":
			tmp = self.arguments.split(";")
			if (tmp[0] in self.commandsMod.keys() and tmp[3] == "mod") or (tmp[0] in self.commandsPleb.keys() and tmp[3] == "pleb"):
				self.send_message("Comando già esistente")
				return
			if (len(tmp) == 4 and len(tmp[0].split(" ")) == 1):
				fields=[tmp[0], tmp[1], tmp[2], tmp[3]]
				with open('commands.csv', 'a') as f:
					writer = csv.writer(f, delimiter=';', quotechar='|', lineterminator='\n')
					writer.writerow(fields)
				newComm = Command(tmp[0], tmp[1], tmp[2], tmp[3])
				if tmp[3] == "mod":
					self.commandsMod[tmp[0]] = newComm
				elif tmp[3] == "pleb":
					self.commandsPleb[tmp[0]] = newComm
				self.send_message("Comando " + tmp[0] + " aggiunto")
			else:
				self.send_message("impossibile aggiungere il comando " + tmp[0])

		elif self.message == "!removecommand":
			args = self.arguments.split(" ")
			if len(args) != 2:
				self.send_message("Comando errato")
				return
			exist=False
			if args[1] == "mod" and args[0] in self.commandsMod.keys():
				del self.commandsMod[args[0]]
				exist=True
			elif args[1] == "pleb" and args[0] in self.commandsPleb.keys():
				del self.commandsPleb[args[0]]
				exist=True
			if exist:
				#SAREBBE BUONO PRIMA COPIARSI TUTTO IL CONTENUTO DEL FILE CSV IN UNA VARIABILE, E IN CASO DI ECCEZIONI (CHE LASCIEREBBERO IL FILE VUOTO) RISCRIVERE IL CONTENUTO DELLA VARIABILE NEL FILE
				#OPPURE TROVARE UN'ALTRO METODO PER ELIMINARE UNA RIGA DAL FILE IN MANIERA SAFE
				f = open('commands.csv', "w+")
				f.close()
				with open('commands.csv', 'a', encoding='utf-8') as f:
					writer = csv.writer(f, delimiter=';', quotechar='|', lineterminator='\n')
					for p in self.commandsPleb.values():
						writer.writerow([p.getName(), p.getResponse(), p.getCooldown(), p.getTipo()])
					for m in self.commandsMod.values():
						writer.writerow([m.getName(), m.getResponse(), m.getCooldown(), m.getTipo()])
				self.send_message("Comando " + self.arguments + " eliminato")
			else:
				self.send_message("Comando " + self.arguments + " inesistente")
				
		else:
			for com in self.commandsMod.values():
				if com.isSimpleCommand() and self.message == com.getName():
					if not self.isInTimeout(com.getName()):
						self.addInTimeout(com.getName())
						self.send_message(com.getResponse())
					
	#Function to answer pleb command
	def call_command_pleb(self):
		if self.message == "!roulette" and not self.isInTimeout("!roulette"):
			self.addInTimeout("!roulette")
			self.send_message("Punto la pistola nella testa di "+self.username+"... monkaS")
			time.sleep(5)
			dead_or_alive = randint(1, 10)
			if dead_or_alive <= 5:
				self.send_message("Il corpo di "+self.username+" giace in chat monkaS Qualcuno può venire a pulire? LUL")
			else:
				self.send_message("La pistola si è inceppata! PogChamp "+self.username+" è sopravvissuto Kreygasm")

		elif self.message == "!salta":
			if self.username not in self.skippers:
				self.skip_count += 1
				self.skippers.append(self.username)
				if self.skip_count >= 3:
					self.skip_count = 0
					self.send_message("!songs skip")
				else:
					if len(self.skippers) == 1:
						self.send_message(self.username+" vuole saltare questa canzone LUL")
					else:
						self.send_message("Anche "+self.username+" assieme ad altri "+str(self.skip_count-1)+" vuole saltare questa canzone LUL")

		elif self.message == "!play":
			if self.username not in self.players:
				self.players.append(self.username)
				self.send_message(self.username+", ti ho aggiunto alla lista dei viewers che vogliono giocare PogChamp")

		elif self.message == "!players" and not self.isInTimeout("!players"):
			self.addInTimeout("!players")
			if self.players:
				pl = ', '.join(self.players)
				self.send_message(pl+" vogliono giocare!")
				if self.username in self.mods:
					self.players = []
			else:
				self.send_message("Non vuole giocare nessuno BibleThump")

		elif self.message == "!maledizione" and not self.isInTimeout("!maledizione"):
			self.addInTimeout("!maledizione")
			file = open("maledizioni.txt", "r")
			maled = file.read()
			count = int(maled) + 1
			file.close()

			self.send_message("Ovviamente la safe zone è dall'altra parte (x"+str(count)+" LUL) Never lucky BabyRage")

			file = open("maledizioni.txt", "w")
			file.write(str(count))

		elif self.message == "!suicidio":
			if self.username == self.NICK:
				self.send_message("Imperatore mio Imperatore, non posso permetterti di farlo! BibleThump")
				time.sleep(2)
				self.send_message("/me si è sacrificata per l'Imperatore Alessiana.")
			elif self.username in self.mods:
				self.send_message(self.username+", l'Imperatore Alessiana non ha ancora finito con te! anaLove")
			else:
				self.send_message("/timeout "+self.username+" 60")
				self.send_message(self.username+" si è suicidato monkaS Press F to pay respect BibleThump")

		elif self.message == "!8ball" and not self.isInTimeout("!8ball"):
			self.addInTimeout("!8ball")
			ball = random.choice(self.ball_choices)
			self.send_message(ball)

		elif self.message == "!love" and not self.isInTimeout("!love"):
			self.addInTimeout("!love")
			emote = ""
			rand = randint(0, 100)
			if rand < 50:
				emote = "FeelsBadMan"
			elif rand == 50:
				emote = "monkaS"
			elif rand > 50:
				emote = "PogChamp"

			if self.arguments:
				self.send_message(self.username+" ama "+self.arguments+" al "+str(rand)+"% "+emote)
			else:
				url = "https://tmi.twitch.tv/group/user/stockhausen_l2p/chatters"
				params = dict(user = "na")
				resp = requests.get(url=url, params=params)
				json_str = json.loads(resp.text)

				ret_list = []
				rand_mod = self.username
				if json_str['chatters']['moderators']:
					while rand_mod == self.username:
						rand_mod = random.choice(json_str['chatters']['moderators'])

				ret_list.append(rand_mod)

				rand_user = self.username
				if json_str['chatters']['viewers']:
					while rand_user == self.username:
						rand_user = random.choice(json_str['chatters']['viewers'])

				ret_list.append(rand_user)

				self.send_message(self.username+" ama "+random.choice(ret_list)+" al "+str(rand)+"% "+emote)

		elif self.message == "!ban" and not self.isInTimeout("!ban"):
			self.addInTimeout("!ban")
			self.send_message(self.username+" ha bandito "+self.arguments+" dalla chat PogChamp")

		elif self.message == "!comandi" and not self.isInTimeout("!comandi"):
			self.addInTimeout("!comandi")
			self.send_message(str(set(self.commandsPleb.keys())))

		elif self.message == "!suoni" and not self.isInTimeout("!suoni"):
			self.addInTimeout("!suoni")
			self.get_sounds()

		elif self.message == "!bush" and not self.isInTimeout("images"):
			self.addInTimeout("!bush")
			self.showImage("res/ShowImages/bush.png")

		else:
			for com in self.commandsPleb.values():
				if com.isSimpleCommand() and self.message == com.getName():
					if not self.isInTimeout(com.getName()):
						self.addInTimeout(com.getName())
						self.send_message(com.getResponse())

	def loadCommands(self):
		try:
			with open('commands.csv', encoding='utf-8') as commands:
				reader = csv.reader(commands, delimiter=';', quotechar='|')
				for row in reader:
					current = Command(row[0], row[1], row[2], row[3])
					if row[3] == "mod":
						self.commandsMod[row[0]] = current
					elif row[3] == "pleb":
						self.commandsPleb[row[0]] = current
			self.printMessage("commands.csv was read correctly.")
		except:
			self.printMessage("Error reading commands.csv")

	def loadSounds(self):
		try:
			with open('sounds.csv', encoding='utf-8') as sounds:
				reader = csv.reader(sounds, delimiter=';', quotechar='|')
				for row in reader:
					current = Sound(row[0], row[1])
					self.sounds[row[0]] = current
			self.printMessage("sounds.csv was read correctly.")
		except:
			self.printMessage("Error reading sounds.csv")
			file = open("LogError.txt", "a")
			file.write(time.strftime("[%d/%m/%Y - %I:%M:%S] ") + traceback.format_exc() + "\n")
			traceback.print_exc()

	#Get sounds list
	def get_sounds(self):
		self.send_message(self.username+", i suoni disponibili sono: "+str(set(self.sounds.keys())))

	def call_sound(self):
		if not self.soundIsInTimeout(self.message):
			self.soundAddInTimeout(self.message)

			pygame.mixer.pre_init(44100, 16, 2, 4096)
			pygame.mixer.init()
			sound = pygame.mixer.Sound("res/Sounds/" + self.message[1:] + ".wav")

			sound.play(0)
			clock = pygame.time.Clock()
			clock.tick(10)
			while pygame.mixer.music.get_busy():
				pygame.event.poll()
				clock.tick(10)
