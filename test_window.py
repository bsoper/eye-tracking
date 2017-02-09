from PyQt5 import QtCore as QtCore
from PyQt5 import QtWidgets as QtWidgets
from PyQt5 import QtGui as QtGui
import sys

class UIWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UIWidget, self).__init__(parent)

        #Set widget params
        self.setWindowTitle("Pupil Tracker")
        self.resize(550, 400)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = UIWidget()
    widget.show()
    sys.exit(app.exec_())

