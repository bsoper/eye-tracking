from PyQt5 import QtCore as QtCore
from PyQt5 import QtWidgets as QtWidgets
from PyQt5 import QtGui as QtGui
from PyQt5.QtCore import *
import sys
import cv2
import collections
import math
import pyautogui
from tracking_thread import TrackingThread as TrackingThread

class CustomButton(QtWidgets.QPushButton):
    change_menu_options = pyqtSignal(str)
    append_to_text = pyqtSignal(str)
    backspace = pyqtSignal()
    clear_signal = pyqtSignal()
    speak_signal = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initializes button by connecting signals and clearing parameters
        """
        super(CustomButton, self).__init__(parent)

        #Allow button to track where mouse is
        self.setMouseTracking(True)

        #Connect clicking signal to click function
        self.clicked.connect(self.buttonClicked)
        self.released.connect(self.buttonReleased)

        #Set the content of the button
        self.content = 'none'

        #Set previous menu of button
        self.prev_menu = "main"


    def enterEvent(self, event):
        """
        Called when mouse hovers over button

        :param event: Mouse Enter Event called when mouse hovers over button
        """
        self.setStyleSheet("background-color: red")

    def leaveEvent(self, event):
        """
        Called when mouse leaves button

        :param event: Mouse Leave Event called when mouse leaves button
        """
        self.setStyleSheet("")

    @pyqtSlot()
    def buttonClicked(self):
        """
        Slotted function that performs various actions when a button is clicked.

        It is essentially a massive switch/case statement that performs functions
        based off of the buttons self.button_content
        """
        menu_options = ["A-E", "F-J","K-O","P-T","U-Z","X,Z","Numbers",
                        "Letters","Phrases","0-4","5-9","Punctuation",
                        "Symbols","Additional Symbols","Greetings",
                        "Responses","Emotions"]

        if self.content in menu_options:
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "Space"):
            self.append_to_text.emit(" ")
            self.change_menu_options.emit("main")
        elif(self.content == "Clear"):
            self.clear_signal.emit()
            pass
        elif(self.content == "Backspace"):
            self.backspace.emit()
        elif(self.content == "Confirm"):
            self.speak_signal.emit()
        elif(self.content == "Back"):
            self.change_menu_options.emit(str(self.prev_menu))
        elif(self.content == ""):
            pass
        else:
            #Otherwise, just add content to the current string
            self.append_to_text.emit(str(self.content))
            self.change_menu_options.emit("main")


    @pyqtSlot()
    def buttonReleased(self):
        """
        Slotted Qt Function: Called when button is released after being clicked
        """
        self.setStyleSheet("background-color: red")

    def setContent(self, val):
        """
        Sets the content of the button. The content denotes what the function the
        button will perform when clicked

        :param val: The content to be assigned to the button
        :type val: str
        """
        self.content = val
        self.setText(str(val))

    def setPrevMenu(self, prev):
        """
        Sets the previous menu of the button

        :param prev_menu: The previous menu
        :type prev_menu: str
        """
        self.prev_menu = prev
