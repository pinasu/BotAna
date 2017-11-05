import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from botana import BotAna
import threading

class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.bot = BotAna(self)
        self.t = threading.Thread(target=self.bot.test, args=())
        self.t.start()

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
        self.textarea = QtWidgets.QPlainTextEdit()
        self.textarea.setReadOnly(1)
        self.textarea.setObjectName("textarea")
        self.inputText = QtWidgets.QLineEdit()
        self.inputText.setObjectName("inputText")
        self.sendButton = QtWidgets.QPushButton('INVIA')
        self.sendButton.setCursor (Qt.PointingHandCursor)
        self.sendButton.setObjectName("sendButton")


        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(self.logo)
        v_box.addStretch()

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
            self.textarea.insertPlainText(msg + "\n")

    def keyPressEvent(self, event):
        if(event.key() == Qt.Key_Return and self.inputText.hasFocus()):
            self.btn_click()

    def btn_click(self):
        msg = self.inputText.text()
        if(msg != ""):
            self.bot.sendMessage(msg)
            self.textarea.insertPlainText("BotAna_: " + msg + "\n")
            self.inputText.setText("")


app = QtWidgets.QApplication(sys.argv)
a_window = Window()

sys.exit(app.exec_())
