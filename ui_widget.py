from PyQt5 import QtCore as QtCore
from PyQt5 import QtWidgets as QtWidgets
from PyQt5 import QtGui as QtGui
from PyQt5 import QtTest
from PyQt5.QtCore import *
import sys
import cv2
import collections
import math
import pyautogui
from tracking_thread import TrackingThread as TrackingThread
from custom_button import CustomButton
from gtts import gTTS
import os

class UIWidget(QtWidgets.QWidget):

    #Signal to update button center locations in thread
    update_button_centers = pyqtSignal(list)

    #Signal to calibrate pupil center
    calibrate_pupil_centers = pyqtSignal()

    def __init__(self, parent=None):
        super(UIWidget, self).__init__(parent)

        #Set widget params
        self.setWindowTitle("Pupil Tracker")
        self.resize(550, 400)
        self.thread = TrackingThread()
        self.button_centers = list()

        #Initialize UI -- only one init can be uncommented
        self.init_ui6() #6 button layout

        #Pass center information to thread
        self.update_button_centers.connect(self.thread.setButtonCenters)
        self.thread.request_button_centers.connect(self.establishButtonCenters)
        self.calibrate_pupil_centers.connect(self.thread.calibrate)

        #Allow for cursor movement
        self.thread.move_cursor_to_button.connect(self.moveCursor)

        #Send button centers to thread
        self.thread.startProcessing()
        self.calibrate()

    def init_ui6(self):
        self.showFullScreen()

        #Make six buttons for our layout
        self.b1 = CustomButton()
        self.b2 = CustomButton()
        self.b3 = CustomButton()
        self.b4 = CustomButton()
        self.b5 = CustomButton()
        self.b6 = CustomButton()

        #Resize the buttons - they will all be squares
        b_width = self.frameGeometry().width() / 4.0
        b_height = self.frameGeometry().height() / 4.0
        if(b_width > 300):
            b_width = 300
        if(b_height > 300):
            b_width = 300

        self.b1.setFixedSize(b_width, b_height)
        self.b2.setFixedSize(b_width, b_height)
        self.b3.setFixedSize(b_width, b_height)
        self.b4.setFixedSize(b_width, b_height)
        self.b5.setFixedSize(b_width, b_height)
        self.b6.setFixedSize(b_width, b_height)


        #Create layout for top 3 buttons
        b_layout_top = QtWidgets.QHBoxLayout()
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b1)
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b2)
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b3)
        b_layout_top.addStretch()

        #Create layout to contain text
        text_layout = QtWidgets.QHBoxLayout()
        self.print_text = QtWidgets.QLabel()
        text_layout.addStretch()
        text_layout.addWidget(self.print_text)
        text_layout.addStretch()

        #Create layout for bottom 3 buttons
        b_layout_bot = QtWidgets.QHBoxLayout()
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b4)
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b5)
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b6)
        b_layout_bot.addStretch()

        #Arrange 3 sublayouts to create whle window layout
        master_layout = QtWidgets.QVBoxLayout()
        master_layout.addStretch()
        master_layout.addLayout(b_layout_top)
        master_layout.addStretch()
        master_layout.addLayout(text_layout)
        master_layout.addStretch()
        master_layout.addLayout(b_layout_bot)
        master_layout.addStretch()
        self.setLayout(master_layout)

        #Set the beginning content for each button. The content denotes what
        #function that button will have.
        self.b1.setContent("A-E")
        self.b2.setContent("F-J")
        self.b3.setContent("K-O")
        self.b4.setContent("P-T")
        self.b5.setContent("U-Y")
        self.b6.setContent("Z, Actions")

        #Connect signals of buttons (changing menus)
        self.b1.change_menu_options.connect(self.changeMenu)
        self.b2.change_menu_options.connect(self.changeMenu)
        self.b3.change_menu_options.connect(self.changeMenu)
        self.b4.change_menu_options.connect(self.changeMenu)
        self.b5.change_menu_options.connect(self.changeMenu)
        self.b6.change_menu_options.connect(self.changeMenu)

        #Connect signals of buttons (appending text)
        self.b1.append_to_text.connect(self.appendText)
        self.b2.append_to_text.connect(self.appendText)
        self.b3.append_to_text.connect(self.appendText)
        self.b4.append_to_text.connect(self.appendText)
        self.b5.append_to_text.connect(self.appendText)
        self.b6.append_to_text.connect(self.appendText)

        #Connect signals of buttons (backspace)
        self.b1.backspace.connect(self.backspace)
        self.b2.backspace.connect(self.backspace)
        self.b3.backspace.connect(self.backspace)
        self.b4.backspace.connect(self.backspace)
        self.b5.backspace.connect(self.backspace)
        self.b6.backspace.connect(self.backspace)

        #Connect signals of buttons (clear)
        self.b1.clear_signal.connect(self.clearText)
        self.b2.clear_signal.connect(self.clearText)
        self.b3.clear_signal.connect(self.clearText)
        self.b4.clear_signal.connect(self.clearText)
        self.b5.clear_signal.connect(self.clearText)
        self.b6.clear_signal.connect(self.clearText)

        #Connect signals of buttons (Done)
        self.b1.speak_signal.connect(self.speakText)
        self.b2.speak_signal.connect(self.speakText)
        self.b3.speak_signal.connect(self.speakText)
        self.b4.speak_signal.connect(self.speakText)
        self.b5.speak_signal.connect(self.speakText)
        self.b6.speak_signal.connect(self.speakText)

    def keyPressEvent(self, event):
        if event.text() == 'q':
            QtWidgets.QApplication.quit()

        if event.text() == 'b':
            self.establishButtonCenters()

        if event.text() == 'c':
            self.calibrate()

    @pyqtSlot()
    def establishButtonCenters(self):
        ###Used to create list of button centers
        buttons = [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6]
        for button in buttons:
            #Get the center of the button
            global_center = self.mapToGlobal(button.geometry().center())
            center_tup = (global_center.x(),global_center.y())
            self.button_centers.append(center_tup)

        self.update_button_centers.emit(self.button_centers)

    @pyqtSlot(tuple)
    def moveCursor(self, cursor_dest):
        c = QtGui.QCursor()
        c.setPos(cursor_dest[0], cursor_dest[1])
        c.setShape(QtCore.Qt.CrossCursor)
        self.setCursor(c)

    @pyqtSlot(str)
    def changeMenu(self, button_content):
        if(button_content == "main"):
            self.b1.setContent("A-E")
            self.b2.setContent("F-J")
            self.b3.setContent("K-O")
            self.b4.setContent("P-T")
            self.b5.setContent("U-Y")
            self.b6.setContent("Z, Actions")

        if(button_content == "A-E"):
            self.b1.setContent("A")
            self.b2.setContent("B")
            self.b3.setContent("C")
            self.b4.setContent("D")
            self.b5.setContent("E")
            self.b6.setContent("Back")
            self.setPrevMenu("main")

        if(button_content == "F-J"):
            self.b1.setContent("F")
            self.b2.setContent("G")
            self.b3.setContent("H")
            self.b4.setContent("I")
            self.b5.setContent("J")
            self.b6.setContent("Back")
            self.setPrevMenu("main")

        if(button_content == "K-O"):
            self.b1.setContent("K")
            self.b2.setContent("L")
            self.b3.setContent("M")
            self.b4.setContent("N")
            self.b5.setContent("O")
            self.b6.setContent("Back")
            self.setPrevMenu("main")


        if(button_content == "P-T"):
            self.b1.setContent("P")
            self.b2.setContent("Q")
            self.b3.setContent("R")
            self.b4.setContent("S")
            self.b5.setContent("T")
            self.b6.setContent("Back")
            self.setPrevMenu("main")

        if(button_content == "U-Y"):
            self.b1.setContent("U")
            self.b2.setContent("V")
            self.b3.setContent("W")
            self.b4.setContent("X")
            self.b5.setContent("Y")
            self.b6.setContent("Back")
            self.setPrevMenu("main")

        if(button_content == "Z, Actions"):
            self.b1.setContent("Z")
            self.b2.setContent("Numbers")
            self.b3.setContent("Symbols")
            self.b4.setContent("Space")
            self.b5.setContent("Shift, Delete, Clear, Done")
            self.b6.setContent("Back")
            self.setPrevMenu("main")

        if(button_content == "Shift, Delete, Clear, Done"):
            self.b1.setContent("Shift")
            self.b2.setContent("Delete")
            self.b3.setContent("Clear")
            self.b4.setContent("Done")
            self.b5.setContent("")
            self.b6.setContent("Back")
            self.setPrevMenu("Z, Actions")

        if(button_content == "Numbers"):
            self.b1.setContent("0-4")
            self.b2.setContent("5-9")
            self.b3.setContent("")
            self.b4.setContent("")
            self.b5.setContent("")
            self.b6.setContent("Back")
            self.setPrevMenu("Z, Actions")

        if(button_content == "0-4"):
            self.b1.setContent("0")
            self.b2.setContent("1")
            self.b3.setContent("2")
            self.b4.setContent("3")
            self.b5.setContent("4")
            self.b6.setContent("Back")
            self.setPrevMenu("Z, Actions")

        if(button_content == "5-9"):
            self.b1.setContent("5")
            self.b2.setContent("6")
            self.b3.setContent("7")
            self.b4.setContent("8")
            self.b5.setContent("9")
            self.b6.setContent("Back")
            self.setPrevMenu("Z, Actions")

    @pyqtSlot(str)
    def appendText(self, val):
        if(val == 'Space'):
            val = " "
        text = self.print_text.text() + val
        self.print_text.setText(text)

    @pyqtSlot()
    def backspace(self):
        if(len(self.print_text.text()) > 0):
                text = self.print_text.text() [:-1]
                self.print_text.setText(text)

    @pyqtSlot()
    def clearText(self):
        text = ""
        self.print_text.setText(text)


    @pyqtSlot()
    def speakText(self):
        tts = gTTS(text=self.print_text.text(), lang='en')
        tts.save("text.mp3")
        os.system("afplay text.mp3")
        self.clearText()


    @pyqtSlot()
    def calibrate(self):
        txt = self.print_text.text()
        self.print_text.setText('Look here\nto calibrate.')
        self.print_text.setStyleSheet('color: red; font: bold 24pt')
        QtTest.QTest.qWait(3000)
        self.calibrate_pupil_centers.emit()
        self.print_text.setText('Calibrated')
        QtTest.QTest.qWait(1000)
        self.print_text.setStyleSheet('color: black; font: 20pt')
        self.print_text.setText(txt)

    def setPrevMenu(self, prev_menu):
       self.b1.setPrevMenu(prev_menu)
       self.b2.setPrevMenu(prev_menu)
       self.b3.setPrevMenu(prev_menu)
       self.b4.setPrevMenu(prev_menu)
       self.b5.setPrevMenu(prev_menu)
       self.b6.setPrevMenu(prev_menu)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = UIWidget()
    widget.show()
    sys.exit(app.exec_())

