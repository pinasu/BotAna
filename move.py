#Key pressing
import ctypes


SendInput = ctypes.windll.user32.SendInput

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

def mouse(self, x, y, code=''):
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
    if type == 'Mouse':
        self.mouse(0,0,'Press' + code)
        time.sleep(tim)
        self.lock3.acquire()
        if self.move_dict[tmp] == 1:
            self.mouse(0,0,'Release' + code)
        self.move_dict[tmp] = self.move_dict[tmp] - 1
        self.lock3.release()
    elif type == 'Key':
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

    if text.lower() == 'q':
        self.press_key(0x21) #F
        self.release_key(0x21) #F
        time.sleep(0.5)
        self.mouse(0,0,'PressLeft')
        self.mouse(0,0,'ReleaseLeft')
    elif text.lower() == 'g':
        self.press_key(0x22) #g
        self.release_key(0x22)
        time.sleep(0.5)
        self.mouse(0,0,'PressLeft')
        self.mouse(0,0,'ReleaseLeft')
    #elif text.lower() == 'f':
        #TODO piazzare scale
        #self.press_key(0x14) #T
        #self.release_key(0x14)
        #time.sleep(0.5)
        #self.mouse(0,0,'PressLeft')
    elif text.lower() == '1':
        self.press_key(0x02) #1
        self.release_key(0x02)
        # self.mouse(0,0,'PressLeft')
        self.press_whait_release('Mouse', 5, 'Left')
    elif text.lower() == '2':
        self.press_key(0x03) #2
        self.release_key(0x03)
        self.press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '3':
        self.press_key(0x04) #3
        self.release_key(0x04)
        self.press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '4':
        self.press_key(0x05) #4
        self.release_key(0x05)
        self.press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '5':
        self.press_key(0x06) #5
        self.release_key(0x06)
        self.press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == '6':
        self.press_key(0x2C) #Z
        self.release_key(0x2C)
        self.press_whait_release('Mouse', 3, 'Left')
    elif text.lower() == 'u':
        self.mouse(0,-1000) #Top
    elif text.lower() == 'j':
        self.mouse(0,1000) #Bottom
    elif text.lower() == 'h':
        self.mouse(-1000,0) #Left
    elif text.lower() == 'k':
        self.mouse(1000,0) #Right
    elif text.lower() == 'w':
        self.press_whait_release('Key', 5, 0x11)
        # self.press_key(0x11)
    elif text.lower() == 's':
        self.press_whait_release('Key', 5, 0x1F)
        # self.press_key(0x1F)
    elif text.lower() == 'a':
        self.press_whait_release('Key', 5, 0x1E)
        # self.press_key(0x1E)
    elif text.lower() == 'd':
        self.press_whait_release('Key', 5, 0x20)
        # self.press_key(0x20)
    elif text.lower() == 'm':
        self.press_key(0x32) #4
        self.release_key(0x32)
    elif text.lower() == 'b':
        self.press_key(0x39) #space
        self.release_key(0x39)
    elif text.lower() == 'e':
        self.press_key(0x12) #e
        self.release_key(0x12)
    elif text.lower() == 'x':
        self.press_key(0x01) #esc
        self.release_key(0x01)
    elif text.lower() == 'r':
        self.mouse_move_abs(1920 + 1790, 1050)
        # self.mouse_move_from_bottom_right(130, 30)
        self.mouse(0,0,'PressLeft')
        self.mouse(0,0,'ReleaseLeft')
    elif text.lower() == 't':
        self.mouse_move_abs(1920 + 1700, 950)
        # self.mouse_move_from_bottom_right(220, 130)
        self.mouse(0,0,'PressLeft')
        self.mouse(0,0,'ReleaseLeft')
