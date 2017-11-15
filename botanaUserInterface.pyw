import sys, os, time
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QTextCursor
from botana import BotAna
import threading

class WindowTwo(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.isInTest = False
        self.parent = parent
        self.parent.activateGreenScreenButton(False)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(450,450)
        self.setPosition()
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setStyleSheet("WindowTwo{background-color:#0f0;}")
        self.setWindowTitle('BotAnaImage')
        self.setWindowIcon(QtGui.QIcon('res/Gui/icon.ico'))
        self.img = QtWidgets.QLabel()
        
        v_box = QtWidgets.QVBoxLayout()
        v_box.setContentsMargins(0,0,0,0)
        v_box.addWidget(self.img)
        self.setLayout(v_box)
        self.show()

    def setPosition(self):
        if (self.parent.pos().x() - self.width()) >= 0:
            self.move(self.parent.pos().x() - 450,self.parent.pos().y())
        else:
            self.move(0,0)

    def closeEvent(self, event):
        self.parent.activateGreenScreenButton(True)
        self.setButtonTestImageActive(False)
        event.accept()

    def setButtonTestImageActive(self, bo):
        self.isInTest = bo
        self.parent.setButtonTestImage(bo)

    def triggerTestImage(self):
        if not self.isInTest:
            self.img.setPixmap(QtGui.QPixmap("res/ShowImages/test.png"))
            self.setButtonTestImageActive(True)
        else:
            self.img.clear()
            self.setButtonTestImageActive(False)
        

    def showImage(self, path):
        if self.isVisible() and not self.isInTest:
            threading.Thread(target=self.process, args=[path]).start()

    def process(self, path):
        self.img.setPixmap(QtGui.QPixmap(path))
        time.sleep(10)
        if not self.isInTest:
            self.img.clear()

class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.secondWind = WindowTwo(self)
        self.bot = BotAna()
        self.bot.sign.connect(self.printOnTextArea)
        self.bot.sign2.connect(self.showImage)
        self.bot.start()

    def init_ui(self):

        sshFile="res/style.css"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())

        self.setWindowIcon(QtGui.QIcon('res/Gui/icon.ico'))
        
        self.setGeometry(0,0,950, 450)
        self.move(600, 200)
        self.setMinimumSize(700,300)
        self.logo = QtWidgets.QLabel()
        self.logo.setObjectName("logo")
        self.logo.setPixmap(QtGui.QPixmap('res/Gui/botana.png'))

        self.creators = QtWidgets.QLabel()
        self.creators.setPixmap(QtGui.QPixmap('res/Gui/creators.png'))
        
        self.textarea = QtWidgets.QTextEdit()
        self.textarea.setReadOnly(True)
        self.textarea.setObjectName("textarea")
        self.inputText = QtWidgets.QLineEdit()
        self.inputText.setObjectName("inputText")
        self.sendButton = QtWidgets.QPushButton('INVIA')
        self.sendButton.setCursor (Qt.PointingHandCursor)
        self.sendButton.setObjectName("sendButton")
        self.sendButton.setProperty('class','button')
        self.greenScreenButton = QtWidgets.QPushButton("")
        self.greenScreenButton.setIcon(QtGui.QIcon('res/Gui/greenScreenButton.png'))
        self.greenScreenButton.setIconSize(QtCore.QSize(40,40))
        self.greenScreenButton.setCursor (Qt.PointingHandCursor)
        self.greenScreenButton.setProperty('class','button gridButton')
        self.logErrorButton = QtWidgets.QPushButton("")
        self.logErrorButton.setIcon(QtGui.QIcon('res/Gui/errorLogButton.png'))
        self.logErrorButton.setIconSize(QtCore.QSize(40,40))
        self.logErrorButton.setCursor (Qt.PointingHandCursor)
        self.logErrorButton.setProperty('class','button gridButton')
        self.msgLog = QtWidgets.QMessageBox()
        self.msgLog.setIcon(QMessageBox.Information)
        self.msgLog.setText("Nessun log di errore presente")
        self.msgLog.setWindowTitle("Info")
        self.msgLog.setWindowIcon(QtGui.QIcon('res/Gui/icon.ico'))
        self.testImageGreenScreen = QtWidgets.QPushButton("")
        self.testImageGreenScreen.setIcon(QtGui.QIcon('res/Gui/testImageGreenScreen.png'))
        self.testImageGreenScreen.setIconSize(QtCore.QSize(40,40))
        self.testImageGreenScreen.setCursor (Qt.PointingHandCursor)
        self.testImageGreenScreen.setProperty('class','button gridButton')
        self.restartBtn = QtWidgets.QPushButton("")
        self.restartBtn.setIcon(QtGui.QIcon('res/Gui/restart.png'))
        self.restartBtn.setIconSize(QtCore.QSize(40,40))
        self.restartBtn.setCursor (Qt.PointingHandCursor)
        self.restartBtn.setProperty('class','button gridButton')

        g_box = QtWidgets.QGridLayout()
        g_box.addWidget(self.greenScreenButton, 0 , 0)
        g_box.addWidget(self.testImageGreenScreen, 0 , 1)
        g_box.addWidget(self.logErrorButton, 1 , 0)
        g_box.addWidget(self.restartBtn, 1 , 1)

        v_box = QtWidgets.QVBoxLayout()
        v_box.setContentsMargins(7,7,14,0)
        v_box.addWidget(self.logo)
        v_box.addLayout(g_box)
        v_box.addStretch()
        v_box.addWidget(self.creators)

        h_box2 = QtWidgets.QHBoxLayout()
        h_box2.addWidget(self.inputText)
        h_box2.addWidget(self.sendButton)
        

        v_box2 = QtWidgets.QVBoxLayout()
        v_box2.addWidget(self.textarea)
        v_box2.addLayout(h_box2)
        

        h_box = QtWidgets.QHBoxLayout()
        h_box.addLayout(v_box)
        h_box.addLayout(v_box2)

        self.setLayout(h_box)
        self.setWindowTitle('BotAna')

        self.sendButton.clicked.connect(self.btn_click)
        self.greenScreenButton.clicked.connect(self.openGreenScreen)
        self.logErrorButton.clicked.connect(self.openErrorLog)
        self.testImageGreenScreen.clicked.connect(self.triggerTestImage)
        self.restartBtn.clicked.connect(self.restart)

        self.show()

    def restart(self):
        self.bot.restart()

    def setButtonTestImage(self, active):
        if active:
            self.testImageGreenScreen.setIcon(QtGui.QIcon('res/Gui/testImageGreenScreenX.png'))
        else:
            self.testImageGreenScreen.setIcon(QtGui.QIcon('res/Gui/testImageGreenScreen.png'))

    def triggerTestImage(self):
        self.secondWind.triggerTestImage()

    def openErrorLog(self):
        if os.path.exists('LogError.txt'):
            os.startfile('LogError.txt')
        else:
            self.msgLog.exec_()

    def activateGreenScreenButton(self, bo):
        self.greenScreenButton.setEnabled(bo)
        self.testImageGreenScreen.setEnabled(not bo)

    def openGreenScreen(self):
        self.secondWind = WindowTwo(self)

    def showImage(self, path):
        self.secondWind.showImage(path)

    def closeEvent(self, event):
        self.secondWind.close()
        event.accept()

    def printOnTextArea(self, msg):
        if(msg != ""):
            self.textarea.append(msg)

    def keyPressEvent(self, event):
        if(event.key() == Qt.Key_Return and self.inputText.hasFocus()):
            self.btn_click()

    def btn_click(self):
        msg = self.inputText.text()
        if(msg != ""):
            self.bot.send_message(msg)
            self.inputText.setText("")


app = QtWidgets.QApplication(sys.argv)
a_window = Window()
os._exit(app.exec_())

