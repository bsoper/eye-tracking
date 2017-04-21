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
        """**Deprecated** Used to initialize user interface"""

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
        """Used to initialize a user interface with 6 buttons

        **This is the main initialization for our project -- initialization
        with any other button amounts will require considerable code alterations
        throughout rest of project**

        """
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

        self.b1.setFixedSize(b_width, b_height)
        self.b2.setFixedSize(b_width, b_height)
        self.b3.setFixedSize(b_width, b_height)
        self.b4.setFixedSize(b_width, b_height)
        self.b5.setFixedSize(b_width, b_height)
        self.b6.setFixedSize(b_width, b_height)

        #Create screen layout
        self.createSixButtonLayout()

        #Set the beginning content for each button. The content denotes what
        #function that button will have.
        self.setMenuButtonContent("Letters","Numbers","Space","Confirm",
                                    "Phrases","Backspace")

        #Connect signals of buttons
        self.connectChangeMenuOptionsSignal()
        self.connectAppendToTextSignal()
        self.connectBackspaceSignal()
        self.connectClearSignal()
        self.connectSpeakTextSignal()

    def keyPressEvent(self, event):
        """
        Called when a key is pressed while ui is in focus. Overloaded Qt
        function -- do not usually call this ourselves.

        :param event: The key press event which triggers this function.
        """
        if event.text() == 'q':
            QtWidgets.QApplication.quit()

        if event.text() == 'b':
            self.establishButtonCenters()

        if event.text() == 'c':
            self.calibrate()

    @pyqtSlot()
    def establishButtonCenters(self):
        """Calculates the center positions of the six buttons on screen.

        Emits the update_button_centers

        .. seealso::update_button_centers
        """

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
        """Moves the mouse cursor to the destination

        :param cursor_dest: The x,y pixel destination of mouse cursor
        :type cursor_dest: tuple: (float,float)
        """
        c = QtGui.QCursor()
        c.setPos(cursor_dest[0], cursor_dest[1])
        #c.setShape(QtCore.Qt.CrossCursor)
        #self.setCursor(c)


    @pyqtSlot(str)
    def changeMenu(self, button_content):
        """The mechanism by which we change the menu currently displayed on screen

        :param button_content: The function associated with the button that emitted this signal
        :type button_content: str
        """
        if(button_content == "main"):
            self.setMenuButtonContent("Letters","Numbers","Space",
                    "Confirm","Phrases","Backspace")

        if(button_content == "Letters"):
            self.setMenuButtonContent("A-E","F-J","K-O","P-T","Back","U-Z")
            self.setPrevMenu("main")

        if(button_content == "A-E"):
            self.setMenuButtonContent("A","B","C","D","Back","E")
            self.setPrevMenu("Letters")

        if(button_content == "F-J"):
            self.setMenuButtonContent("F","G","H","I","Back","J")
            self.setPrevMenu("Letters")

        if(button_content == "K-O"):
            self.setMenuButtonContent("K","L","M","N","Back","O")
            self.setPrevMenu("Letters")

        if(button_content == "P-T"):
            self.setMenuButtonContent("P","Q","R","S","Back","T")
            self.setPrevMenu("Letters")

        if(button_content == "U-Z"):
            self.setMenuButtonContent("U","V","W","Y","Back","X,Z")
            self.setPrevMenu("Letters")

        if(button_content == "X,Z"):
            self.setMenuButtonContent("X","Z","","","Back","")
            self.setPrevMenu("U-Z")

        if(button_content == "Numbers"):
            self.setMenuButtonContent("0-4","5-9","Punctuation","Symbols","Back",
            "Additional Symbols")
            self.setPrevMenu("main")

        if(button_content == "0-4"):
            self.setMenuButtonContent("0","1","2",'3','Back','4')
            self.setPrevMenu("Numbers")

        if(button_content == "5-9"):
            self.setMenuButtonContent('5','6','7','8','Back','9')
            self.setPrevMenu("Numbers")

        if(button_content == "Punctuation"):
            self.setMenuButtonContent('. ',', ','! ','? ','Back','"')
            self.setPrevMenu("Numbers")

        if(button_content == "Symbols"):
            self.setMenuButtonContent('@','#','$','%','Back','&')
            self.setPrevMenu("Numbers")

        if(button_content == "Additional Symbols"):
            self.setMenuButtonContent('(',')','/','*','Back','-')
            self.setPrevMenu('Numbers')

        if(button_content == "Phrases"):
            self.setMenuButtonContent('Greetings','Emotions','Responses',
                    '','Back','')
            self.setPrevMenu('main')

        if(button_content == "Greetings"):
            self.setMenuButtonContent('Hello ','Good Morning ','Good Afternoon ',
                    'Goodnight ', 'Back', 'Goodbye ')
            self.setPrevMenu('Phrases')

        if(button_content == "Emotions"):
            self.setMenuButtonContent('Good ','Bad ','Happy ','Sad ','Back','Angry ')
            self.setPrevMenu('Phrases')

        if(button_content == "Responses"):
            self.setMenuButtonContent('Yes ', 'I Don\'t know ', 'No ','Okay ',
                    'Back','Thank You ')
            self.setPrevMenu('Phrases')


    @pyqtSlot(str)
    def appendText(self, val):
        """Slotted Qt Function: Appends passed text to the communication string

        :param val: The string to append to the communication string
        :type val: str
        """
        if(val == 'Space'):
            val = " "
        text = self.print_text.text() + val
        self.print_text.setText(text.upper())

    @pyqtSlot()
    def backspace(self):
        """
        Slotted Qt Function: Backspaces the last character added to communication string
        """
        if(len(self.print_text.text()) > 0):
                text = self.print_text.text() [:-1]
                self.print_text.setText(text)

    @pyqtSlot()
    def clearText(self):
        """
        Slotted Qt Function: Completely clears communication string
        """
        text = ""
        self.print_text.setText(text)


    @pyqtSlot()
    def speakText(self):
        """
        Slotted Qt Function: Calls TTS function to speak communication string
        """
        if self.print_text.text() == '':
            return
        tts = gTTS(text=self.print_text.text(), lang='en')
        tts.save("text.mp3")
        os.system("afplay text.mp3")
        self.clearText()


    @pyqtSlot()
    def calibrate(self):
        """
        Slotted Qt Function: Recalibrates pupil tracker in case head moves too
        much to accurately track eyes
        """
        txt = self.print_text.text()
        self.print_text.setText('Look here\nto calibrate.')
        self.print_text.setStyleSheet('color: red; font: bold 24pt')
        while(not self.thread.found_face):
            QtTest.QTest.qWait(1000)
        QtTest.QTest.qWait(3000)
        self.calibrate_pupil_centers.emit()
        self.print_text.setText('Calibrated')
        QtTest.QTest.qWait(1000)
        self.print_text.setStyleSheet('color: black; font: 36pt')
        self.print_text.setText(txt)

    def setPrevMenu(self, prev_menu):
        """
        Sets the previous menu of the buttons in the current menu

        :param prev_menu: The previous menu to set for button
        :type prev_menu: str
        """
        self.b1.setPrevMenu(prev_menu)
        self.b2.setPrevMenu(prev_menu)
        self.b3.setPrevMenu(prev_menu)
        self.b4.setPrevMenu(prev_menu)
        self.b5.setPrevMenu(prev_menu)
        self.b6.setPrevMenu(prev_menu)

    def connectClearSignal(self):
        """
        Connects the clear_signal signal to all buttons
        """
        self.b1.clear_signal.connect(self.clearText)
        self.b2.clear_signal.connect(self.clearText)
        self.b3.clear_signal.connect(self.clearText)
        self.b4.clear_signal.connect(self.clearText)
        self.b5.clear_signal.connect(self.clearText)
        self.b6.clear_signal.connect(self.clearText)

    def connectBackspaceSignal(self):
        """
        Connects the backspace signal to all buttons
        """
        self.b1.backspace.connect(self.backspace)
        self.b2.backspace.connect(self.backspace)
        self.b3.backspace.connect(self.backspace)
        self.b4.backspace.connect(self.backspace)
        self.b5.backspace.connect(self.backspace)
        self.b6.backspace.connect(self.backspace)

    def connectAppendToTextSignal(self):
        """
        Connects the append_to_text signal to all buttons
        """
        self.b1.append_to_text.connect(self.appendText)
        self.b2.append_to_text.connect(self.appendText)
        self.b3.append_to_text.connect(self.appendText)
        self.b4.append_to_text.connect(self.appendText)
        self.b5.append_to_text.connect(self.appendText)
        self.b6.append_to_text.connect(self.appendText)

    def connectChangeMenuOptionsSignal(self):
        """
        Connects the change_menu_options signal to all buttons
        """
        self.b1.change_menu_options.connect(self.changeMenu)
        self.b2.change_menu_options.connect(self.changeMenu)
        self.b3.change_menu_options.connect(self.changeMenu)
        self.b4.change_menu_options.connect(self.changeMenu)
        self.b5.change_menu_options.connect(self.changeMenu)
        self.b6.change_menu_options.connect(self.changeMenu)

    def connectSpeakTextSignal(self):
        """
        Connects the speak_signal signal to all buttons
        """
        self.b1.speak_signal.connect(self.speakText)
        self.b2.speak_signal.connect(self.speakText)
        self.b3.speak_signal.connect(self.speakText)
        self.b4.speak_signal.connect(self.speakText)
        self.b5.speak_signal.connect(self.speakText)
        self.b6.speak_signal.connect(self.speakText)

    def setMenuButtonContent(self, b1_text, b2_text, b3_text, b4_text, b5_text,
            b6_text):
        """
        Sets the button content for each button in currently displayed menu.

        :param b1_text: Content of button 1 (top left corner)
        :param b2_text: Content of button 2 (top middle)
        :param b3_text: Content of button 3 (top right corner)
        :param b4_text: Content of button 4 (bottom left corner)
        :param b5_text: Content of button 5 (bottom middle)
        :param b6_text: Content of button 6 (bottom right corner)

        :type b1_text: str
        :type b2_text: str
        :type b3_text: str
        :type b4_text: str
        :type b5_text: str
        :type b6_text: str
        """
        self.b1.setContent(b1_text)
        self.b2.setContent(b2_text)
        self.b3.setContent(b3_text)
        self.b4.setContent(b4_text)
        self.b5.setContent(b5_text)
        self.b6.setContent(b6_text)

    def createSixButtonLayout(self):
        """
        Creates a screen layout for the ui with six buttons
        """
        #Create layout for top 3 buttons
        b_layout_top = QtWidgets.QHBoxLayout()
        b_layout_top.addWidget(self.b1)
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b2)
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b3)

        #Create layout to contain text
        text_layout = QtWidgets.QHBoxLayout()
        self.print_text = QtWidgets.QLabel()
        text_layout.addStretch()
        text_layout.addWidget(self.print_text)
        text_layout.addStretch()

        #Create layout for bottom 3 buttons
        b_layout_bot = QtWidgets.QHBoxLayout()
        b_layout_bot.addWidget(self.b4)
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b5)
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b6)

        #Arrange 3 sublayouts to create master layout for entire window
        master_layout = QtWidgets.QVBoxLayout()
        master_layout.addLayout(b_layout_top)
        master_layout.addStretch()
        master_layout.addLayout(text_layout)
        master_layout.addStretch()
        master_layout.addLayout(b_layout_bot)
        self.setLayout(master_layout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = UIWidget()
    widget.show()
    sys.exit(app.exec_())

