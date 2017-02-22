from PyQt5 import QtCore as QtCore
from PyQt5 import QtWidgets as QtWidgets
from PyQt5 import QtGui as QtGui
from PyQt5.QtCore import *
import sys
import cv2
import collections
import math
import pyautogui
from tracking_thread import TrackingThread
import time

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
        #self.init_basic_ui()
        self.init_ui6() #6 button layout

        #Pass center information to thread
        self.update_button_centers.connect(self.thread.setButtonCenters)
        self.thread.request_button_centers.connect(self.establishButtonCenters)
        self.calibrate_pupil_centers.connect(self.thread.calibrate)

        #Allow for cursor movement
        self.thread.move_cursor_to_button.connect(self.moveCursor)

        #Send button centers to thread
        self.thread.startProcessing()

    def init_basic_ui(self):
        self.showFullScreen()
        self.b1 = QtWidgets.QPushButton("Left Button")

        self.b2 = QtWidgets.QPushButton("Right Button")

        #self.statusBar = QtWidgets.QStatusBar()

        #Resize buttons
        button_width = 400
        button_height = 600
        self.b1.setFixedSize(button_width, button_height)
        self.b2.setFixedSize(button_width, button_height)
        #self.statusBar.setFixedSize(button_width, button_height)

        #Create layout for buttons
        b_layout = QtWidgets.QHBoxLayout()
        b_layout.addWidget(self.b1)
        b_layout.addStretch()
        #b_layout.addWidget(self.statusBar)
        #b_layout.addStretch()
        b_layout.addWidget(self.b2)

        #Layout for window at lage
        w_layout = QtWidgets.QVBoxLayout()
        w_layout.addStretch()
        w_layout.addLayout(b_layout)
        w_layout.addStretch()

        self.setLayout(w_layout)

    def init_ui6(self):
        self.showFullScreen()
        self.b1 = QtWidgets.QPushButton("Button 1", parent=self)
        self.b2 = QtWidgets.QPushButton("Button 2", parent=self)
        self.b3 = QtWidgets.QPushButton("Button 3", parent=self)
        self.b4 = QtWidgets.QPushButton("Button 4", parent=self)
        self.b5 = QtWidgets.QPushButton("Button 5", parent=self)
        self.b6 = QtWidgets.QPushButton("Button 6", parent=self)

        #Resize the buttons - they will all be squares
        b_width = 300
        b_height = 300
        self.b1.setFixedSize(b_width, b_height)
        self.b2.setFixedSize(b_width, b_height)
        self.b3.setFixedSize(b_width, b_height)
        self.b4.setFixedSize(b_width, b_height)
        self.b5.setFixedSize(b_width, b_height)
        self.b6.setFixedSize(b_width, b_height)


        #Create layout
        b_layout_top = QtWidgets.QHBoxLayout()
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b1)
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b2)
        b_layout_top.addStretch()
        b_layout_top.addWidget(self.b3)
        b_layout_top.addStretch()

        text_layout = QtWidgets.QHBoxLayout()
        self.print_text = QtWidgets.QLabel("Text printed here...")
        text_layout.addStretch()
        text_layout.addWidget(self.print_text)
        text_layout.addStretch()

        b_layout_bot = QtWidgets.QHBoxLayout()
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b4)
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b5)
        b_layout_bot.addStretch()
        b_layout_bot.addWidget(self.b6)
        b_layout_bot.addStretch()

        master_layout = QtWidgets.QVBoxLayout()
        master_layout.addStretch()
        master_layout.addLayout(b_layout_top)
        master_layout.addStretch()
        master_layout.addLayout(text_layout)
        master_layout.addStretch()
        master_layout.addLayout(b_layout_bot)
        master_layout.addStretch()

        self.setLayout(master_layout)

    def keyPressEvent(self, event):
        if event.text() == 'q':
            QtWidgets.QApplication.quit()

        if event.text() == 'b':
            self.establishButtonCenters()

        if event.text() == 'c':
            self.calibrate()
            #statusBar = QtWidgets.QStatusBar()
            #msg_bar.showMessage('Look here to calibrate.')
            #msg_bar.hideOrShow()
            #statusBar.showMessage('Look here to calibrate.');
            #statusBar.show()
            #time.sleep(1)
            #statusBar.close()

            #self.calibration_popup = Popup('Calibration')
            #self.calibration_popup.dispMessage('Look here to calibrate.', 1000)
            #self.calibration_popup.show()
            #time.sleep(1)
            #self.calibration_popup.close()
            #self.thread.calibrate()

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
        text = str(cursor_dest[0]) + ","  + str(cursor_dest[1])
        self.print_text.setText(text)
        self.setCursor(c)

    @pyqtSlot()
    def calibrate(self):
        self.calibrate_pupil_centers.emit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = UIWidget()
    widget.show()
    sys.exit(app.exec_())

