#Main application file

#Useful imports
import socket, time, json, requests, datetime, command, os, traceback, subprocess, random, csv, pygame
from pygame import mixer
from random import randint
from command import Command
from image import Image
from sound import Sound
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import threading

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
        self.timeLastSoundCalled = None
        self.cooldownSound = 20

        self.images = dict()
        self.timeLastImageCalled = None
        self.cooldownImage = 20

        self.skippers = []
        self.timeSkip = 0

        self.greetings = ["ciao", "buonasera", "buongiono", "salve"]
        self.greeted = []

        self.words_cooldown = dict()

        self.msg_count = 0

        self.msg_spam = ["Attaccate a StoDiscord https://goo.gl/2QSx3V KappaPride",
        				"Se vuoi supportare il canale... Attaccate a Stockhausen, clicca sul Follow. CLASSIC PogChamp",
        				"Io sono BotAna, per i miei comandi digita !comandi PogChamp",
			            "Se vedi messaggi del tipo anaLove , FeelsBadMan o monkaS e pensi che la gente sia impazzita, probabilmente non hai BetterTTV: https://goo.gl/hx75Jf 4Head",
        				"Vuoi giocare con noi? Usa il comando !play! KappaPride"
    					]

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
            self.loadImage()

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
            self.send_message("Don't even worry guys, BotAna is here anaLove")

            threading.Thread(target=self.check_spam, args=()).start()

            #Bot main while loop
            while True: #"while 1" if you prefere *lennyface*
                #Get Twitch chat current message
                rec = (str(self.sock.recv(1024).decode('utf-8'))).split("\r\n")
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
                            #messo qui il counter conta anche messaggi iniziali (di handshake) che non sono di un utente...
                            #... che in teoria non dovrebbero essere tenuti in conto qui...
                            self.msg_count += 1
                            usernamesplit = parts[1].split("!")
                            self.username = usernamesplit[0]

                            #Print to stdout user's nick and message
                            self.printMessage(self.username+": "+self.message)

                            #Check user message, if he's screaming he'll be warned by bot or banned
                            if sum(1 for c in self.message if c.isupper()) > 15:
                                self.check_ban()

                            if set(self.greetings).intersection(set(list(self.message.lower().split(' ')))):
                                if self.username not in self.greeted:
                                    self.greeted.append(self.username)
                                    self.send_message("Ciao, "+self.ana(self.username)+"! KappaPride")

                            #Message is a command
                            elif self.message.startswith('!'):
                                message_list = self.message.split(' ');

                                #Get command from messages
                                self.message = message_list[0]

                                #Get message arguments, if there are any
                                self.arguments = ' '.join(message_list[1:])

                                if self.message in self.commandsMod.keys() and self.username in self.mods:
                                    self.call_command_mod()
                                else:
                                    self.call_command_pleb()

                                if self.message in self.sounds.keys():
                                    self.call_sound(self.message)
                                elif self.message in self.images.keys():
                                    self.call_image(self.message)

                            self.check_words(self.message)

                #Prevent Bot to use too much CPU
                time.sleep(1/self.RATE)
        except:
            self.play_sound("crash")
            self.printMessage("----SI E' VERIFICATO UN ERRORE, TI PREGO RIAVVIAMI CON IL BOTTONE APPOSITO-----")
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()

    def __del__(self):
        self.exiting = True
        self.wait()

    def showImage(self, path):
        self.sign2.emit(path)

    def printMessage(self, msg):
        print(msg)
        self.sign.emit(time.strftime("%H:%M  ")+msg)

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
        self.sock.send(bytes("PRIVMSG "+self.CHAN+" :"+str(message)+"\r\n", 'utf-8'))
        self.printMessage(self.botName + ": " + str(message))

    #Function to send whisper to user
    #Watch out, if you abuse using whispers Twitch will ban your Bot's account
    def send_whisper(self, message):
        self.sock.send(bytes("PRIVMSG #botana__ :/w "+self.username+" "+message+"\r\n", "UTF-8"))

    #Function to check if user needs to be banned
    def check_ban(self):
        if self.username not in self.mods:
            if self.username == to_ban:
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

    def check_spam(self):
        tempo = time.time()
        index = 0
        while True:
            print(str(int(time.time() - tempo)) + " - " + str(self.msg_count))
            if time.time() - tempo > 900 and self.msg_count > 15:
                self.send_message(self.msg_spam[index])
                tempo = time.time()
                self.msg_count = 0
                index = (index + 1) % len(self.msg_spam)
                '''
                if index == len(self.msg_spam):
                    index = 0
                else:
                    index += 1'''
            time.sleep(1)

    def addInTimeout(self, command):
        if command in self.commandsMod.keys():
            self.timeCommandsModCalled[command] = time.time()
        elif command in self.commandsPleb.keys():
            self.timeCommandsPlebCalled[command] = time.time()

    def isInTimeout(self, command):
        if command in self.commandsMod.keys():
            if command not in self.timeCommandsModCalled or (time.time() - self.timeCommandsModCalled[command] >= float(self.commandsMod[command].getCooldown())):
                return False
            return True
        elif command in self.commandsPleb.keys():
            if command not in self.timeCommandsPlebCalled or (time.time() - self.timeCommandsPlebCalled[command] >= float(self.commandsPleb[command].getCooldown())):
                return False
            return True

    def soundAddInTimeout(self, sound):
        if sound in self.sounds.keys():
            self.timeLastSoundCalled = time.time()

    def soundIsInTimeout(self, sound):
        if sound in self.sounds.keys():
            if self.timeLastSoundCalled == None or (time.time() - self.timeLastSoundCalled >= float(self.cooldownSound)):
                return False
        return True

    def imageAddInTimeout(self, img):
        if img in self.images.keys():
            self.timeLastImageCalled = time.time()

    def imageIsInTimeout(self, img):
        if img in self.images.keys():
            if self.timeLastImageCalled == None or (time.time() - self.timeLastImageCalled >= float(self.cooldownImage)):
                return False
        return True

    def restart(self):
        subprocess.Popen("botanaUserInterface.pyw", shell=True)
        os._exit(0)

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
            self.send_whisper(self.username+", essendo un mod hai anche: " + str(set(self.commandsMod.keys())))

        elif self.message == "!suoni":
            self.get_sounds()

        elif self.message == "!addcommand":
            tmp = self.arguments.split(";")
            if (tmp[0] in self.commandsMod.keys() and tmp[3] == "mod") or (tmp[0] in self.commandsPleb.keys() and tmp[3] == "pleb"):
                self.send_message("Non posso aggiungere un comando uguale a uno che esiste già, stupido babbuino LUL")
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
                self.send_message("Ho aggiunto il comando " + tmp[0] + " FeelsGoodMan")
            else:
                self.send_message("Uso: !comando;risposta;cooldown;permessi(pleb/mod)")

        elif self.message == "!removecommand":
            args = self.arguments.split(" ")
            if len(args) == 1 and args[0]== "":
                self.send_message("Devi specificarmi quale comando eliminare, stupido babbuino LUL")
                return

            if len(args) == 1 or args[1] == "pleb":
                if args[0] in self.commandsPleb.keys(): #Pleb command
                    del self.commandsPleb[args[0]]
                else:
                    self.send_message("Il comando " + args[0] + " (pleb) non esiste, scrivi bene stupido babbuino LUL")
                    return

            elif len(args) == 2 and  args[1] == "mod":
                if args[0] in self.commandsMod.keys(): #Mod command
                    del self.commandsMod[args[0]]
                else:
                    self.send_message("Il comando " + args[0] + " (mod) non esiste, scrivi bene stupido babbuino LUL")
                    return

            else:
                self.send_message("Uso: !removecommand !comando mod(opzionale)")
                return

            subprocess.run("copy commands.csv commands_bkp.csv", shell=True)
            f = open('commands.csv', "w+")
            f.close()
            try:
                with open('commands.csv', 'a', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';', quotechar='|', lineterminator='\n')
                    for p in self.commandsPleb.values():
                        writer.writerow([p.getName(), p.getResponse(), p.getCooldown(), p.getTipo()])
                    for m in self.commandsMod.values():
                        writer.writerow([m.getName(), m.getResponse(), m.getCooldown(), m.getTipo()])
                self.send_message("Comando " + self.arguments + " eliminato FeelsGoodMan")
            except:
                subprocess.run("del commands.csv", shell=True)
                subprocess.run("ren commands_bkp.csv commands.csv", shell=True)
                self.send_message("Impossibile eliminare il comando " + self.arguments+" FeelsBadMan")
            subprocess.run("del commands_bkp.csv", shell=True)

        else:
            for com in self.commandsMod.values():
                if com.isSimpleCommand() and self.message == com.getName():
                    if not self.isInTimeout(com.getName()):
                        self.addInTimeout(com.getName())
                        self.send_message(com.getResponse())

    def startRoulette(self, user):
        self.addInTimeout("!roulette")
        self.send_message("Punto la pistola nella testa di "+user+"... monkaS")
        time.sleep(5)
        dead_or_alive = randint(1, 10)
        if dead_or_alive <= 5:
            self.send_message("Il corpo di "+user+" giace in chat monkaS Qualcuno può venire a pulire? LUL")
        else:
            self.send_message("La pistola si è inceppata! PogChamp "+user+" è sopravvissuto Kreygasm")

    def startSuicidio(self, user):
        if user == self.NICK:
            self.send_message("Imperatore mio Imperatore, non posso permetterti di farlo! BibleThump")
            time.sleep(2)
            self.send_message("/me si è sacrificata per l'Imperatore Alessiana.")
        elif user in self.mods:
            self.send_message(user+", l'Imperatore Alessiana non ha ancora finito con te! anaLove")
        else:
            self.send_message("/timeout "+user+" 60")
            self.send_message(user+" si è suicidato monkaS Press F to pay respect BibleThump")

    def perform_love(self, username, rand, emote):
        url = "https://tmi.twitch.tv/group/user/stockhausen_l2p/chatters"
        params = dict(user = "na")

        try:
            resp = requests.get(url=url, params=params, timeout=10)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as err:
            self.send_message("Mi dispiace "+self.username+", ma tu non amerai nessuno oggi FeelsBadMan")
            return

        json_str = json.loads(resp.text)
        ret_list = []
        rand_mod = username
        if json_str['chatters']['moderators']:
            while rand_mod == username:
                rand_mod = random.choice(json_str['chatters']['moderators'])

        ret_list.append(rand_mod)

        rand_user = username
        if json_str['chatters']['viewers']:
            while rand_user == username:
                rand_user = random.choice(json_str['chatters']['viewers'])

        ret_list.append(rand_user)

        self.send_message(username+" ama "+random.choice(ret_list)+" al "+str(rand)+"% "+emote)

    #Function to answer pleb command
    def call_command_pleb(self):
        if self.message == "!roulette" and not self.isInTimeout("!roulette"):
            threading.Thread(target=self.startRoulette, args=(self.username)).start()

        elif self.message == "!salta":

            #Se è il primo a voler skippare oppure se sono passati 60 secondi dall'ultimo skip
            if len(self.skippers) == 0 or time.time() - self.timeSkip > 60:
                del self.skippers[:]
                self.timeSkip = time.time()
                self.skippers.append(self.username)
                self.send_message(self.username+" vuole saltare questa canzone LUL")

            #L'utente non ha già chiamato skip
            elif self.username not in self.skippers:
                self.skippers.append(self.username)
                if len(self.skippers) == 3:
                    self.send_message(str(len(self.skippers))+" persone vogliono saltare questa canzone PogChamp")
                    self.send_message("!songs skip")
                    del self.skippers[:]
                else:
                    self.send_message("Anche "+self.username+" assieme ad altri "+str(len(self.skippers) - 1)+" vuole saltare questa canzone LUL")

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
            threading.Thread(target=self.startSuicidio, args=([self.username])).start()

        elif self.message == "!8ball" and not self.isInTimeout("!8ball"):
            self.addInTimeout("!8ball")
            ball = random.choice(self.ball_choices)
            self.send_message(ball)

        elif self.message == "!love" and not self.isInTimeout("!love"):
            if self.username == "lusyoo" and self.arguments.lower() == "dio":
                self.send_message(self.username+" ama "+self.arguments+" allo 0% FeelsBadMan")
                return
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
                threading.Thread(target=self.perform_love, args=(self.username, rand, emote)).start()

        elif self.message == "!ban" and not self.isInTimeout("!ban"):
            self.addInTimeout("!ban")
            self.send_message(self.username+" ha bandito "+self.arguments+" dalla chat PogChamp")

        elif self.message == "!comandi" and not self.isInTimeout("!comandi"):
            self.addInTimeout("!comandi")
            self.send_message(str(set(self.commandsPleb.keys())))

        elif self.message == "!suoni" and not self.isInTimeout("!suoni"):
            self.addInTimeout("!suoni")
            self.get_sounds()

        else:
            for com in self.commandsPleb.values():
                if com.isSimpleCommand() and self.message == com.getName():
                    if not self.isInTimeout(com.getName()):
                        self.addInTimeout(com.getName())
                        self.send_message(com.getResponse())

    def ana(self, user):
        new = ""

        if user.endswith("ana"):
            new = user[:-3]
        else:
            #Pinasu
            lun = (len(user))-1
            last = user[lun]
            while last not in "bcdfghjklmnpqrstvwxyz":
                lun = lun -1
                last = user[lun]
                print(last)

            new = user[:lun+1]
            print(new)

        return new + "ANA";

    def wordInTimeout(self, word):
        self.words_cooldown[word] = time.time()

    def isWordInTimeout(self, word):
        if word not in self.words_cooldown.keys() or (time.time() - self.words_cooldown[word] >= 15):
            return False
        return True

    def check_words(self, message):
        if "classic" in message.lower() and not self.isWordInTimeout("classic"):
            self.wordInTimeout("classic")
            self.send_message("CLASSIC LUL")

        elif "anche io" in message.lower() and not self.isWordInTimeout("anche io"):
            self.wordInTimeout("anche io")
            self.send_message("Anche io KappaPride")

    def loadCommands(self):
        with open('commands.csv', encoding='utf-8') as commands:
            reader = csv.reader(commands, delimiter=';', quotechar='|')
            for row in reader:
                current = Command(row[0], row[1], row[2], row[3])
                if row[3] == "mod":
                    self.commandsMod[row[0]] = current
                elif row[3] == "pleb":
                    self.commandsPleb[row[0]] = current
        self.printMessage("commands.csv was read correctly.")

    def loadImage(self):
        with open('images.csv', encoding='utf-8') as imgs:
            reader = csv.reader(imgs, delimiter=';', quotechar='|')
            for row in reader:
                current = Image(row[0], row[1], row[2])
                self.images[row[0]] = current
        self.printMessage("images.csv was read correctly.")

    def loadSounds(self):
        with open('sounds.csv', encoding='utf-8') as sounds:
            reader = csv.reader(sounds, delimiter=';', quotechar='|')
            for row in reader:
                current = Sound(row[0])
                self.sounds[row[0]] = current
        self.printMessage("sounds.csv was read correctly.")

    #Get sounds list
    def get_sounds(self):
        self.send_message(self.username+", i suoni disponibili sono: "+str(set(self.sounds.keys())))

    def call_image(self, name):
        for img in self.images.values():
            if name == img.getName() and not self.imageIsInTimeout(name):
                self.imageAddInTimeout(name)
                self.send_message("Pro strats PogChamp")
                self.showImage(img.getMessage())

    def play_sound(self, name):
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.mixer.init()

        sound = pygame.mixer.Sound("res/Sounds/" + name + ".wav")

        sound.play(0)
        clock = pygame.time.Clock()
        clock.tick(10)
        while pygame.mixer.music.get_busy():
            pygame.event.poll()
            clock.tick(10)

    def call_sound(self, name):
        if name[:1] == "!":
                sname = name[1:]
        if name == "!gg":
            self.soundAddInTimeout(name)
            self.play_sound(sname)
        elif not self.soundIsInTimeout(name):
            self.soundAddInTimeout(name)
            self.play_sound(sname)
