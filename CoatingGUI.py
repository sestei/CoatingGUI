#!/usr/bin/python

import sys
from gui.mainWindow import MainWindow
from PyQt4 import QtGui

qApp = QtGui.QApplication(sys.argv) 
Window = MainWindow()
Window.show()
qApp.exec_()