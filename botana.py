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

        self.sock = socket.socket()
        self.HOST = "irc.twitch.tv"
        self.PORT = 6667
        self.botName = "BotAna__"
        self.BOT_OAUTH = ""
        self.NICK = ""
        self.CHAN = ""
        self.CLIENT_ID = ""

        self.username = ""
        self.message = ""
        self.arguments = ""

        self.RATE = 20/30

        self.mods = ["lusyoo", "boomtvmod", "botana__", "boxyes", "frankiethor", "gurzo06", "ilmarcana", "iltegame", "khaleesix90", "nightbot", "pinasu", "stockhausen_l2p", "tubbablubbah", "urza2k", "xuneera"]

        self.to_ban = ""

        self.players = []

        self.used = {}

        self.players = []

        self.ball_choices = ["Non pensarci nemmeno LUL",
                        "Ma in che pianeta vivi LUL",
                        "Ma proprio no DansGame",
                        "Ti piacerebbe Kappa",
                        "Ma ovviamente PogChamp",
                        "Vai tranqui Kreygasm"
        ]

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
            self.BOT_OAUTH = self.get_bot_oauth()
            self.NICK = self.get_nick()
            self.CHAN = "#"+self.NICK
            self.CLIENT_ID = self.get_clientID()

            self.load_commands()
            self.load_sounds()
            self.load_image()

            self.sock.connect((self.HOST, self.PORT))
            self.sock.send(bytes("PASS " + self.BOT_OAUTH + "\r\n", "UTF-8"))
            self.sock.send(bytes("NICK " + self.NICK + "\r\n", "UTF-8"))
            self.sock.send(bytes("JOIN " + self.CHAN + "\r\n", "UTF-8"))

            self.print_message("I'm now connected to "+ self.NICK + ".")

            self.check_online()

            self.send_message("Don't even worry guys, BotAna is here anaLove")

            threading.Thread(target=self.check_spam, args=()).start()
            threading.Thread(target=self.check_followers, args=()).start()

            while True:
                rec = (str(self.sock.recv(1024).decode('utf-8'))).split("\r\n")
                if rec:

                    for line in rec:
                        if "PING" in line:
                            self.sock.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))
                        else:
                            parts = line.split(':')
                            if len(parts) < 3: continue
                            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
                                self.message = parts[2]

                            usernamesplit = parts[1].split("!")
                            self.username = usernamesplit[0]

                            if "tmi.twitch.tv" in self.username:
                                continue

                            self.msg_count += 1

                            self.print_message(self.username+": "+self.message)

                            if sum(1 for c in self.message if c.isupper()) > 15:
                                self.check_ban()

                            if set(self.greetings).intersection(set(list(self.message.lower().split(' ')))):
                                if self.username not in self.greeted:
                                    self.greeted.append(self.username)
                                    self.send_message("Ciao, "+self.ana(self.username)+"! KappaPride")

                            elif self.message.startswith('!'):
                                message_list = self.message.split(' ');

                                self.message = message_list[0]

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

                time.sleep(1/self.RATE)
        except:
            self.play_sound("crash")
            self.print_message("----SI E' VERIFICATO UN ERRORE, TI PREGO RIAVVIAMI CON IL BOTTONE APPOSITO-----")
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()

    def __del__(self):
        self.exiting = True
        self.wait()

    def show_image(self, path):
        self.sign2.emit(path)

    def print_message(self, msg):
        print(msg)
        self.sign.emit(time.strftime("%H:%M  ")+msg)

    def read_config_file(self, path):
        if os.path.exists(path):
            try:
                with open(path,"r") as f:
                    tmp = f.read()
                    self.print_message(path + " was read correctly.")
                    return tmp
            except:
                self.print_message("Error opening " + path + "\n")
        else:
            self.print_message("Error reading " + path + "\n")

    def get_bot_oauth(self):
        return self.read_config_file("bot_OAuth.txt")

    def get_nick(self):
        return self.read_config_file("username.txt")

    def get_clientID(self):
        return self.read_config_file("clientID.txt")

    def send_message(self, message):
        self.sock.send(bytes("PRIVMSG "+self.CHAN+" :"+str(message)+"\r\n", 'utf-8'))
        self.print_message(self.botName + ": " + str(message))

    def send_whisper(self, message):
        self.sock.send(bytes("PRIVMSG #botana__ :/w "+self.username+" "+message+"\r\n", "UTF-8"))

    def check_ban(self):
        if self.username not in self.mods:
            if self.username == to_ban:
                self.send_message("/timeout "+self.username+" 5")
            else:
                to_ban = self.username
                self.send_message(self.username+", hai davvero bisogno di tutti queli caps? <warning>")

    def check_online(self):
        #Momentaneamente commentata per far credere al bot che il canale è live
        '''
        offline = True
        url = "https://api.twitch.tv/kraken/streams/"+self.NICK+""
        params = {"Client-ID" : ""+self.CLIENT_ID+""}
        resp = requests.get(url=url, headers=params)
        online = json.loads(resp.text)
        #Check if stream is offline or is a Vodcast
        while online["stream"] == None or online["stream"]["stream_type"] == "watch_party":
            #It's a vodcast
            if online["stream"]:
                if online["stream"]["stream_type"] == "watch_party":
                    #Get user message
                    rec = str(self.sock.recv(1024)).split("\\r\\n")
                    if rec:
                        for line in rec:
                            parts = line.split(':')
                            if len(parts) < 3: continue
                            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
                                self.message = parts[2]

                            usernamesplit = parts[1].split("!")
                            self.username = usernamesplit[0]

                            if "tmi.twitch.tv" not in self.username:
                                self.send_message("Ciao "+self.username+"! Questo è solo un Vodcast, ma Stockhausen_L2P torna (quasi) tutte le sere alle 20:00! PogChamp")
                                time.sleep(1)
                                self.send_message("PS: puoi comunque attaccarte a StoDiscord nel frattempo: https://goo.gl/2QSx3V KappaPride")
            time.sleep(10)

            resp = requests.get(url=url, headers=params)
            online = json.loads(resp.text)
        '''

    def check_followers(self):
        tempo = time.time()
        url = "https://api.twitch.tv/kraken/channels/"+self.NICK+"/follows"
        params = {"Client-ID" : ""+ self.CLIENT_ID +""}

        #First followers list pull
        resp = requests.get(url = url, headers = params)
        first = json.loads(resp.text)

        while True:
            self.print_message("Checking for new followers...")
            resp = requests.get(url=url, headers=params)
            new = json.loads(resp.text)

            #Ora ho due liste di oggetti "follows"
            inter = set(set(first).difference(set(new)))
            for i in inter:
                self.send_message(inter["user"]["display_name"]+"! Benvenuto nella FamigliANA PogChamp Grazie del follow anaLove Mucho appreciato FeelsAmazingMan")
                new.append(inter["user"])

            time.sleep(30)

    def check_spam(self):
        tempo = time.time()
        index = 0
        while True:
            if time.time() - tempo > 900 and self.msg_count > 15:
                self.send_message(self.msg_spam[index])
                tempo = time.time()
                self.msg_count = 0
                index = (index + 1) % len(self.msg_spam)

            time.sleep(1)

    def add_in_timeout(self, command):
        if command in self.commandsMod.keys():
            self.timeCommandsModCalled[command] = time.time()
        elif command in self.commandsPleb.keys():
            self.timeCommandsPlebCalled[command] = time.time()

    def is_in_timeout(self, command):
        if command in self.commandsMod.keys():
            if command not in self.timeCommandsModCalled or (time.time() - self.timeCommandsModCalled[command] >= float(self.commandsMod[command].get_cooldown())):
                return False
            return True
        elif command in self.commandsPleb.keys():
            if command not in self.timeCommandsPlebCalled or (time.time() - self.timeCommandsPlebCalled[command] >= float(self.commandsPleb[command].get_cooldown())):
                return False
            return True

    def sound_add_in_timeout(self, sound):
        if sound in self.sounds.keys():
            self.timeLastSoundCalled = time.time()

    def sound_is_in_timeout(self, sound):
        if sound in self.sounds.keys():
            if self.timeLastSoundCalled == None or (time.time() - self.timeLastSoundCalled >= float(self.cooldownSound)):
                return False
        return True

    def image_add_in_timeout(self, img):
        if img in self.images.keys():
            self.timeLastImageCalled = time.time()

    def image_is_in_timeout(self, img):
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
            if ((len(tmp) == 4 or len(tmp) == 5) and len(tmp[0].split(" ")) == 1):
                if len(tmp) == 4:
                    fields=[tmp[0], tmp[1], tmp[2], tmp[3]]
                    newComm = Command(tmp[0], tmp[1], tmp[2], tmp[3])
                elif len(tmp) == 5:
                    fields=[tmp[0], tmp[1], tmp[2], tmp[3], tmp[4]]
                    newComm = Command(tmp[0], tmp[1], tmp[2], tmp[3], tmp[4])
                with open('commands.csv', 'a') as f:
                    writer = csv.writer(f, delimiter=';', quotechar='|', lineterminator='\n')
                    writer.writerow(fields)
                if tmp[3] == "mod":
                    self.commandsMod[tmp[0]] = newComm
                elif tmp[3] == "pleb":
                    self.commandsPleb[tmp[0]] = newComm
                self.send_message("Ho aggiunto il comando " + tmp[0] + " FeelsGoodMan")
            else:
                self.send_message("Uso: !comando;risposta;cooldown;permessi(pleb/mod);gioco(opzionale)")

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
                        writer.writerow([p.get_name(), p.get_response(), p.get_cooldown(), p.get_tipo()])
                    for m in self.commandsMod.values():
                        writer.writerow([m.get_name(), m.get_response(), m.get_cooldown(), m.get_tipo()])
                self.send_message("Comando " + self.arguments + " eliminato FeelsGoodMan")
            except:
                subprocess.run("del commands.csv", shell=True)
                subprocess.run("ren commands_bkp.csv commands.csv", shell=True)
                self.send_message("Impossibile eliminare il comando " + self.arguments+" FeelsBadMan")
            subprocess.run("del commands_bkp.csv", shell=True)

        else:
            for com in self.commandsMod.values():
                if com.is_simple_command() and self.message == com.get_name():
                    if not self.is_in_timeout(com.get_name()):
                        self.add_in_timeout(com.get_name())
                        self.send_message(com.get_response())

    def start_roulette(self, user):
        self.add_in_timeout("!roulette")
        self.send_message("Punto la pistola nella testa di "+user+"... monkaS")
        time.sleep(5)
        dead_or_alive = randint(1, 10)
        if dead_or_alive <= 5:
            self.send_message("Il corpo di "+user+" giace in chat monkaS Qualcuno può venire a pulire? LUL")
        else:
            self.send_message("La pistola si è inceppata! PogChamp "+user+" è sopravvissuto Kreygasm")

    def start_suicidio(self, user):
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

    def get_stats(self, user):
        PLATFORM = "pc"
        URL = "https://fortnitetracker.com/profile/"+PLATFORM+"/"+user
        try:
            resp = requests.get(URL)
            player_data = json.loads(self.find(resp.text, 'var playerData = ', ';</script>'))
            self.send_message("["+user+"] Solo: "+player_data['p2'][0]['value']+", Duo: "+player_data['p10'][0]['value']+", Squad: "+player_data['p9'][0]['value']+" KappaPride")
        except:
            self.send_message("Utente <"+user+"> non trovato. Scrivi bene, stupido babbuino LUL")

    #Copiato brutalmente, cerca nella pagina
    def find(self, s, first, last):
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]

    def call_command_pleb(self):
        if self.message == "!wins" and not self.is_in_timeout("!wins"):
            if self.arguments:
                threading.Thread(target=self.get_stats, args=([self.arguments])).start()
            else:
                threading.Thread(target=self.get_stats, args=(["lidfrid"])).start()

        elif self.message == "!roulette" and not self.is_in_timeout("!roulette"):
            threading.Thread(target=self.start_roulette, args=(self.username)).start()

        elif self.message == "!salta":
            if len(self.skippers) == 0 or time.time() - self.timeSkip > 60:
                del self.skippers[:]
                self.timeSkip = time.time()
                self.skippers.append(self.username)
                self.send_message(self.username+" vuole saltare questa canzone LUL")

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

        elif self.message == "!players" and not self.is_in_timeout("!players"):
            self.add_in_timeout("!players")
            if self.players:
                pl = ', '.join(self.players)
                self.send_message(pl+" vogliono giocare!")
                if self.username in self.mods:
                    self.players = []
            else:
                self.send_message("Non vuole giocare nessuno BibleThump")

        elif self.message == "!maledizione" and not self.is_in_timeout("!maledizione"):
            self.add_in_timeout("!maledizione")
            file = open("maledizioni.txt", "r")
            maled = file.read()
            count = int(maled) + 1
            file.close()

            self.send_message("Ovviamente la safe zone è dall'altra parte (x"+str(count)+" LUL) Never lucky BabyRage")

            file = open("maledizioni.txt", "w")
            file.write(str(count))

        elif self.message == "!suicidio":
            threading.Thread(target=self.start_suicidio, args=([self.username])).start()

        elif self.message == "!8ball" and not self.is_in_timeout("!8ball"):
            self.add_in_timeout("!8ball")
            ball = random.choice(self.ball_choices)
            self.send_message(ball)

        elif self.message == "!love" and not self.is_in_timeout("!love"):
            if self.username == "lusyoo" and self.arguments.lower() == "dio":
                self.send_message(self.username+" ama "+self.arguments+" allo 0% FeelsBadMan")
                return
            self.add_in_timeout("!love")
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

        elif self.message == "!ban" and not self.is_in_timeout("!ban"):
            self.add_in_timeout("!ban")
            self.send_message(self.username+" ha bandito "+self.arguments+" dalla chat PogChamp")

        elif self.message == "!comandi" and not self.is_in_timeout("!comandi"):
            self.add_in_timeout("!comandi")
            self.send_message(str(set(self.commandsPleb.keys())))

        elif self.message == "!suoni" and not self.is_in_timeout("!suoni"):
            self.add_in_timeout("!suoni")
            self.get_sounds()

        else:
            for com in self.commandsPleb.values():
                if com.is_simple_command() and self.message == com.get_name() and self.is_for_current_game(com):
                    if not self.is_in_timeout(com.get_name()):
                        self.add_in_timeout(com.get_name())
                        self.send_message(com.get_response())

    def ana(self, user):
        new = ""

        if user.endswith("ana"):
            new = user[:-3]
        else:
            lun = (len(user))-1
            last = user[lun]
            while last not in "bcdfghjklmnpqrstvwxyz":
                lun = lun -1
                last = user[lun]
                print(last)

            new = user[:lun+1]
            print(new)

        return new + "ANA";

    def word_in_timeout(self, word):
        self.words_cooldown[word] = time.time()

    def is_word_in_timeout(self, word):
        if word not in self.words_cooldown.keys() or (time.time() - self.words_cooldown[word] >= 15):
            return False
        return True

    def check_words(self, message):
        if "classic" in message.lower() and not self.is_word_in_timeout("classic"):
            self.word_in_timeout("classic")
            self.send_message("CLASSIC LUL")

        elif "anche io" in message.lower() and not self.is_word_in_timeout("anche io"):
            self.word_in_timeout("anche io")
            self.send_message("Anche io KappaPride")

    def load_commands(self):
        with open('commands.csv', encoding='utf-8') as commands:
            reader = csv.reader(commands, delimiter=';', quotechar='|')
            for row in reader:
                if len(row) == 5:
                    current = Command(row[0], row[1], row[2], row[3], row[4])
                else:
                    current = Command(row[0], row[1], row[2], row[3])
                if row[3] == "mod":
                    self.commandsMod[row[0]] = current
                elif row[3] == "pleb":
                    self.commandsPleb[row[0]] = current
        self.print_message("commands.csv was read correctly.")

    def load_image(self):
        with open('images.csv', encoding='utf-8') as imgs:
            reader = csv.reader(imgs, delimiter=';', quotechar='|')
            for row in reader:
                if len(row) == 4:
                    current = Image(row[0], row[1], row[2], row[3])
                else:
                    current = Image(row[0], row[1], row[2])
                self.images[row[0]] = current
        self.print_message("images.csv was read correctly.")

    def load_sounds(self):
        with open('sounds.csv', encoding='utf-8') as sounds:
            reader = csv.reader(sounds, delimiter=';', quotechar='|')
            for row in reader:
                if len(row) == 2:
                    current = Sound(row[0], row[1])
                else:
                    current = Sound(row[0])
                self.sounds[row[0]] = current
        self.print_message("sounds.csv was read correctly.")

    def get_sounds(self):
        self.send_message(self.username+", i suoni disponibili sono: "+str(set(self.sounds.keys())))

    def call_image(self, name):
        for img in self.images.values():
            if name == img.get_name() and not self.image_is_in_timeout(name) and self.is_for_current_game(self.images[name]):
                self.image_add_in_timeout(name)
                self.send_message("Pro strats PogChamp")
                self.show_image(img.get_message())

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
            self.sound_add_in_timeout(name)
            self.play_sound(sname)
        elif not self.sound_is_in_timeout(name) and self.is_for_current_game(self.sounds[sname]):
            self.sound_add_in_timeout(name)
            self.play_sound(sname)

    def is_for_current_game(self, command):
        if not command.is_for_specific_game():
            return True
        curr_game = "va visto come fare"
        if command.get_game() == curr_game:
            return True
        return False
