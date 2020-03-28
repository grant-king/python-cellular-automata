from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow():
    def __init__(self, size):
        self.app = QApplication(sys.argv)
        self.win = QMainWindow()
        self.win.setGeometry(100, 100, size[0], size[1])
        self.win.setWindowTitle('QT Main Window')

    def show(self):
        self.win.show()
        sys.exit(self.app.exec_()) #clean exit

    def set_title(self, title):
        self.win.setWindowTitle(title)
