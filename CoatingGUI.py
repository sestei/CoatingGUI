#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import sys
from gui.mainWindow import MainWindow
from PyQt4 import QtGui

qApp = QtGui.QApplication(sys.argv) 
Window = MainWindow()
Window.show()
qApp.exec_()