import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread as QThread
import track_pupils as PupilTracker
import image_processing_thread as IPT

class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.init_ui()

        #Start image processing tab
        self.get_thread(IPT.imageProcessingThread())

    def init_ui(self):
        self.top_button = QtWidgets.QPushButton('Top Button')
        self.left_button = QtWidgets.QPushButton('Left Button')
        self.right_button = QtWidgets.QPushButton('Right Button')
        self.bottom_button = QtWidgets.QPushButton('Bottom Button')
        self.print_text = QtWidgets.QLabel('Printed Text...')

        #Resize Buttons
        top_button_width = 600
        top_button_height = 200
        side_button_width = 300
        side_button_height = 400

        self.top_button.setFixedSize(top_button_width, top_button_height)
        self.bottom_button.setFixedSize(top_button_width, top_button_height)
        self.left_button.setFixedSize(side_button_width, side_button_height)
        self.right_button.setFixedSize(side_button_width, side_button_height)

        #Create layouts for buttons/label
        top_box = QtWidgets.QHBoxLayout()
        top_box.addStretch()
        top_box.addWidget(self.top_button)
        top_box.addStretch()

        mid_box = QtWidgets.QHBoxLayout()
        mid_box.addWidget(self.left_button)
        mid_box.addStretch()
        mid_box.addWidget(self.print_text)
        mid_box.addStretch()
        mid_box.addWidget(self.right_button)

        bot_box = QtWidgets.QHBoxLayout()
        bot_box.addStretch()
        bot_box.addWidget(self.bottom_button)
        bot_box.addStretch()


        #Assign layout to window
        v_box = QtWidgets.QVBoxLayout()
        v_box.addLayout(top_box)
        v_box.addLayout(mid_box)
        v_box.addLayout(bot_box)

        self.setLayout(v_box)
        self.setWindowTitle('Pupil Tracking')

        #Button Callbacks
        self.top_button.clicked.connect(self.top_clicked)
        self.left_button.clicked.connect(self.left_clicked)
        self.right_button.clicked.connect(self.right_clicked)
        self.bottom_button.clicked.connect(self.bottom_clicked)

        #Call our pupil tracking script
        #PupilTracker.detectPupils()

        self.show()

    #Button Callback Definitions
    def top_clicked(self):
        self.print_text.setText('Top Button Clicked')

    def left_clicked(self):
        self.print_text.setText('Left Button Clicked')

    def right_clicked(self):
        self.print_text.setText('Right Button Clicked')

    def bottom_clicked(self):
        self.print_text.setText('Bottom Button Clicked')

def run_app(app):
    sys.exit(app.exec_())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    a_window = Window()
    sys.exit(app.exec_())
