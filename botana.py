#Main application file

#Useful imports
import socket, time, json, requests, datetime, command, os, traceback, subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

class BotAna(QtCore.QThread):
    sign = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        #First, we need to create the socket to connect to the chat
        self.sock = socket.socket()
        #Twitch Host, always this
        self.HOST = "irc.twitch.tv"
        #Twitch port, always this
        self.PORT = 6667
        #Bot OAuth
        self.BOT_OAUTH = ""
        #NICK and CHAN are basically the same, but CHAN comes with a "#" before the channel name
        #Channel name
        self.NICK = ""
        #Channel to join
        self.CHAN = ""
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
        self.mods = ["lusyoo", "boomtvmod", "botana__", "boxyes", "frankiethor", "gurzo06", "ilmarcana", "iltegame", "khaleesix90", "moobot", "nightbot", "pinasu", "revlobot", "stockazzobot", "stockhausen_l2p", "tubbablubbah", "urza2k", "vivbot", "xuneera"]
        #Chatter to ban, he's screaming too much.
        self.to_ban = ""
        #Mod commands
        self.mods_commands = dict()
        #Bot control
        self.mods_commands ["!restart"] = ""
        self.mods_commands ["!stop"] = ""
        #Raffle related commands
        self.mods_commands ["!clean" ] = ""
        self.mods_commands ["!raffle"] = ""
        self.mods_commands ["!pickone"] = ""
        #Warns a user if he's being a dick
        self.mods_commands ["!warn"] = ""
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
        #Trick random
        self.old_ball = ""

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
            
            #Chat connection
            self.sock.connect((self.HOST, self.PORT))

            #Send to Twitch some usefuli nformations
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
                            s.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))
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
                                if self.message in self.mods_commands:
                                    self.call_command_mod()
                                else:
                                    self.process_command_pleb()

                #Prevent Bot to use too much CPU
                time.sleep(1/self.RATE)
        except:
            self.printMessage("----------SI E' VERIFICATO UN ERRORE, TI PREGO RIAVVIAMI----------")
            traceback.print_exc()

    def __del__(self):
        self.exiting = True
        self.wait()

    def printMessage(self, msg):
        print(msg)
        self.sign.emit(msg)

    def readConfigFile(self, path):
        if os.path.exists(path):
            with open(path,"r") as f:
                try:
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
        self.printMessage("BotAna_: " + message)

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
        """Momentaneamente commentata per far credere al bot che il canale è live"""
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
    ##                            time.sleep(300)
    ##
    ##        resp = requests.get(url=url, headers=params)
    ##        online = json.loads(resp.text)
    ##
    ##        #Stockhausen always stream at 20, set for how much time will the Bot sleep
    ##        if datetime.datetime.now().strftime('%H') == "19":
    ##            offline = False
    ##
    ##        if offline:
    ##            time.sleep(900)
    ##        else:
    ##            time.sleep(300)

    #Function to answer mod command
    def call_command_mod(self):
        if self.username not in self.mods:
            self.send_message("Mi dispiace, ma questo comando non è per te.")
        else:
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
                        send_message("Ho scelto "+raffled+" PogChamp")
                    else:
                        send_message("Non ci sono persone da scegliere BibleThump")

                elif self.message == "!comandi":
                    cmd = self.username+", i comandi disponibili sono [ "
                    #Commands for everyone
                    for r in self.commands:
                        cmd+="'"+p+", "
                    for r in self.mods_commands:
                        #Last command in the dict?
                        if list(self.commands.keys())[-1] == p:
                            cmd+="'"+p+"' "
                        else:
                            cmd+="'"+p+", "
                    self.send_message(cmd+" ]")

                elif self.message == "!suoni":
                    self.get_sounds()

    #Function to check if message is in cooldown
    def process_command_pleb(self):
        if self.message not in self.used or time.time()-self.used[command] > self.command_coold:
            if command != "!play" and command != "!energia":
                self.used[command] = time.time()
            self.call_command_pleb()

    #Function to answer pleb command
    def call_command_pleb(self):
        if self.message == "!roulette":
            send_message("Punto la pistola nella testa di "+self.username+"... monkaS")
            time.sleep(5)
            doa = randint(1, 10)
            if doa <= 5:
                self.send_message("Il corpo di "+self.username+" giace in chat monkaS Qualcuno può venire a pulire? LUL")
            else:
                self.send_message("La pistola si è inceppata! PogChamp "+self.username+" è sopravvissuto Kreygasm")

        elif self.message == "!play":
            if self.username not in self.players:
                self.players.append(self.username)
                self.send_message(self.username+", ti ho aggiunto alla lista dei viewers che vogliono giocare PogChamp")

        elif self.message == "!players":
            if self.players:
                pl = ', '.join(self.players)
                self.send_message(pl+" vogliono giocare!")
                if self.username in mods:
                    self.players = []
            else:
                self.send_message("Non vuole giocare nessuno BibleThump")

        elif self.message == "maledizione":
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
            elif self.username in self.mods:
                self.send_message(self.username+", l'Imperatore Alessiana non ha ancora finito con te! anaLove")
            else:
                self.send_message("/timeout "+self.username+" 60")
                self.send_message(self.username+" si è suicidato monkaS Press F to pay respect BibleThump")

        elif self.message == "!8ball":
            new_ball = random.choice(self.ball_choices)

            #Alessiana rompeva le palle ogni volta che usciva due volte la stessa
            while new_ball == self.old_ball:
                new_ball = random.choice(self.ball_choices)

            self.send_message(new_ball)
            self.old_ball = new_ball

        elif self.message == "!ban":
            self.send_message(self.username+" ha bannato "+self.arguments+" PogChamp")

        elif self.message == "!suoni":
            self.get_sounds()

    def get_pleb_commands(self):
        command_list = []
        with open('commands.csv') as commands:
            reader = csv.reader(commands, delimiter=';', quotechar='|')
            for row in reader:
                current = Command(row[0], row[1], row[2])
                command_list.append(current)
            
            for current in command_list:
                print(current.command+", "+current.response+", "+current.cooldown)
        return commands

    #Get sounds list
    def get_sounds(self):
        self.send_message(self.username+", i suoni disponibili sono "+str(self.sounds))



