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
        #Triggered when mouse hovers over button
        self.setStyleSheet("background-color: red")

    def leaveEvent(self, event):
        #Triggered when mouse leaves area of push button
        self.setStyleSheet("")

    @pyqtSlot()
    def buttonClicked(self):
        #Massive switch statement that performs some action based on a button's
        #content
        if(self.content == "A-E"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "F-J"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "K-O"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "P-T"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "U-Y"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "Z, Actions"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "Numbers"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "Shift, Delete, Clear, Done"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "0-4"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "5-9"):
            self.change_menu_options.emit(str(self.content))
        elif(self.content == "Symbols"):
            ##TODO Add symbols menu
            pass
        elif(self.content == "Shift"):
            ##TODO Add a shift modifier
            pass
        elif(self.content == "Clear"):
            self.clear_signal.emit()
            pass
        elif(self.content == "Delete"):
            self.backspace.emit()
        elif(self.content == "Done"):
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
        self.setStyleSheet("background-color: red")

    def setContent(self, val):
        self.content = val
        self.setText(str(val))

    def setPrevMenu(self, prev):
        self.prev_menu = prev
