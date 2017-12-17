import socket, time, json, requests, datetime, command, os, traceback, subprocess, random, csv, pygame, threading
import pythoncom
import win32com.client as wincl
from pygame import mixer
from random import randint
from command import Command
from image import Image
from sound import Sound
from quote import Quote
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

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
        self.USER_ID = ""

        self.username = ""
        self.message = ""
        self.arguments = ""

        self.RATE = 20/30

        self.mods = ["lusyoo", "boomtvmod", "botana__", "boxyes", "frankiethor", "gurzo06", "ilmarcana", "iltegame", "khaleesix90", "moobot", "nightbot", "pinasu", "revlobot", "stockazzobot", "stockhausen_l2p", "tubbablubbah", "urza2k", "vivbot", "xuneera"]

        self.to_ban = ""

        self.players = []

        self.used = {}

        self.players = []

        self.ball_choices = [
                        "Ma certo che si KappaPride",
                        "Decisamente Kreygasm",
                        "Molto probabilmente Kappa",
                        "Diciamo che le prospettive sono buone 4Head",
                        "Ci puoi contare! SeemsGood",

                        "E' difficile... Riprova più tardi! :thinking:",
                        "Meglio che non ti risponda ora monkaS",
                        "Ora non ho proprio voglia di risponderti ResidentSleeper",

                        "Non ci contare LUL",
                        "Le mie fonti dicono di no FeelsBadMan",
                        "Diciamo che le prospettive non sono per niente buone :/",
                        "Molto... Molto... improbabile haHAA"
                        "Ma proprio no LUL"
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

        self.greetings = ["ciao", "buonasera", "buongiorno", "salve"]
        self.greeted = []

        self.words_cooldown = dict()

        self.msg_count = 0

        self.msg_spam = ["Attaccate a StoDiscord https://discord.gg/7r7VfDp KappaPride",
        				"Se vuoi supportare il canale... Attaccate a Stockhausen, clicca sul Follow. CLASSIC PogChamp",
        				"Io sono BotAna, per i miei comandi digita !comandi PogChamp",
                        "Anche se può sembrare che Pinasu non sia nello stream, ricordate che vi osserva sempre monkaPeek",
			            "Se vedi messaggi del tipo anaLove , FeelsBadMan o monkaS e pensi che la gente sia impazzita, probabilmente non hai BetterTTV: https://goo.gl/hx75Jf 4Head",
        				"Vuoi giocare con noi? Usa il comando !play! KappaPride",
                        "Guadagna punti per comprare i tuoi giochi preferiti con Refereum e Stockhausen_L2P! FeelsGoodMan https://earn.refereum.com/?refid=stockhausen_l2p",
                        "Per scoprire come usare al meglio i comandi, usa il comando !info FeelsGoodMan",
                        "Inviate ad Alessiana su Discord un audio con cui date il benvenuto da parte vostra nella famigliana ai nuovi follower così da poterlo mettere quando qualcuno mette follow KappaPride"
                        ]

        self.quotes = []

        self.online = None

        self.lock = threading.RLock()
        self.lock2 = threading.RLock()

        self.vodded = []

        self.previous_title = ""
        self.previous_game = ""

        self.state_string = ""

        self.text_to_speech = 0

        self.youtube_count = 0

    def run(self):
        try:
            self.BOT_OAUTH = self.get_bot_oauth()
            self.NICK = self.get_nick()
            self.CHAN = "#"+self.NICK
            self.CLIENT_ID = self.get_clientID()
            self.USER_ID = self.get_userID()

            self.load_commands()
            self.load_sounds()
            self.load_image()
            self.load_quotes()

            self.sock.connect((self.HOST, self.PORT))
            self.sock.send(bytes("PASS " + self.BOT_OAUTH + "\r\n", "UTF-8"))
            self.sock.send(bytes("NICK " + self.NICK + "\r\n", "UTF-8"))
            self.sock.send(bytes("JOIN " + self.CHAN + "\r\n", "UTF-8"))

            self.print_message("I'm now connected to "+ self.NICK + ".")

            self.online = self.check_online()

            threading.Thread(target=self.check_online_cicle, args=()).start()

            self.send_message("Don't even worry guys, BotAna is here anaLove")

            threading.Thread(target=self.check_spam, args=()).start()
            
            while True:
                self.lock.acquire()
                tmponline = self.online
                self.lock.release()

                rec = (str(self.sock.recv(1024).decode('utf-8'))).split("\r\n")

                if tmponline["stream"] == None or (tmponline["stream"]["stream_type"] != "watch_party" and tmponline["stream"]["stream_type"] != "live"):
                    if self.state_string != "offline":
                        self.state_string = "offline"

                    if self.vodded:
                        self.vodded = []
                    if rec:
                        for line in rec:
                            if "PING" in line:
                                self.sock.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))

                elif tmponline["stream"]["stream_type"] == "watch_party":
                    if self.state_string != "vodcast":
                        self.state_string = "vodcast"
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

                                    if "tmi.twitch.tv" not in self.username and self.username not in self.vodded and self.username not in self.mods:
                                        self.vodded.append(self.username)
                                        self.send_message("Ciao "+self.username+"! Questo è un Alessiana del passato ( monkaS ), ma Stockhausen_L2P torna (quasi) tutte le sere alle 20:00! Pigia follow! cmonBruh ")
                                        self.send_message("PS: puoi comunque attaccarte a StoDiscord nel frattempo: https://goo.gl/2QSx3V KappaPride")

                elif tmponline["stream"]["stream_type"] == "live":
                    if self.state_string != "live":
                        self.state_string = "live"

                    if self.vodded:
                        self.vodded = []
                    if rec:
                        for line in rec:
                            if "PING" in line:
                                self.sock.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))
                            else:
                                parts = line.split(':', 2)

                                if len(parts) < 3: continue
                                if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
                                    self.message = parts[2]

                                usernamesplit = parts[1].split("!")
                                self.username = usernamesplit[0]

                                if "tmi.twitch.tv" in self.username:
                                    continue

                                if self.username not in self.mods:
                                    self.lock2.acquire()
                                    self.msg_count += 1
                                    self.lock2.release()

                                self.print_message(self.username+": "+self.message)

                                if sum(1 for c in self.message if c.isupper()) > 15:
                                    self.check_ban()

                                if set(self.greetings).intersection(set(list(self.message.lower().split(' ')))):
                                    if self.username not in self.greeted and self.username not in self.mods:
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

                                    if len(message_list) == 1 and self.message in self.sounds.keys():
                                        self.call_sound(self.message)
                                    elif len(message_list) == 1 and self.message in self.images.keys():
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

    def afk(self):
        url = "https://api.twitch.tv/kraken/channels/"+self.NICK+""
        params = {"Client-ID" : ""+self.CLIENT_ID+""}
        resp = requests.get(url=url, headers=params)
        j = json.loads(resp.text)
        self.previous_title = j["status"]
        self.previous_game = j["game"]
        self.send_message("!title AFK")
        self.send_message("!game IRL")

    def in_game(self):
        self.send_message("!title " + self.previous_title)
        self.send_message("!game " + self.previous_game)
        self.previous_title = ""
        self.previous_game = ""

    def check_online(self):
        try:
            url = "https://api.twitch.tv/kraken/streams/"+self.NICK+""
            params = {"Client-ID" : ""+self.CLIENT_ID+""}
            resp = requests.get(url=url, headers=params)
            return json.loads(resp.text)
        except:
            return

    def check_online_cicle(self):
        while True:
            tmp = self.check_online()
            self.lock.acquire()
            self.online = tmp
            self.lock.release()
            time.sleep(10)

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

    def get_userID(self):
        return self.read_config_file("userID.txt")

    def get_bot_oauth(self):
        return self.read_config_file("bot_OAuth.txt")

    def get_nick(self):
        return self.read_config_file("username.txt")

    def get_clientID(self):
        return self.read_config_file("clientID.txt")

    def print_message(self, msg):
        print(msg)
        self.sign.emit(time.strftime("%H:%M  ")+msg)

    def show_image(self, path):
        self.sign2.emit(path)

    def send_message(self, message):
        self.sock.send(bytes("PRIVMSG "+self.CHAN+" :"+str(message)+"\r\n", 'utf-8'))
        self.print_message(self.botName + ": " + str(message))

    def send_whisper(self, message):
        self.sock.send(bytes("PRIVMSG #botana__ :/w "+self.username+" "+message+"\r\n", "UTF-8"))

    def check_ban(self):
        if self.username not in self.mods:
            if self.username == self.to_ban:
                self.send_message("/timeout "+self.username+" 5")
            else:
                self.to_ban = self.username
                self.send_message(self.username+", hai davvero bisogno di tutti quei caps? <warning>")

    def check_spam(self):
        tempo = time.time()
        index = 0
        while True:
            self.lock2.acquire()
            count = self.msg_count
            self.lock2.release()
            if time.time() - tempo > 900 and count > 15:
                self.send_message(self.msg_spam[index])
                tempo = time.time()
                self.lock2.acquire()
                self.msg_count = 0
                self.lock2.release()
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
                self.add_in_timeout(command)
                return False
            return True
        elif command in self.commandsPleb.keys():
            if command not in self.timeCommandsPlebCalled or (time.time() - self.timeCommandsPlebCalled[command] >= float(self.commandsPleb[command].get_cooldown())):
                self.add_in_timeout(command)
                return False
            return True

    def sound_add_in_timeout(self, sound):
        if sound in self.sounds.keys():
            self.timeLastSoundCalled = time.time()

    def sound_is_in_timeout(self, sound):
        if sound in self.sounds.keys():
            if self.timeLastSoundCalled == None or (time.time() - self.timeLastSoundCalled >= float(self.cooldownSound)):
                self.sound_add_in_timeout(sound)
                return False
        return True

    def image_add_in_timeout(self, img):
        if img in self.images.keys():
            self.timeLastImageCalled = time.time()

    def image_is_in_timeout(self, img):
        if img in self.images.keys():
            if self.timeLastImageCalled == None or (time.time() - self.timeLastImageCalled >= float(self.cooldownImage)):
                self.image_add_in_timeout(img)
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
            self.send_message("Grazie a "+self.username+" non ci sono più utenti che vogliono giocare FeelsBadMan")

        elif self.message == "!raffle":
            if len(self.players) == 0:
                self.send_message("Non vuole giocare nessuno BibleThump ")
                return

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

        elif self.message == "!newpatch":
            threading.Thread(target=self.set_patch, args=(self.arguments,)).start()

        elif self.message == "!addsound":
            tmp = self.arguments.split(' ')
            if not tmp[0].startswith('!'):
                self.send_message("Errore. Il suono deve essre un comando (deve avere ! davanti).")
                return

            elif len(tmp) < 1 or len(tmp) > 1:
                self.print_message(tmp)
                self.send_message("Errore. Usa !addsound <!suono>.")
                return

            if (tmp[0] in self.sounds.keys()):
                self.send_message("Non posso aggiungere un suono uguale a uno che esiste già, stupido babbuino LUL")
                return

            PATH = 'res\\Sounds\\'
            self.print_message(PATH)
            snd = str(tmp[0])[1:]+".wav"
            if not os.path.isfile(PATH+snd):
                self.print_message(PATH+snd)
                self.send_message("Errore. Aggiungi il file "+snd+" alla cartella "+PATH+" .")
                return

            with open('sounds.csv', 'a',  encoding='utf-8') as f:
                f.write("\n"+str(tmp[0]))
            self.send_message("Suono "+str(tmp[0])+" aggiunto correttamente FeelsGoodMan")

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
                with open('commands.csv', 'a',  encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';', quotechar='|', lineterminator='\n')
                    writer.writerow(fields)
                if tmp[3] == "mod":
                    self.commandsMod[tmp[0]] = newComm
                elif tmp[3] == "pleb":
                    self.commandsPleb[tmp[0]] = newComm
                self.send_message("Ho aggiunto il comando " + tmp[0] + " FeelsGoodMan")
            else:
                self.send_message("Errore. Usa: !comando;risposta;cooldown;permessi(pleb/mod);gioco(opzionale)")

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
                self.send_message("Errore. Usa: !removecommand !comando mod(opzionale)")
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
                        self.send_message(com.get_response())

    def set_patch(self, args):
        if args != "":
            try:
                file = open("patch.txt", "w")
                file.write(args)
                self.send_message("Nuova patch registrata SeemsGood ")
            except:
                self.print_message("Error while writing file patch.txt")
        else:
            self.send_message("Errore. Usa !newpatch link")

    def start_roulette(self, user):
        self.add_in_timeout("!roulette")
        self.send_message("Punto la pistola nella testa di "+user+"... monkaS")
        time.sleep(5)
        dead_or_alive = randint(1, 10)
        if dead_or_alive <= 5:
            self.send_message("Il corpo di "+user+" giace in chat monkaS Qualcuno può venire a pulire? LUL")
        else:
            self.send_message("La pistola si è inceppata! PogChamp "+user+" è sopravvissuto Kreygasm")

    def start_suicidio(self, user, nick, mods):
        if user == nick:
            self.send_message("Imperatore mio Imperatore, non posso permetterti di farlo! BibleThump")
            time.sleep(2)
            self.send_message("/me si è sacrificata per l'Imperatore Alessiana.")
        elif user in mods:
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
            self.send_message("Mi dispiace "+username+", ma tu non amerai nessuno oggi FeelsBadMan")
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

    def get_stats(self, user, platform):
        if platform != "pc" and platform != "xbox" and platform != "ps4":
            self.send_message("Errore. Usa !wins <utente> <piattaforma> SeemsGood")
        else:
            URL = "https://fortnitetracker.com/profile/"+platform+"/"+user
            if '%20' in user:
                user = user.replace('%20', ' ')
            try:
                resp = requests.get(URL)
                lifetime_stats = json.loads(self.find(resp.text, 'var LifeTimeStats = ', ';</script>'))
                player_data = json.loads(self.find(resp.text, 'var playerData = ', ';</script>'))
                wins = lifetime_stats[7]['Value']
                solo = player_data['p2'][1]['value'] if "p2" in player_data else "N/A"
                duo = player_data['p10'][1]['value'] if "p10" in player_data else "N/A"
                squad = player_data['p9'][1]['value'] if "p9" in player_data else "N/A"
                self.send_message("["+user+"] Solo: "+solo+", Duo: "+duo+", Squad: "+squad+" ("+wins+" partite) KappaPride ")
            except ValueError:
                if platform == "ps4" or platform == "xbox":
                    self.send_message("Utente <"+user+"> non trovato BibleThump Assicurati di aver collegato il tuo account PS4 Xbox a quello di EpicGames!")
                else:
                    self.send_message("Utente <"+user+"> non trovato BibleThump Sicuro di aver scritto bene?")

    def find(self, s, first, last):
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]

    def speak_text(self, text):
        self.text_to_speech = time.time()
        pythoncom.CoInitialize()
        speak = wincl.Dispatch("SAPI.SpVoice")
        speak.Speak(text)

    def get_rand_quote(self):
        rand = randint(0, len(self.quotes)-1)
        q = self.quotes[rand]
        self.send_message("#"+str(str(q.get_index()))+": ''"+str(q.get_quote())+" '' - "+str(q.get_author())+" "+str(q.get_date()))
        if time.time() - self.text_to_speech > 20:
            threading.Thread(target=self.speak_text, args=(str(q.get_author())+" una volta disse: "+str(q.get_quote()),)).start()

    def get_quote(self, args):
        if int(args) > len(self.quotes):
            self.send_message("Non ho tutte quelle citazioni HotPokket")
        else:
            q = self.quotes[int(args)-1]
            self.send_message("#"+str(q.get_index())+": ''"+str(q.get_quote())+" '' - "+q.get_author()+" "+str(q.get_date()))
            if time.time() - self.text_to_speech > 20:
                threading.Thread(target=self.speak_text, args=(str(q.get_author())+" una volta disse: "+str(q.get_quote()),)).start()

    def add_quote(self, args):
        args = str(args)
        args = args.split('-')
        if len(args) != 2:
            self.send_message("A questa citazione manca l'autore: aggiungilo alla fine dopo un trattino!")
            return

        self.quotes.append(Quote(len(self.quotes)+1, args[0], args[1], time.strftime("[%d/%m/%Y]")))

        fields = [len(self.quotes), args[0], args[1], time.strftime("[%d/%m/%Y]")]

        with open('quotes.csv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quotechar='|', lineterminator='\n')
            writer.writerow(fields)

        self.send_message("Citazione aggiunta con indice #"+str(len(self.quotes)))

    def get_patch(self):
        self.add_in_timeout("!patch")
        try:
            file = open("patch.txt", "r")
            patch = file.read()
            self.send_message(self.username+", ecco l'ulima patch di FortNite (al "+time.strftime("%d/%m/%Y")+"): "+str(patch)+" FeelsGoodMan")
            file.close()
        except:
            self.print_message("Error reading patch.txt")

    def call_command_pleb(self):
        if self.message == "!cit" and not self.is_in_timeout("!cit"):
            if self.arguments:
                if self.arguments.isdigit():
                    self.get_quote(self.arguments)
                else:
                    self.add_quote(self.arguments)
            else:
                self.get_rand_quote()

        elif self.message == "!wins" and not self.is_in_timeout("!wins") and self.is_for_current_game(self.commandsPleb["!wins"]):
            if self.arguments:
                args = self.arguments.split(' ')
                if '%20'.join(args[:-1]).lower() == "zizory":
                    self.send_message("E' inutile vedere le mie stat, sono troppo scarsa StoneLightning ")
                    return
                threading.Thread(target=self.get_stats, args=('%20'.join(args[:-1]), args[-1],)).start()
            else:
                threading.Thread(target=self.get_stats, args=(["Alessiana", "pc"])).start()

        elif self.message == "!patch" and not self.is_in_timeout("!patch") and self.is_for_current_game(self.commandsPleb["!wins"]):
            threading.Thread(target=self.get_patch, args=()).start()

        elif self.message == "!play":
            if self.username not in self.players:
                self.players.append(self.username)
                self.send_message(self.username+", ti ho aggiunto alla lista dei viewers che vogliono giocare PogChamp")

        elif self.message == "!players" and not self.is_in_timeout("!players"):
            if self.players:
                pl = ', '.join(self.players)
                if len(self.players) == 1:
                    self.send_message(pl+" vuole giocare! KappaPride")
                else:
                    self.send_message(pl+" vogliono giocare! KappaPride")
            else:
                self.send_message("Non vuole giocare nessuno BibleThump")

        elif self.message == "!maledizione" and not self.is_in_timeout("!maledizione"):
            file = open("maledizioni.txt", "r")
            maled = file.read()
            count = int(maled) + 1
            file.close()

            self.send_message("Ovviamente la safe zone è dall'altra parte (x"+str(count)+" LUL ) Never lucky BabyRage")

            file = open("maledizioni.txt", "w")
            file.write(str(count))

        elif self.message == "!roulette" and not self.is_in_timeout("!roulette"):
            threading.Thread(target=self.start_roulette, args=([self.username])).start()

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

        elif self.message == "!suicidio":
            threading.Thread(target=self.start_suicidio, args=([self.username, self.NICK, self.mods])).start()

        elif self.message == "!8ball" and not self.is_in_timeout("!8ball"):
            if self.arguments != "":
                ball = random.choice(self.ball_choices)
                self.send_message(ball)
            else:
                self.send_message("Errore. Usa: !8ball <domanda>.")

        elif self.message == "!love" and not self.is_in_timeout("!love"):
            if self.username == "lusyoo" and self.arguments.lower() == "dio":
                self.send_message(self.username+" ama "+self.arguments+" allo 0% FeelsBadMan")
                return
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
            if self.arguments != "":
                self.send_message(self.username+" ha bandito "+self.arguments+" dalla chat PogChamp")
            else:
                self.send_message(self.username+" non posso bandire il nulla,  stupido babbuino LUL")

        elif self.message == "!comandi" and not self.is_in_timeout("!comandi"):
            self.send_message(str(set(self.commandsPleb.keys())))

        elif self.message == "!suoni" and not self.is_in_timeout("!suoni"):
            self.get_sounds()

        elif self.message == "!energia":
            if self.arguments:
                args = self.arguments.split(' ')
                if len(args) > 1:
                    self.send_message("Mi dispiace "+self.username+", ma puoi donare la tua energia a una sola persona FeelsBadMan")
                else:
                    self.send_message("༼ つ ◕_◕ ༽つ "+str(args[0])+" prendi la mia energia ༼ つ ◕_◕ ༽つ")
            else:
                self.send_message("༼ つ ◕_◕ ༽つ Alessiana prendi la mia energia ༼ つ ◕_◕ ༽つ")
        else:
            for com in self.commandsPleb.values():
                if com.is_simple_command() and self.message == com.get_name() and self.is_for_current_game(com):
                    if not self.is_in_timeout(com.get_name()):
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

        elif "omg" in message.lower() and not self.is_word_in_timeout("omg"):
            self.word_in_timeout("omg")
            self.send_message("IT'S OVER 9000 9000Ana")

    def load_quotes(self):
        with open('quotes.csv', encoding='utf-8') as quotes:
            reader = csv.reader(quotes, delimiter=';', quotechar='|')
            for row in reader:
                self.quotes.append(Quote(row[0], row[1], row[2], row[3]))

        self.print_message("quotes.csv was read correctly.")

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
        elif not self.sound_is_in_timeout(name) and self.is_for_current_game(self.sounds[name]):
            self.play_sound(sname)

    def is_for_current_game(self, command):
        if not command.is_for_specific_game():
            return True

        user_id = self.USER_ID
        try:
            url = 'https://api.twitch.tv/kraken/channels/'+user_id
            headers = {'Client-ID': self.CLIENT_ID, 'Accept': 'application/vnd.twitchtv.v5+json'}
            resp = requests.get(url, headers=headers).json()
        except:
            self.print_message("Error getting stream title.")
            return
        curr_game = resp["game"]

        if command.get_game() == curr_game:
            return True
        return False

    #***************************************************************************
    #   DO  NOT SCROLL  DOWN
    #***************************************************************************






    #***************************************************************************
    #   REALLY  DUDE
    #***************************************************************************






    #***************************************************************************
    #   I   WARNED  YOU
    #***************************************************************************




    def set_title(self):
        #GET https://api.twitch.tv/kraken/oauth2/authorize
        #?client_id=<your client ID>
        #&redirect_uri=<your registered redirect URI>
        #&response_type=code
        #&scope=<space-separated list of scopes>
        #Get token
        URL = "https://api.twitch.tv/kraken/oauth2/authorize?client_id="+self.CLIENT_ID+"&redirect_uri=https://pinasu.github.io/BotAna/&response_type=code&scope=channel_editor"
        #funuvnh4eo2qlq874lcncgtkzccugr
        #POST https://api.twitch.tv/kraken/oauth2/token
        #?client_id=uo6dggojyb8d6soh92zknwmi5ej1q2
        #&client_secret=nyo51xcdrerl8z9m56w9w6wg
        #&code=394a8bc98028f39660e53025de824134fb46313
        #&grant_type=authorization_code
        #&redirect_uri=http://localhost
        URL = "https://api.twitch.tv/kraken/oauth2/token?client_id="+self.CLIENT_ID+"&client_secret="+"su0xa7amlq6rss7r9b7422n9tengdh"+"&code="+"funuvnh4eo2qlq874lcncgtkzccugr"+"&grant_type=authorization_code"+"&redirect_uri=https://pinasu.github.io/BotAna/"
        resp = requests.post(URL)
        self.print_message(str(json.loads(resp.text)))
        #curl -H 'Client-ID: uo6dggojyb8d6soh92zknwmi5ej1q2'
        #-H 'Accept: application/vnd.twitchtv.v5+json'
        #-H 'Authorization: OAuth cfabdegwdoklmawdzdo98xt2fo512y'
        #-H 'Content-Type: application/json'
        #-d '{"channel": {"status": "The Finalest of Fantasies", "game": "Final Fantasy XV", "channel_feed_enabled": true}}' \
        #-X PUT 'https://api.twitch.tv/kraken/channels/44322889'
        URL = "https://api.twitch.tv/kraken/channels/"+"133174210"
        headers = {
                "Client-ID" : ""+self.CLIENT_ID+"",
                "Accept": "application/vnd.twitchtv.v5+json",
                "Authorization": "OAuth "+access_token+"",
                "Content-Type": "application/json"
        }
        data = {"channel": {"status": "The Finalest of Fantasies", "game": "Final Fantasy XV", "channel_feed_enabled": true}}
        requests.put(url=URL, headers=headers, data=data)
