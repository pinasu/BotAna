#Bot useful functions

#Useful imports
import config, socket, time, json, requests, datetime

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
    url = "https://api.twitch.tv/kraken/streams/"+config.NICK+""
    params = {"Client-ID" : ""+config.CLIENT_ID+""}
    resp = requests.get(url=url, headers=params)
    online = json.loads(resp.text)
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
                            time.sleep(1)
                            functions.send_message(s, "PS: puoi comunque attaccarte a StoDiscord nel frattempo: https://goo.gl/2QSx3V KappaPride")
                            time.sleep(300)

        resp = requests.get(url=url, headers=params)
        online = json.loads(resp.text)

        #Stockhausen always stream at 20, set for how much time will the Bot sleep
        if datetime.datetime.now().strftime('%H') == "19":
            offline = False

        if offline:
            time.sleep(900)
        else:
            time.sleep(300)

#Function to answer mod command
def call_command_mod(socket):
    if config.username not in config.mods:
        send_message(socket, "Mi dispiace, ma questo comando non è per te.")
    else:
            raffled = ""
            
            if config.message == "!restart":
                os.system("python bot_ana.py")
                exit(0)

            elif config.message == "!stop":
                send_message("HeyGuys")
                exit(0)

            elif config.message == "!clean":
                file = open("players.txt", "w")
                file.write("")
                config.players = []

            elif config.message == "!raffle":
                if len(config.players) > 3:
                    raffle = random.sample(config.players, 3)
                    raffled = ', '.join(raffle)
                    config.players = set(config.players) - set(raffle)
                else:
                    raffled = ', '.join(config.players)
                    config.players = []
                send_message(socket, "Ho scelto "+raffled+" PogChamp")
            
            elif config.message == "!pickone":
                if len(config.players) > 0:
                    raffle = random.sample(config.players, 1)
                    raffled = ", ".join(raffle)
                    send_message(socket, "Ho scelto "+raffled+" PogChamp")
                else:
                    send_message(socket, "Non ci sono persone da scegliere BibleThump")

            elif config.message == "!comandi":
                cmd = config.username+", i comandi disponibili sono [ "
                #Commands for everyone
                for r in config.commands:
                    cmd+="'"+p+", "
                for r in config.mods_commands:
                    #Last command in the dict?
                    if list(config.commands.keys())[-1] == p:
                        cmd+="'"+p+"' "
                    else:
                        cmd+="'"+p+", "
                send_message(socket, cmd+" ]")

            elif config.message == "!suoni":
                get_sounds(socket)

#Function to check if message is in cooldown
def process_command_pleb(socket):
    if config.message not in config.used or time.time()-config.used[command] > config.command_coold:
        if command != "!play" and command != "!energia":
            config.used[command] = time.time()

        call_command_pleb(socket)

#Function to answer pleb command
def call_command_pleb(socket):
    if config.message == "!roulette":
        send_message(socket, "Punto la pistola nella testa di "+config.username+"... monkaS")
        time.sleep(5)
        doa = randint(1, 10)
        if doa <= 5:
            send_message(socket, "Il corpo di "+config.username+" giace in chat monkaS Qualcuno può venire a pulire? LUL")
        else:
            send_message(socket, "La pistola si è inceppata! PogChamp "+config.username+" è sopravvissuto Kreygasm")

    elif config.message == "!play":
        if config.username not in config.players:
            config.players.append(config.username)
            send_message(socket, config.username+", ti ho aggiunto alla lista dei viewers che vogliono giocare PogChamp")

    elif config.message == "!players":
        if config.players:
            pl = ', '.join(config.players)
            send_message(socket, pl+" vogliono giocare!")
            if config.username in mods:
                config.players = []
        else:
            send_message(socket, "Non vuole giocare nessuno BibleThump")

    elif config.message == "maledizione":
        file = open("maledizioni.txt", "r")
        maled = file.read()
        count = int(maled) + 1
        file.close()

        send_message(socket, "Ovviamente la safe zone è dall'altra parte (x"+str(count)+" LUL) Never lucky BabyRage")

        file = open("maledizioni.txt", "w")
        file.write(str(count))

    elif config.message == "!suicidio":
        if config.username == config.NICK:
            send_message(socket, "Imperatore mio Imperatore, non posso permetterti di farlo! BibleThump")
        elif config.username in config.mods:
            send_message(socket, config.username+", l'Imperatore Alessiana non ha ancora finito con te! anaLove")
        else:
            send_message(socket, "/timeout "+config.username+" 60")
            send_message(socket, config.username+" si è suicidato monkaS Press F to pay respect BibleThump")

    elif config.message == "!8ball":
        new_ball = random.choice(config.ball_choices)

        #Alessiana rompeva le palle ogni volta che usciva due volte la stessa
        while new_ball == config.old_ball:
            new_ball = random.choice(config.ball_choices)

        send_message(socket, new_ball)
        config.old_ball = new_ball

    elif config.message == "!ban":
        send_message(socket, config.username+" ha bannato "+config.arguments+" PogChamp")

    elif config.message == "!suoni":
        get_sounds(socket)

#Get sounds list
def get_sounds(socket):
    send_message(socket, config.username+", i suoni disponibili sono "+str(config.sounds))
