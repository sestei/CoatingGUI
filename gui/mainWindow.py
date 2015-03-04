#!/usr/bin/env python

import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_mainWindow import Ui_MainWindow
from ..stacks import Stack

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.plt = self.pltMain.figure.add_subplot(111)
        x = [0, 1, 2]
        y = [4, 1, 3]
        self.plt.plot(x, y)
        self.pltMain.draw()
        self.initialise_tblMain()
        self.build_stack()

    def initialise_tblMain(self):
        t = [250,150]
        i = [1.45,2.2]
        self.tblStack.setRowCount(10)
        self.tblStack.setColumnCount(2)
        self.tblStack.setHorizontalHeaderLabels(['Thickness (nm)', 'Index'])
        self.tblStack.setVerticalHeaderLabels(['1','2','3','4','5','6','7','8','9','10'])
        for ii in range(0,10):
            tt = QTableWidgetItem(str(t[ii%2]))
            it = QTableWidgetItem(str(i[ii%2]))
            tt.setTextAlignment(Qt.AlignRight)
            it.setTextAlignment(Qt.AlignRight)
            self.tblStack.setItem(ii,0,tt)
            self.tblStack.setItem(ii,1,it)

    def build_stack(self):
        isubstrate = float(self.cbSubstrate.currentText())
        isuperstrate = float(self.cbSuperstrate.currentText())
        stack_d = []
        stack_n = []
        for ii in range(0, self.tblStack.rowCount):
            pass

        

    @pyqtSlot()
    def on_btnUpdate_clicked(self):
        x = np.linspace(0,2*np.pi,100)
        y = np.sin(x)
        self.plt.plot(x,y)
        self.pltMain.draw()

    @pyqtSlot()
    def on_btnClearStack_clicked(self):
        response = QMessageBox.warning(self, "Clear stack data",
                               "Do you want to clear the stack data?",
                               buttons=QMessageBox.Ok|QMessageBox.Cancel)
        if response == QMessageBox.Ok:
            self.tblStack.clear()
            self.initialise_tblMain()
