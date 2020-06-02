# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'controls.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class Ui_ControlWindow:
    def setupUi(self, ControlWindow, control_instance):
        self.controls = control_instance
        ControlWindow.setObjectName("ControlWindow")
        ControlWindow.resize(648, 839)
        self.centralwidget = QtWidgets.QWidget(ControlWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        #make buttons
        self.save_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_button.setGeometry(QtCore.QRect(10, 10, 371, 101))
        self.save_button.setObjectName("save_button")

        self.load_states_button = QtWidgets.QPushButton(self.centralwidget)
        self.load_states_button.setGeometry(QtCore.QRect(10, 250, 371, 101))
        self.load_states_button.setObjectName("load_states_button")

        self.change_ruleset_button = QtWidgets.QPushButton(self.centralwidget)
        self.change_ruleset_button.setGeometry(QtCore.QRect(10, 130, 371, 101))
        self.change_ruleset_button.setObjectName("change_ruleset_button")

        self.load_image_button = QtWidgets.QPushButton(self.centralwidget)
        self.load_image_button.setGeometry(QtCore.QRect(10, 370, 371, 101))
        self.load_image_button.setObjectName("load_image_button")

        self.set_timer_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_timer_button.setGeometry(QtCore.QRect(10, 490, 371, 101))
        self.set_timer_button.setObjectName("set_timer_button")

        self.connect_buttons()

        ControlWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ControlWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 648, 38))
        self.menubar.setObjectName("menubar")
        ControlWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ControlWindow)
        self.statusbar.setObjectName("statusbar")
        ControlWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ControlWindow)
        QtCore.QMetaObject.connectSlotsByName(ControlWindow)

    def retranslateUi(self, ControlWindow):
        _translate = QtCore.QCoreApplication.translate
        ControlWindow.setWindowTitle(_translate("ControlWindow", "MainWindow"))
        self.save_button.setText(_translate("ControlWindow", "Save Image and States"))
        self.load_states_button.setText(_translate("ControlWindow", "Load From States"))
        self.change_ruleset_button.setText(_translate("ControlWindow", "Change Ruleset"))
        self.load_image_button.setText(_translate("ControlWindow", "Load From Image"))
        self.set_timer_button.setText(_translate("ControlWindow", "Set Timer"))

    def connect_buttons(self):
        self.save_button.clicked.connect(self.clicked)
        self.load_states_button.clicked.connect(self.clicked)
        self.change_ruleset_button.clicked.connect(self.clicked)
        self.load_image_button.clicked.connect(self.clicked)
        self.load_states_button.clicked.connect(self.clicked)
        self.set_timer_button.clicked.connect(self.controls.set_timer_handler)

    def clicked(self):
        print('button clicked')


class ButtonWindow:
    def __init__(self, control_instance):
        #Control object containing handlers
        self.control = control_instance

        app = QtWidgets.QApplication(sys.argv)
        ControlWindow = QtWidgets.QMainWindow()
        ui = Ui_ControlWindow()
        ui.setupUi(ControlWindow, self.control)
        ControlWindow.show()
        sys.exit(app.exec_())

