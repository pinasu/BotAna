#Key pressing
import ctypes, threading, time

SendInput = ctypes.windll.user32.SendInput

lock3 = threading.RLock()

move_dict = dict()

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [('wVk', ctypes.c_ushort),
                ('wScan', ctypes.c_ushort),
                ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong),
                ('dwExtraInfo', PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [('uMsg', ctypes.c_ulong),
                ('wParamL', ctypes.c_short),
                ('wParamH', ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [('dx', ctypes.c_long),
                ('dy', ctypes.c_long),
                ('mouseData', ctypes.c_ulong),
                ('dwFlags', ctypes.c_ulong),
                ('time',ctypes.c_ulong),
                ('dwExtraInfo', PUL)]

class Input_I(ctypes.Union):
    _fields_ = [('ki', KeyBdInput),
                 ('mi', MouseInput),
                 ('hi', HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [('type', ctypes.c_ulong),
                ('ii', Input_I)]


#Key pressing
# non funge su doppio schermo, prende sempre solo il primo
def mouse_move_from_bottom_right(x, y):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    x = int((ctypes.windll.user32.GetSystemMetrics(0) - x) * (65536/ctypes.windll.user32.GetSystemMetrics(0))+1)
    y = int((ctypes.windll.user32.GetSystemMetrics(1) - y) * (65536/ctypes.windll.user32.GetSystemMetrics(1))+1)
    ii_.mi = MouseInput(x, y, 0, 0x0001 | 0x8000, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def mouse_move_abs(x, y):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    x = int(x*(65536/ctypes.windll.user32.GetSystemMetrics(0))+1)
    y = int(y*(65536/ctypes.windll.user32.GetSystemMetrics(1))+1)
    ii_.mi = MouseInput(x, y, 0, 0x0001 | 0x8000, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def mouse(x, y, code=''):
    if code == 'PressLeft':
        cd = 0x0002;
    elif code == 'ReleaseLeft':
        cd = 0x0004;
    elif code == 'PressRight':
        cd = 0x0008;
    elif code == 'ReleaseRight':
        cd = 0x0010;
    else:
        cd = 0x0001;

    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(x, y, 0, cd, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def press_whait_release(type, time, code):
    threading.Thread(target=thread_press, args=(type, time, code,)).start()

def thread_press(type, tim, code):
    tmp = str(code)
    lock3.acquire()
    if tmp in move_dict:
        move_dict[tmp] = move_dict[tmp] + 1
    else:
        move_dict[tmp] = 1
    lock3.release()
    if type == 'Mouse':
        mouse(0,0,'Press' + code)
        time.sleep(tim)
        lock3.acquire()
        if move_dict[tmp] == 1:
            mouse(0,0,'Release' + code)
        move_dict[tmp] = move_dict[tmp] - 1
        lock3.release()
    elif type == 'Key':
        if code in [0x11, 0x1F, 0x1E, 0x20]: # w a s d
            press_key(0x2A) #shift per correre
        press_key(code)
        time.sleep(tim)
        lock3.acquire()
        if move_dict[tmp] == 1:
            if code in [0x11, 0x1F, 0x1E, 0x20]: # w a s d
                release_key(0x2A) #shift per correre
            release_key(code)
        move_dict[tmp] = move_dict[tmp] - 1
        lock3.release()

def trigger_key(text):
    # directx scan codes http://www.gamespp.com/directx/directInputKeyboardScanCodes.html

    if not len(text) == 1:
        return

    if text.lower() == 'q':
        press_key(0x21) #F
        release_key(0x21) #F
        time.sleep(0.5)
        mouse(0,0,'PressLeft')
        mouse(0,0,'ReleaseLeft')
    elif text.lower() == 'g':
        press_key(0x22) #g
        release_key(0x22)
        time.sleep(0.5)
        mouse(0,0,'PressLeft')
        mouse(0,0,'ReleaseLeft')
    #elif text.lower() == 'f':
        #TODO piazzare scale
        #press_key(0x14) #T
        #release_key(0x14)
        #time.sleep(0.5)
        #mouse(0,0,'PressLeft')
    elif text.lower() == '1':
        press_key(0x02) #1
        release_key(0x02)
        # mouse(0,0,'PressLeft')
        press_whait_release('Mouse', 5, 'Left')
    elif text.lower() == '2':
        press_key(0x03) #2
        release_key(0x03)
        press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '3':
        press_key(0x04) #3
        release_key(0x04)
        press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '4':
        press_key(0x05) #4
        release_key(0x05)
        press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '5':
        press_key(0x06) #5
        release_key(0x06)
        press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '6':
        press_key(0x2C) #Z
        release_key(0x2C)
        press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == 'u':
        mouse(0,-1000) #Top
    elif text.lower() == 'j':
        mouse(0,1000) #Bottom
    elif text.lower() == 'h':
        mouse(-1000,0) #Left
    elif text.lower() == 'k':
        mouse(1000,0) #Right
    elif text.lower() == 'w':
        press_whait_release('Key', 5, 0x11)
        # press_key(0x11)
    elif text.lower() == 's':
        press_whait_release('Key', 5, 0x1F)
        # press_key(0x1F)
    elif text.lower() == 'a':
        press_whait_release('Key', 5, 0x1E)
        # press_key(0x1E)
    elif text.lower() == 'd':
        press_whait_release('Key', 5, 0x20)
        # press_key(0x20)
    elif text.lower() == 'm':
        press_key(0x32) #4
        release_key(0x32)
    elif text.lower() == 'b':
        press_key(0x39) #space
        release_key(0x39)
    elif text.lower() == 'e':
        press_key(0x12) #e
        release_key(0x12)
    elif text.lower() == 'x':
        press_key(0x01) #esc
        release_key(0x01)
    elif text.lower() == 'r':
        mouse_move_abs(1920 + 1790, 1050)
        # mouse_move_from_bottom_right(130, 30)
        mouse(0,0,'PressLeft')
        mouse(0,0,'ReleaseLeft')
    elif text.lower() == 't':
        mouse_move_abs(1920 + 1700, 950)
        # mouse_move_from_bottom_right(220, 130)
        mouse(0,0,'PressLeft')
        mouse(0,0,'ReleaseLeft')
