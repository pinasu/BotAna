import socket, time, json, requests, datetime, command, configparser, os, traceback, subprocess, random, csv, pygame, threading, pythoncom
import win32com.client as wincl
from bs4 import BeautifulSoup
from pygame import mixer
from random import randint
from command import Command
from image import Image
from sound import Sound
from quote import Quote
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import git
from git import Repo
#Key pressing
import ctypes

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class BotAna(QtCore.QThread):
    sign = pyqtSignal(str)
    sign2 = pyqtSignal(str)
    sign3 = pyqtSignal(bool)
    sign4 = pyqtSignal(bool)

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
        self.CLIENT_SECRET = ""

        self.username = ""
        self.message = ""
        self.arguments = ""

        self.RATE = 20/30

        self.mods = ["boomtvmod", "botana__", "boxyes", "ilmarcana", "iltegame", "logviewer", "lusyoo", "moobot", "nightbot", "pinasu", "revlobot", "stockhausen_l2p", "vivbot", "xuneera"]

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
                        "Diciamo che le prospettive non sono per niente buone FeelsBadMan",
                        "Molto... Molto... improbabile haHAA",
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

        self.words_cooldown = dict()

        self.msg_count = 0

        self.msg_spam = []
        self.msg_spam = self.get_spam_phrases('spam.txt')

        self.quotes = []

        self.online = None

        self.lock = threading.RLock()
        self.lock2 = threading.RLock()
        self.lock3 = threading.RLock()

        self.vodded = []

        self.previous_title = ""
        self.previous_game = ""

        self.state_string = ""

        self.text_to_speech = 0

        self.speak = None

        self.gged = dict()

        self.is_muted = False

        self.tempo_trap = time.time()
        self.trap_nicks = []

        self.trap_count = 0

        self.multi_twitch = "https://multistre.am/"+self.NICK+"/"

        self.can_move = False
        self.move_dict = dict()

        self.repo = Repo(os.path.dirname(os.path.realpath(__file__)))

    def run(self):
        try:

            config = configparser.ConfigParser()
            self.BOT_OAUTH = self.get_bot_oauth('config.ini', config)
            self.NICK = self.get_nick('config.ini', config)
            self.CHAN = "#"+self.NICK
            self.CLIENT_ID = self.get_clientID('config.ini', config)
            self.USER_ID = self.get_userID('config.ini', config)
            self.CLIENT_SECRET = self.get_clientSECRET('config.ini', config)

            self.load_commands()
            self.load_sounds()
            self.load_image()
            self.load_quotes()

            self.sock.connect((self.HOST, self.PORT))
            self.sock.send(bytes("PASS " + self.BOT_OAUTH + "\r\n", "UTF-8"))
            self.sock.send(bytes("NICK " + self.NICK + "\r\n", "UTF-8"))
            self.sock.send(bytes("JOIN " + self.CHAN + "\r\n", "UTF-8"))

            self.print_message("I'm now connected to "+ self.NICK + ".")

            self.send_message("Don't even worry guys, BotAna is here anaLove")

            threading.Thread(target=self.check_new_follows, args=(self.get_follower_list(),)).start()

            threading.Thread(target=self.reset_trap, args=()).start()

            threading.Thread(target=self.check_new_hosts, args=(self.get_host_list(),)).start()

            threading.Thread(target=self.check_spam, args=()).start()

            self.online = self.check_online()
            threading.Thread(target=self.check_online_cicle, args=()).start()

            while True:
                self.lock.acquire()
                tmponline = self.online
                self.lock.release()

                rec = (str(self.sock.recv(1024).decode('utf-8'))).split("\r\n")

                if not hasattr(tmponline, "__getitem__"):
                    file = open("LogError.txt", "a")
                    file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + "\n" + "-----------------MI è ARRIVATO UN OGGETTO SUL TIPO DELLO STREAM SBAGLIATO---------------------- (linea 154)" + "\n" + "\n")
                    continue

                if tmponline['stream'] == None:
                    if self.state_string != "offline":
                        self.print_message(self.NICK+" is offline.")
                        self.state_string = "offline"

                    if self.vodded:
                        self.vodded = []
                    if rec:
                        for line in rec:
                            if "PING" in line:
                                self.sock.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))

                elif tmponline["stream"]["stream_type"] == "rerun":
                    if self.state_string != "vodcast":
                        self.print_message(self.NICK+" is in a vodcast.")
                        self.state_string = "vodcast"

                    if rec:
                        for line in rec:
                            if "PING" in line:
                                self.sock.send("PONG tmi.twitch.tv\r\n".encode("utf-8"))
                            else:
                                parts = line.split(':')
                                if len(parts) < 3: continue
                                if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PARTS" not in parts[1]:
                                    self.message = parts[2].lower()
                                    usernamesplit = parts[1].split("!")
                                    self.username = usernamesplit[0]

                                    if "tmi.twitch.tv" not in self.username and self.username not in self.vodded and self.username not in self.mods:
                                        self.vodded.append(self.username)
                                        self.send_message("Ciao "+self.username+"! Questo è un Alessiana del passato ( monkaS ), ma Stockhausen_L2P torna (quasi) tutte le sere alle 20:00! Pigia follow! cmonBruh ")
                                        self.send_message("PS: puoi comunque attaccarte a StoDiscord nel frattempo: https://goo.gl/2QSx3V KappaPride")

                else:
                    if self.state_string != "live":
                        self.print_message(self.NICK+" is online.")
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

                            if self.can_move:
                                self.trigger_key(self.message)

                            if self.message.startswith('!'):
                                self.message = self.message.lower()

                                message_list = self.message.split(' ')

                                self.message = message_list[0]
                                self.arguments = ' '.join(message_list[1:])

                                if self.message in self.commandsMod.keys() and self.username in self.mods:
                                    self.call_command_mod()
                                elif self.message in self.commandsPleb.keys():
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
            file.close()

    def __del__(self):
        self.exiting = True
        self.wait()

    #Key pressing
    # non funge su doppio schermo, prende sempre solo il primo
    def mouse_move_from_bottom_right(self, x, y):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        x = int((ctypes.windll.user32.GetSystemMetrics(0) - x) * (65536/ctypes.windll.user32.GetSystemMetrics(0))+1)
        y = int((ctypes.windll.user32.GetSystemMetrics(1) - y) * (65536/ctypes.windll.user32.GetSystemMetrics(1))+1)
        ii_.mi = MouseInput(x, y, 0, 0x0001 | 0x8000, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def mouse_move_abs(self, x, y):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        x = int(x*(65536/ctypes.windll.user32.GetSystemMetrics(0))+1)
        y = int(y*(65536/ctypes.windll.user32.GetSystemMetrics(1))+1)
        ii_.mi = MouseInput(x, y, 0, 0x0001 | 0x8000, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def mouse(self, x, y, code=""):
        if code == "PressLeft":
            cd = 0x0002;
        elif code == "ReleaseLeft":
            cd = 0x0004;
        elif code == "PressRight":
            cd = 0x0008;
        elif code == "ReleaseRight":
            cd = 0x0010;
        else:
            cd = 0x0001;

        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(x, y, 0, cd, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def press_key(self, hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
        x = Input( ctypes.c_ulong(1), ii_ )
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_key(self, hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
        x = Input( ctypes.c_ulong(1), ii_ )
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def press_whait_release(self, type, time, code):
        threading.Thread(target=self.thread_press, args=(type, time, code,)).start()

    def thread_press(self, type, tim, code):
        tmp = str(code)
        self.lock3.acquire()
        if tmp in self.move_dict:
            self.move_dict[tmp] = self.move_dict[tmp] + 1
        else:
            self.move_dict[tmp] = 1
        self.lock3.release()
        if type == "Mouse":
            self.mouse(0,0,"Press" + code)
            time.sleep(tim)
            self.lock3.acquire()
            if self.move_dict[tmp] == 1:
                self.mouse(0,0,"Release" + code)
            self.move_dict[tmp] = self.move_dict[tmp] - 1
            self.lock3.release()
        elif type == "Key":
            if code in [0x11, 0x1F, 0x1E, 0x20]: # w a s d
                self.press_key(0x2A) #shift per correre
            self.press_key(code)
            time.sleep(tim)
            self.lock3.acquire()
            if self.move_dict[tmp] == 1:
                if code in [0x11, 0x1F, 0x1E, 0x20]: # w a s d
                    self.release_key(0x2A) #shift per correre
                self.release_key(code)
            self.move_dict[tmp] = self.move_dict[tmp] - 1
            self.lock3.release()

    def trigger_key(self, text):
        # directx scan codes http://www.gamespp.com/directx/directInputKeyboardScanCodes.html

        if not len(text) == 1:
            return

        if text.lower() == "q":
            self.press_key(0x21) #F
            self.release_key(0x21) #F
            time.sleep(0.5)
            self.mouse(0,0,"PressLeft")
            self.mouse(0,0,"ReleaseLeft")
        elif text.lower() == "g":
            self.press_key(0x22) #g
            self.release_key(0x22)
            time.sleep(0.5)
            self.mouse(0,0,"PressLeft")
            self.mouse(0,0,"ReleaseLeft")
        #elif text.lower() == "f":
            #TODO piazzare scale
            #self.press_key(0x14) #T
            #self.release_key(0x14)
            #time.sleep(0.5)
            #self.mouse(0,0,"PressLeft")
        elif text.lower() == "1":
            self.press_key(0x02) #1
            self.release_key(0x02)
            # self.mouse(0,0,"PressLeft")
            self.press_whait_release("Mouse", 5, "Left")
        elif text.lower() == "2":
            self.press_key(0x03) #2
            self.release_key(0x03)
            self.press_whait_release("Mouse", 3, "Left")
        elif text.lower() == "3":
            self.press_key(0x04) #3
            self.release_key(0x04)
            self.press_whait_release("Mouse", 3, "Left")
        elif text.lower() == "4":
            self.press_key(0x05) #4
            self.release_key(0x05)
            self.press_whait_release("Mouse", 3, "Left")
        elif text.lower() == "5":
            self.press_key(0x06) #5
            self.release_key(0x06)
            self.press_whait_release("Mouse", 3, "Left")
        elif text.lower() == "6":
            self.press_key(0x2C) #Z
            self.release_key(0x2C)
            self.press_whait_release("Mouse", 3, "Left")
        elif text.lower() == "u":
            self.mouse(0,-1000) #Top
        elif text.lower() == "j":
            self.mouse(0,1000) #Bottom
        elif text.lower() == "h":
            self.mouse(-1000,0) #Left
        elif text.lower() == "k":
            self.mouse(1000,0) #Right
        elif text.lower() == "w":
            self.press_whait_release("Key", 5, 0x11)
            # self.press_key(0x11)
        elif text.lower() == "s":
            self.press_whait_release("Key", 5, 0x1F)
            # self.press_key(0x1F)
        elif text.lower() == "a":
            self.press_whait_release("Key", 5, 0x1E)
            # self.press_key(0x1E)
        elif text.lower() == "d":
            self.press_whait_release("Key", 5, 0x20)
            # self.press_key(0x20)
        elif text.lower() == "m":
            self.press_key(0x32) #4
            self.release_key(0x32)
        elif text.lower() == "b":
            self.press_key(0x39) #space
            self.release_key(0x39)
        elif text.lower() == "e":
            self.press_key(0x12) #e
            self.release_key(0x12)
        elif text.lower() == "x":
            self.press_key(0x01) #esc
            self.release_key(0x01)
        elif text.lower() == "r":
            self.mouse_move_abs(1920 + 1790, 1050)
            # self.mouse_move_from_bottom_right(130, 30)
            self.mouse(0,0,"PressLeft")
            self.mouse(0,0,"ReleaseLeft")
        elif text.lower() == "t":
            self.mouse_move_abs(1920 + 1700, 950)
            # self.mouse_move_from_bottom_right(220, 130)
            self.mouse(0,0,"PressLeft")
            self.mouse(0,0,"ReleaseLeft")

    def set_can_move(self, can):
        self.can_move = can

    def get_can_move(self):
        return self.can_move

    def afk(self):
        try:
            url = "https://api.twitch.tv/kraken/channels/"+self.NICK+""
            params = {"Client-ID" : ""+self.CLIENT_ID+""}
            resp = requests.get(url=url, headers=params)
            j = json.loads(resp.text)
            self.previous_title = j["status"]
            self.previous_game = j["game"]
            self.send_message("!title AFK")
            self.send_message("!game IRL")
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def in_game(self):
        self.send_message("!title " + self.previous_title)
        self.send_message("!game " + self.previous_game)
        self.previous_title = ""
        self.previous_game = ""

    def get_user_id(self, user):
        try:
            url = "https://api.twitch.tv/kraken/users?login="+user
            params = {
                "Accept": "application/vnd.twitchtv.v5+json",
                "Client-ID" : ""+self.CLIENT_ID+""
            }
            resp = requests.get(url=url, headers=params)
            user = json.loads(resp.text)
            if user:
                return user['users'][0]['_id']
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def reset_trap(self):
        try:
            file = open("trap.txt", "w")
            file.write("0")
            file.close()
        except:
            self.print_message("Error opening trap.txt\n")

    def check_new_hosts(self, old):
        while True:
            new = self.get_host_list()
            if(new or old):
                new_st = set(new)
                old_st = set(old)
                diff = new_st - old_st

                for x in diff:
                    try:
                        url = "https://api.twitch.tv/kraken/streams/"+self.get_user_id(x)
                        params = {
                        "Accept": "application/vnd.twitchtv.v5+json",
                        "Client-ID" : "tf2kbvxsjvy19m0m53oxupk6w6aelv"
                        }
                        resp = requests.get(url=url, headers=params)
                        jsonl = json.loads(resp.text)
                        if jsonl['stream'] != None:
                            count = int(jsonl['stream']['viewers'])
                            self.send_message("[Host da "+x+"] https://www.twitch.tv/"+x)
                    except:
                        file = open("LogError.txt", "a")
                        file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
                        traceback.print_exc()
                        file.close()
            old = new
            time.sleep(10)

    def get_host_list(self):
        try:
            url = "https://tmi.twitch.tv/hosts?include_logins=1&target="+self.USER_ID
            params = {
                "Accept": "application/vnd.twitchtv.v5+json",
                "Client-ID" : ""+self.CLIENT_ID+""
            }
            resp = requests.get(url=url, headers=params)
            lst = json.loads(resp.text)['hosts']
            host_lst = []
            for l in lst:
                host_lst.append(l['host_login'])
            return host_lst
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def check_new_follows(self, old):
        while True:
            new = self.get_follower_list()
            new_st = set(new)
            old_st = set(old)
            diff = new_st - old_st
            for x in diff:
                self.send_message(x+"! Grazie del follow PogChamp Mucho apreciato 1 2 3 1 2 3 KappaPride Usa !discord per unirti alla FamigliANA FeelsGoodMan")
                old = new
            time.sleep(10)

    def get_follower_list(self):
        try:
            url = "https://api.twitch.tv/kraken/channels/"+self.USER_ID+"/follows?limit=100"
            params = {
                "Accept": "application/vnd.twitchtv.v5+json",
                "Client-ID" : ""+self.CLIENT_ID+""
            }
            resp = requests.get(url=url, headers=params)
            lst = json.loads(resp.text)['follows']
            usr_lst = []
            for l in lst:
                usr_lst.append(l['user']['name'])
            return usr_lst
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def check_online(self):
        try:
            url = "https://api.twitch.tv/kraken/streams/"+self.USER_ID
            params = {
                "Accept": "application/vnd.twitchtv.v5+json",
                "Client-ID" : self.CLIENT_ID
            }
            resp = requests.get(url=url, headers=params, timeout=10)
            return json.loads(resp.text)
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def check_online_cicle(self):
        while True:
            tmp = self.check_online()
            self.lock.acquire()
            self.online = tmp
            self.lock.release()
            time.sleep(10)

    def get_spam_phrases(self, path):
        if os.path.exists(path):
            try:
                with open(path, encoding='utf8') as f:
                    msg_spam = f.read().splitlines()
                return msg_spam
            except:
                self.print_message("Error opening " + path + "\n")
        else:
            self.print_message("Error finding " + path + "\n")

    def remove_spam_phrase(self, id):
        try:
            f_r = open("spam.txt", "r", encoding="utf-8")
            d = f_r.readlines()
            f_r.close()

            f = open("spam.txt", "w", encoding="utf-8")
            for line in d:
                if line != self.msg_spam[int(id)-1]+"\n":
                    self.print_message("LINE: *"+line+"* MSG: *"+self.msg_spam[int(id)]+"*")
                    f.write(line)
            f.close()
            self.send_whisper("Spam con id "+str(id)+" rimosso.")

        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def add_spam_phrase(self, phrase):
        if phrase in self.msg_spam:
            self.send_whisper("Errore. Impossibile aggiungere una fase già presente.")
            return
        try:
            self.msg_spam.append(phrase)
            with open("spam.txt", "a",  encoding='utf-8') as f:
                f.write(phrase+"\n")
            self.send_whisper("Frase aggiunta con indice "+str(len(self.msg_spam)))
            f.close()
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def get_userID(self, path, config):
        if os.path.exists(path):
            try:
                config.read(path)
                return config['DEFAULT']['user_id']
            except:
                file = open("LogError.txt", "a")
                file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
                traceback.print_exc()
                file.close()
        else:
            self.print_message("Error reading " + path + "\n")

    def get_bot_oauth(self, path, config):
        if os.path.exists(path):
            try:
                config.read(path)
                return config['DEFAULT']['bot_oauth']
            except:
                    file = open("LogError.txt", "a")
                    file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
                    traceback.print_exc()
                    file.close()
        else:
            self.print_message("Error finding " + path + "\n")

    def get_clientID(self, path, config):
        if os.path.exists(path):
            try:
                config.read(path)
                return config['DEFAULT']['client_id']
            except:
                    file = open("LogError.txt", "a")
                    file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
                    traceback.print_exc()
                    file.close()
        else:
            self.print_message("Error finding " + path + "\n")

    def get_nick(self, path, config):
        if os.path.exists(path):
            try:
                config.read(path)
                return config['DEFAULT']['nick']
            except:
                file = open("LogError.txt", "a")
                file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
                traceback.print_exc()
                file.close()
        else:
            self.print_message("Error reading " + path + "\n")

    def get_clientSECRET(self, path, config):
        if os.path.exists(path):
            try:
                config.read(path)
                return config['DEFAULT']['client_secret']
            except:
                file = open("LogError.txt", "a")
                file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
                traceback.print_exc()
                file.close()
        else:
            self.print_message("Error reading " + path + "\n")

    def print_message(self, msg):
        self.sign.emit(time.strftime("%H:%M  ")+str(msg))

    def show_image(self, path):
        self.sign2.emit(path)

    def send_message(self, message):
        self.sock.send(bytes("PRIVMSG "+self.CHAN+" :"+str(message)+"\r\n", 'utf-8'))
        self.print_message(self.botName + ": " + str(message))

    def send_whisper(self, message):
        self.sock.send(bytes("PRIVMSG #botana__ :/w "+str(self.username)+" "+str(message)+"\r\n", "utf-8"))

    def check_spam(self):
        try:
            tempo = time.time()
            index = 0
            while True:
                self.lock2.acquire()
                count = self.msg_count
                self.lock2.release()
                if time.time() - tempo > 700 and count > 15:
                    self.send_message(self.msg_spam[index])
                    tempo = time.time()
                    self.lock2.acquire()
                    self.msg_count = 0
                    self.lock2.release()
                    index = (index + 1) % len(self.msg_spam)

                time.sleep(1)
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

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

    def fast_restart(self):
        try:
            subprocess.Popen("botanaUserInterface.pyw", shell=True)
            os._exit(0)
        except:
            file = open("LogError.txt", "a")
            file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
            traceback.print_exc()
            file.close()

    def restart(self):
        try:
            # process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, shell=True)
            # retcode = process.communicate()

            o = self.repo.remotes.origin
            o.pull()
        finally:
            self.fast_restart()

    def call_command_mod(self):
        raffled = ""

        if self.message == "!restart":
            self.restart()

        if self.message == "!title":
            self.change_stream_title(self.arguments)

        elif self.message == "!stopbarza":
            self.speak.Pause()
            self.send_message("Questa barza fa schifo HotPokket")

        elif self.message == "!stop":
            self.send_message("HeyGuys")
            os._exit(0)

        elif self.message == "!shout":
            args = self.arguments.split(' ')
            if len(args) == 1:
                try:
                    URL = "https://api.twitch.tv/kraken/channels/"+self.get_user_id(''.join(args))
                    params = {
                        "Accept": "application/vnd.twitchtv.v5+json",
                        "Client-ID" : ""+self.CLIENT_ID+""
                    }

                    resp = requests.get(url=URL, headers=params)
                    self.send_message("Andate a mettere un like a "+self.arguments+" su https://www.twitch.tv/"+self.arguments+" KappaPride")
                except:
                    self.send_whisper("Errore. Il canale non esiste.")
            else:
                self.send_whisper("Errore. Il canale contiene spazi.")

        elif self.message == "!multi":
            args = self.arguments.split(' ')

            if args[0] == "reset":
                self.multi_twitch = "https://multistre.am/"+self.NICK+"/"
                self.send_whisper("Multi-Twitch resettato ("+self.multi_twitch+")")
            elif args[0] == "":
                if "Segui" in self.multi_twitch:
                    self.send_message(self.multi_twitch)
                else:
                    self.send_message("Non ci sono streamer amici da guardare, per ora KappaPride")
            else:
                chans = "/".join(args)
                self.multi_twitch = "Segui tutti gli streamer nello stesso momento! https://multistre.am/"+self.NICK+"/"+chans+" FeelsGoodMan"
                self.send_message(self.multi_twitch)

        elif self.message == "!addspam":
            args = self.arguments
            if len(args) > 1:
                threading.Thread(target=self.add_spam_phrase, args=(args,)).start()
            else:
                self.send_whisper("Impossibile aggiungere lo spam (frase troppo breve).")

        elif self.message == "!removespam":
            args = self.arguments
            if args.isdigit():
                threading.Thread(target=self.remove_spam_phrase, args=(args,)).start()
            else:
                self.send_whisper("Impossibile rimuovere lo spam.")

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
            args = self.arguments.split(' ')
            if len(args) > 1:
                self.send_message(str(args)+", la lista dei comandi è su https://pinasu.github.io/BotAna/ PogChamp")
            else:
                self.send_whisper("Ecco i comandi: [MOD] "+', '.join(str(key[0]) for key in self.commandsMod.items()))
                self.send_whisper(" [PLEB] "+', '.join(str(key[0]) for key in self.commandsPleb.items()))

        elif self.message == "!suoni":
            self.send_message(str(self.sounds))

        elif self.message == "!newpatch":
            threading.Thread(target=self.set_patch, args=(self.arguments,)).start()

        elif self.message == "!addsound":
            tmp = self.arguments.split(' ')
            if not tmp[0].startswith('!'):
                self.send_whisper("Errore. Il suono deve essere un comando (deve avere ! davanti).")
                return

            elif len(tmp) < 1 or len(tmp) > 1:
                self.send_whisper("Errore. Usa !addsound <!suono>.")
                return

            if (tmp[0] in self.sounds.keys()):
                self.send_whisper("Errore. Non posso aggiungere un suono uguale a uno che esiste già.")
                return

            PATH = 'res\\Sounds\\'
            self.print_message(PATH)
            snd = str(tmp[0])[1:]+".wav"
            if not os.path.isfile(PATH+snd):
                self.print_message(PATH+snd)
                self.send_whisper("Errore. Aggiungi il file "+snd+" alla cartella "+PATH+" .")
                return

            with open('sounds.csv', 'a',  encoding='utf-8') as f:
                f.write("\n"+str(tmp[0]))
            self.send_whisper("Suono "+str(tmp[0])+" aggiunto correttamente.")

        elif self.message == "!addcommand":
            tmp = self.arguments.split(";")
            if (tmp[0] in self.commandsMod.keys() and tmp[3] == "mod") or (tmp[0] in self.commandsPleb.keys() and tmp[3] == "pleb"):
                self.send_whisper("Non posso aggiungere un comando uguale a uno che esiste già, stupido babbuino LUL")
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
                self.send_whisper("Ho aggiunto il comando " + tmp[0] + " FeelsGoodMan")
            else:
                self.send_whisper("Errore. Usa: !comando;risposta;cooldown;permessi(pleb/mod);gioco(opzionale)")

        elif self.message == "!removecommand":
            args = self.arguments.split(" ")
            if len(args) == 1 and args[0]== "":
                self.send_whisper("Devi specificarmi quale comando eliminare, stupido babbuino LUL")
                return

            if len(args) == 1 or args[1] == "pleb":
                if args[0] in self.commandsPleb.keys(): #Pleb command
                    del self.commandsPleb[args[0]]
                else:
                    self.send_whisper("Il comando " + args[0] + " (pleb) non esiste, scrivi bene stupido babbuino LUL")
                    return

            elif len(args) == 2 and  args[1] == "mod":
                if args[0] in self.commandsMod.keys(): #Mod command
                    del self.commandsMod[args[0]]
                else:
                    self.send_whisper("Il comando " + args[0] + " (mod) non esiste, scrivi bene stupido babbuino LUL")
                    return

            else:
                self.send_whisper("Errore. Usa: !removecommand !comando mod(opzionale)")
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
                self.send_whisper("Comando " + self.arguments + " eliminato FeelsGoodMan")
            except:
                subprocess.run("del commands.csv", shell=True)
                subprocess.run("ren commands_bkp.csv commands.csv", shell=True)
                self.send_whisper("Impossibile eliminare il comando " + self.arguments+" FeelsBadMan")
            subprocess.run("del commands_bkp.csv", shell=True)

        elif self.message == "!mute":
            self.is_muted = True
            self.sign3.emit(True)
            self.send_message("Credo che me ne starò zitta per un po', grazie Kappa")

        elif self.message == "!unmute":
            self.is_muted = False
            self.sign3.emit(False)
            self.send_message("Toh, m'è tornata la voglia di parlare! PogChamp")

        elif self.message == "!ismute":
            if self.is_muted:
                self.send_message("Non ho voglia di parlare, ora ResidentSleeper")
            else:
                self.send_whisper("SeemsGood")

        elif self.message == "!activatemove":
            if self.get_can_move() == True:
                return
            self.set_can_move(True)
            self.sign4.emit(True)
            self.send_message("La chat ha il comando!!!")

        elif self.message == "!deactivatemove":
            if self.get_can_move() == False:
                return
            self.set_can_move(False)
            self.sign4.emit(False)
            self.send_message("La chat non ha più il comando!!!")

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
                self.send_whisper("Nuova patch registrata SeemsGood ")
                file.close()
            except:
                file = open("LogError.txt", "a")
                file.write(time.strftime("[%d/%m/%Y - %H:%M:%S] ") + traceback.format_exc() + "\n")
                traceback.print_exc()
                file.close()
        else:
            self.send_whisper("Errore. Usa !newpatch link")

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
        try:
            url = "https://tmi.twitch.tv/group/user/stockhausen_l2p/chatters"
            params = dict(user = "na")
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
            while rand_user == username or rand_user == "nightbot" or rand_user == "logviewer":
                rand_user = random.choice(json_str['chatters']['viewers'])

        ret_list.append(rand_user)

        self.send_message("C'è il "+str(rand)+"% <3 tra "+username+" e "+random.choice(ret_list)+" "+emote)

    def get_kd(self, user, platform):
        URL = "https://fortnitetracker.com/profile/"+platform+"/"+user
        if '%20' in user:
            user = user.replace('%20', ' ')
        try:
            try:
                resp = requests.get(URL, timeout=3)
            except requests.exceptions.Timeout:
                self.send_message("Non riesco a ottenere i dati, meglio riprovare più tardi! FeelsBadMan")
                return

            lifetime_stats = json.loads(self.find(resp.text, 'var LifeTimeStats = ', ';</script>'))
            player_data = json.loads(self.find(resp.text, 'var playerData = ', ';</script>'))

            solo = player_data['p2'][9]['value'] if "p2" in player_data else "OMEGALUL"
            duo = player_data['p10'][9]['value'] if "p10" in player_data else "OMEGALUL"
            squad = player_data['p9'][9]['value'] if "p9" in player_data else "OMEGALUL"

            if user == "alessiana":
                self.send_message("["+user+"] Solo: "+solo+", Duo: "+duo+", Squad: "+squad+" KappaPride ")

            elif user == "zizory":
                if self.username != "zizory":
                    self.send_message("Questi non sono affari tuoi HotPokket")
                else:
                    self.send_whisper("["+user+"] Solo: "+solo+" , Duo: "+duo+" , Squad: "+squad+" ("+lifetime_stats[7]['Value']+" partite) KappaPride ")
            else:
                self.send_message("["+user+"] Solo: "+solo+" , Duo: "+duo+" , Squad: "+squad+" ("+lifetime_stats[7]['Value']+" partite) KappaPride ")

        except ValueError:
            if platform == "ps4" or platform == "xbox":
                self.send_message("Utente <"+user+"> non trovato BibleThump Assicurati di aver collegato il tuo account PS4 Xbox a quello di EpicGames!")
            else:
                self.send_message("Utente <"+user+"> non trovato BibleThump Sicuro di aver scritto bene?")

    def get_stats(self, user, platform):
        self.print_message("USER :"+user+" PLAT :"+platform)

        URL = "https://fortnitetracker.com/profile/"+platform+"/"+user
        if '%20' in user:
            user = user.replace('%20', ' ')
        try:
            try:
                resp = requests.get(URL, timeout=3)
            except requests.exceptions.Timeout:
                self.send_message("Non riesco a ottenere i dati, meglio riprovare più tardi! FeelsBadMan")
                return

            lifetime_stats = json.loads(self.find(resp.text, 'var LifeTimeStats = ', ';</script>'))
            player_data = json.loads(self.find(resp.text, 'var playerData = ', ';</script>'))
            solo = player_data['p2'][2]['value'] if "p2" in player_data else "0"
            duo = player_data['p10'][2]['value'] if "p10" in player_data else "0"
            squad = player_data['p9'][2]['value'] if "p9" in player_data else "0"

            if user == "alessiana":
                self.send_message("["+user+"] Solo: "+solo+", Duo: "+duo+", Squad: "+squad+" KappaPride ")

            elif user == "zizory":
                if self.username != "zizory":
                    self.send_message("Questi non sono affari tuoi HotPokket")
                else:
                    self.send_whisper("["+user+"] Solo: "+solo+" , Duo: "+duo+" , Squad: "+squad+" ("+lifetime_stats[7]['Value']+" partite) KappaPride ")
            else:
                if solo == "0":
                    solo = "OMEGALUL"
                if duo == "0":
                    duo = "OMEGALUL"
                if squad == "0":
                    squad = "OMEGALUL"

                self.send_message("["+user+"] Solo: "+solo+" , Duo: "+duo+" , Squad: "+squad+" ("+lifetime_stats[7]['Value']+" partite) KappaPride ")

        except ValueError:
            if platform == "ps4" or platform == "xbox":
                self.send_message("Utente <"+user+"> non trovato BibleThump Assicurati di aver collegato il tuo account PS4 Xbox a quello di EpicGames!")
            else:
                self.send_message("Utente <"+user+"> non trovato BibleThump Sicuro di aver scritto bene?")

    def get_today_stats(self):
        URL = "https://fortnitetracker.com/profile/pc/alessiana"
        wins = 0
        matches = 0
        kills = 0
        try:
            try:
                resp = requests.get(URL)
            except requests.exceptions.Timeout:
                self.send_message("Non riesco a ottenere i dati, meglio riprovare più tardi! FeelsBadMan")
                return

            data = json.loads(self.find(resp.text, 'var Matches = ', ';</script>'))
            today = time.strftime("20%y-%m-%d")
            for match in data:
                if today == (match['DateCollected']).split('T')[0]:
                    wins += match['Top1']
                    matches += match['Matches']
                    kills += match['Kills']
            if matches == 0:
                self.send_message("Mi dispiace, ma Alessiana non ha ancora giocato oggi FeelsBadMan")
            else:
                self.send_message(str(wins)+" vincite e "+str(kills)+" buidiulo uccisi oggi LUL")
        except:
            self.send_message("Non riesco ad accedere ai dati FeelsBadMan")

    def get_emotes(self, channel):
        URL = "https://twitch.center/customapi/bttvemotes?channel="+channel
        try:
            resp = requests.get(URL)
            self.send_message("Le emote di BTTV di "+channel+" sono: "+resp.text)
        except:
            return

    def get_random_barza(self):
        URL = "http://www.barzellette.net/"
        resp = requests.get(URL)
        soup = BeautifulSoup(resp.text, 'html.parser')
        self.speak_text(soup.find(title="Clicca per spedire questa Barzelletta").get_text())
        self.send_message("haHAA")

    def find(self, s, first, last):
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]

    def mute(self):
        self.is_muted = True

    def unmute(self):
        self.is_muted = False

    def speak_text(self, text):
        if self.is_muted:
            self.send_message("Botana non ha voglia di parlare adesso anaLUL")
        else:
            self.text_to_speech = time.time()
            pythoncom.CoInitialize()
            self.speak = wincl.Dispatch("SAPI.SpVoice")
            self.speak.Speak(text)

    def get_rand_quote(self):
        rand = randint(0, len(self.quotes)-1)
        q = self.quotes[rand]
        self.send_message("#"+str(str(q.get_index()))+": ''"+str(q.get_quote())+" '' - "+str(q.get_author())+" "+str(q.get_date()))
        if time.time() - self.text_to_speech > 20:
            if " e " in str(q.get_author()):
                threading.Thread(target=self.speak_text, args=(str(q.get_author())+" una volta dissero: "+str(q.get_quote()),)).start()
            else:
                threading.Thread(target=self.speak_text, args=(str(q.get_author())+" una volta disse: "+str(q.get_quote()),)).start()

    def get_quote(self, args):
        if int(args) > len(self.quotes):
            self.send_message("Non ho tutte quelle citazioni HotPokket")
        else:
            q = self.quotes[int(args)-1]
            self.send_message("#"+str(q.get_index())+": ''"+str(q.get_quote())+" '' - "+q.get_author()+" "+str(q.get_date()))
            if time.time() - self.text_to_speech > 20:
                if " e " in q.get_author().lower():
                    threading.Thread(target=self.speak_text, args=(str(q.get_author())+" una volta dissero: "+str(q.get_quote()),)).start()
                else:
                    threading.Thread(target=self.speak_text, args=(str(q.get_author())+" una volta disse: "+str(q.get_quote()),)).start()

    def add_quote(self, args):
        args = str(args)
        args = args.split('-')
        if len(args) != 2:
            self.send_message("A questa citazione manca l'autore: aggiungilo alla fine dopo un trattino! SeemsGood")
            return

        self.quotes.append(Quote(len(self.quotes)+1, args[0], args[1], time.strftime("[%d/%m/%Y]")))

        fields = [len(self.quotes), args[0], args[1], time.strftime("[%d/%m/%Y]")]

        with open('quotes.csv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quotechar='|', lineterminator='\n')
            writer.writerow(fields)

        self.send_message("Citazione aggiunta con indice #"+str(len(self.quotes))+" FeelsAmazingMan")
        self.get_quote(len(self.quotes))

    def get_patch(self):
        self.add_in_timeout("!patch")
        #try:
        file = open("patch.txt", "r")
        patch = file.read()
        date = os.path.getatime("patch.txt")
        print(date)
        self.send_message(self.username+", ecco l'ulima patch di Fortnite (al "+time.strftime("%d/%m/%Y")+"): "+str(patch)+" FeelsGoodMan")
        file.close()
    #    except:
    #        self.print_message("Error reading patch.txt")

    def call_command_pleb(self):
        if self.message == "!cit" and not self.is_in_timeout("!cit"):
            self.add_in_timeout("!cit")
            if self.arguments:
                if self.arguments.isdigit():
                    self.get_quote(self.arguments)
                else:
                    self.add_quote(self.arguments)
            else:
                self.get_rand_quote()

        elif self.message == "!multi":
            if "Segui" in self.multi_twitch:
                self.send_message(self.multi_twitch)
            else:
                self.send_message("Non ci sono streamer amici da guardare, per ora KappaPride")

        elif self.message == "!trap":
            MAX_TIME = 20

            if time.time() - self.tempo_trap > MAX_TIME or len(self.trap_nicks) == 0:
                self.tempo_trap = time.time()
                self.trap_nicks.append(self.username)

            elif time.time() - self.tempo_trap <= MAX_TIME:
                if self.username not in self.trap_nicks:
                    self.trap_nicks.append(self.username)
                    if len(self.trap_nicks) >= 3:
                        self.trap_count = self.trap_count + 1
                        file = open("trap.txt", "w")
                        file.write(str(self.trap_count))
                        file.close()
                        self.trap_nicks = []
                        self.tempo_trap = time.time()
                        self.send_message(str(self.trap_count) + " trappole PogChamp")
                        self.play_sound("spiketrap")

        elif self.message == "!barza" and not self.is_in_timeout("!barza"):
            threading.Thread(target=self.get_random_barza, args=()).start()

        elif self.message == "!wins" and self.is_for_current_game(self.commandsPleb["!wins"]):
            if self.arguments:
                args = self.arguments.split(' ')
                if args[-1] == "pc" or args[-1] == "ps4" or args[-1] == "xbox":
                    threading.Thread(target=self.get_stats, args=('%20'.join(args[:-1]).lower(), args[-1].lower(),)).start()
                else:
                    threading.Thread(target=self.get_stats, args=('%20'.join(args).lower(), "pc")).start()
            else:
                threading.Thread(target=self.get_stats, args=(["alessiana", "pc"])).start()

        elif self.message == "!kd" and self.is_for_current_game(self.commandsPleb["!kd"]):
            if self.arguments:
                args = self.arguments.split(' ')
                if args[-1] == "pc" or args[-1] == "ps4" or args[-1] == "xbox":
                    threading.Thread(target=self.get_kd, args=('%20'.join(args[:-1]).lower(), args[-1].lower(),)).start()
                else:
                    threading.Thread(target=self.get_kd, args=('%20'.join(args).lower(), "pc")).start()
            else:
                threading.Thread(target=self.get_kd, args=(["alessiana", "pc"])).start()

        elif self.message == "!winoggi" and not self.is_in_timeout("!winoggi") and self.is_for_current_game(self.commandsPleb["!winoggi"]):
            if self.arguments:
                return
            else:
                self.add_in_timeout("!winoggi")
                threading.Thread(target=self.get_today_stats, args=()).start()

        elif self.message == "!patch" and not self.is_in_timeout("!patch") and self.is_for_current_game(self.commandsPleb["!patch"]):
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
            file.close()

        elif self.message == "!roulette" and not self.is_in_timeout("!roulette"):
            threading.Thread(target=self.start_roulette, args=([self.username])).start()

        elif self.message == "!emotes":
            self.get_emotes(self.NICK)

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
                self.send_message("C'è lo 0% <3 tra "+self.username+" e "+self.arguments+" FeelsBadMan")
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
                self.send_message("C'è il "+str(rand)+"% <3 tra "+self.username+" e "+self.arguments+" "+emote+" ")
            else:
                threading.Thread(target=self.perform_love, args=(self.username, rand, emote)).start()

        elif self.message == "!ban" and not self.is_in_timeout("!ban"):
            if self.arguments != "":
                self.send_message(self.username+" ha bandito "+self.arguments+" dalla chat PogChamp")
            else:
                self.send_message(self.username+" non posso bandire il nulla,  stupido babbuino LUL")

        elif self.message == "!comandi" and not self.is_in_timeout("!comandi"):
            self.send_message(self.username+", la lista dei comandi è su https://pinasu.github.io/BotAna/ PogChamp")

        elif self.message == "!suoni" and not self.is_in_timeout("!suoni"):
            self.send_message(self.username+", la lista dei suoni è su https://pinasu.github.io/BotAna/ PogChamp")

        elif self.message == "!energia":
            if self.arguments:
                args = self.arguments.split(' ')
                if len(args) > 1:
                    self.send_message("Mi dispiace "+self.username+", ma puoi donare la tua energia a una sola persona FeelsBadMan")
                else:
                    self.send_message("GivePLZ "+str(args[0]).upper()+" "+self.username.upper()+" TI DONA LA SUA ENERGIA GivePLZ")
            else:
                self.send_message("GivePLZ "+self.NICK.upper()+" "+self.username.upper()+" TI DONA LA SUA ENERGIA GivePLZ")

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

            new = user[:lun+1]

        return new + "ANA";

    def word_in_timeout(self, word):
        self.words_cooldown[word] = time.time()

    def is_word_in_timeout(self, word):
        if word not in self.words_cooldown.keys() or (time.time() - self.words_cooldown[word] >= 15):
            return False
        return True

    def check_words(self, message):
        if " classic" in message.lower() and not self.is_word_in_timeout("classic"):
            self.word_in_timeout("classic")
            self.send_message("CLASSIC LUL")

        elif "anche io" in message.lower() and not self.is_word_in_timeout("anche io"):
            self.word_in_timeout("anche io")
            self.send_message("Anche io KappaPride")

        elif "omg" in message.lower() and not self.is_word_in_timeout("omg"):
            self.word_in_timeout("omg")
            self.send_message("IT'S OVER 9000 THOUSAND SwiftRage")

        elif "denti" in message.lower() and not self.is_word_in_timeout("denti"):
            if self.username == "xuneera":
                self.word_in_timeout("denti")
                self.send_message("Quali denti OMEGALUL ")

    def load_quotes(self):
        with open('quotes.csv', encoding='utf-8') as quotes:
            reader = csv.reader(quotes, delimiter=';', quotechar='|')
            for row in reader:
                self.quotes.append(Quote(row[0], row[1], row[2], row[3]))

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

    def load_image(self):
        with open('images.csv', encoding='utf-8') as imgs:
            reader = csv.reader(imgs, delimiter=';', quotechar='|')
            for row in reader:
                if len(row) == 4:
                    current = Image(row[0], row[1], row[2], row[3])
                else:
                    current = Image(row[0], row[1], row[2])
                self.images[row[0]] = current

    def load_sounds(self):
        with open('sounds.csv', encoding='utf-8') as sounds:
            reader = csv.reader(sounds, delimiter=';', quotechar='|')
            for row in reader:
                if len(row) == 2:
                    current = Sound(row[0], row[1])
                else:
                    current = Sound(row[0])
                self.sounds[row[0]] = current

    def call_image(self, name):
        for img in self.images.values():
            if name == img.get_name() and not self.image_is_in_timeout(name) and self.is_for_current_game(self.images[name]):
                self.send_message("Pro strats PogChamp")
                self.show_image(img.get_message())

    def play_sound(self, name):
        if not self.is_muted:
            pygame.mixer.pre_init(44100, 16, 2, 4096)
            pygame.mixer.init()

            sound = pygame.mixer.Sound("res/Sounds/" + name + ".wav")

            sound.play(0)
            clock = pygame.time.Clock()
            clock.tick(10)
            while pygame.mixer.music.get_busy():
                pygame.event.poll()
                clock.tick(10)
        else:
            self.send_message("Shhhhhh silenzio!")

    def call_sound(self, name):
        if name[:1] == "!":
            sname = name[1:]

        if name == "!gg":
            self.sound_add_in_timeout(name)

            if self.username not in self.gged:
                self.gged[self.username] = 0

            if time.time() - self.gged[self.username] > 7:
                self.play_sound(sname)
                self.gged[self.username] = time.time()

        elif not self.sound_is_in_timeout(name) and self.is_for_current_game(self.sounds[name]):
            self.play_sound(sname)

    def is_for_current_game(self, command):
        if not command.is_for_specific_game():
            return True
        try:
            url = 'https://api.twitch.tv/kraken/channels/'+self.get_user_id(self.NICK)
            headers = {
                'Accept': 'application/vnd.twitchtv.v5+json',
                'Client-ID': self.CLIENT_ID
            }
            resp = requests.get(url, headers=headers).json()
        except:
            self.print_message("Error getting stream game.")
            return
        curr_game = resp["game"]
        if command.get_game().lower() == curr_game.lower():
            return True
        return False

    def change_stream_title(self, title):
        url = "https://api.twitch.tv/kraken/channels/"+self.NICK+""
        params = {"Client-ID" : ""+self.CLIENT_ID+""}
        resp = requests.get(url=url, headers=params)
        game = json.loads(resp.text)['game']

        URL = 'https://api.twitch.tv/helix/channels/'+self.get_user_id(self.NICK)
        params = {
            'Client-ID : '+self.CLIENT_ID,
            'Accept: application/vnd.twitchtv.v5+json',
            'Authorization: Bearer '+self.get_app_access_token()+"",
            'Content-Type: application/json'
        }
        data = {
            "channel": {
                "status": ""+title+"",
                "game": ""+game+"",
                "channel_feed_enabled": "true"
            }
        }

        #try:
        r = requests.put(url=URL, headers=params, data=data)
        self.send_message("Titolo aggiornato in -"+title+"-")
#        except:
#            self.print_message("Error")

    def get_app_access_token(self):
        try:
            URL = 'https://id.twitch.tv/oauth2/token?client_id='+self.CLIENT_ID+'&client_secret='+self.CLIENT_SECRET+'&grant_type=client_credentials&scope=user:edit'
            resp = requests.post(URL).json()
            return resp['access_token']
        except:
            self.print_message("Error getting App Access Token.")
