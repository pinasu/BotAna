import sys, os, time
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from botana import BotAna
import threading

class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.bot = BotAna()
        self.bot.sign.connect(self.printOnTextArea)
        self.bot.start()

    def init_ui(self):

        sshFile="res/style.css"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())

        self.setWindowIcon(QtGui.QIcon('res/icon.png'))
        
        self.setGeometry(400,200,950, 450)
        self.setMinimumSize(700,300)
        self.logo = QtWidgets.QLabel()
        self.logo.setObjectName("logo")
        self.logo.setPixmap(QtGui.QPixmap('res/botana.png'))

        self.creators = QtWidgets.QLabel()
        self.creators.setPixmap(QtGui.QPixmap('res/creators.png'))
        
        self.textarea = QtWidgets.QTextEdit()
        self.textarea.setReadOnly(True)
        self.textarea.setObjectName("textarea")
        self.inputText = QtWidgets.QLineEdit()
        self.inputText.setObjectName("inputText")
        self.sendButton = QtWidgets.QPushButton('INVIA')
        self.sendButton.setCursor (Qt.PointingHandCursor)
        self.sendButton.setObjectName("sendButton")


        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(self.logo)
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

        self.show()

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

