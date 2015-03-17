#!/usr/bin/env python

from os.path import basename, splitext
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from coating import Coating
from plottypes import plottypes
from config import Config
from utils import block_signals
from materialDialog import MaterialDialog
import materials

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.config = Config.Instance()
        self.config.load('default.cgp')
        self.materials = materials.MaterialLibrary.Instance()
        uic.loadUi('gui/ui_mainWindow.ui', self)
 
        self.plotHandle = self.pltMain.figure.add_subplot(111)
        
        self.update_title('untitled')
        self.config.modified.connect(self.handle_modified)

        self.initialise_plotoptions()
        self.initialise_materials()
        self.initialise_stack()

    def update_title(self, filename=None, changed=False):
        if changed:
            flag = '*'
            self.modified = True
        else:
            flag = ''
            self.modified = False
        if filename:
            self.filename = filename

        self.setWindowTitle('Coating GUI - {0}{1}'.format(self.filename, flag))

    def initialise_materials(self):
        self.materials.load_materials()
        self.update_material_list()

    def initialise_plotoptions(self):
        with block_signals(self.cbPlotType) as cb:
            cb.clear()
            for ii in range(0, len(plottypes)):
                cb.insertItem(ii, plottypes[ii][0])
            cb.setCurrentIndex(self.config.get('plot.plottype'))
        
        if self.config.get('plot.xaxis.limits') == 'auto':
            self.rbXLimAuto.setChecked(True)
            self.rbXLimUser.setChecked(False)
        else:
            self.rbXLimAuto.setChecked(False)
            self.rbXLimUser.setChecked(True)
        if self.config.get('plot.yaxis.limits') == 'auto':
            self.rbYLimAuto.setChecked(True)
            self.rbYLimUser.setChecked(False)
        else:
            self.rbYLimAuto.setChecked(False)
            self.rbYLimUser.setChecked(True)
        
        if self.config.get('plot.xaxis.scale') == 'lin':
            self.rbXScaleLin.setChecked(True)
            self.rbXScaleLog.setChecked(False)
        else:
            self.rbXScaleLin.setChecked(False)
            self.rbXScaleLog.setChecked(True)
        if self.config.get('plot.yaxis.scale') == 'lin':
            self.rbYScaleLin.setChecked(True)
            self.rbYScaleLog.setChecked(False)
        else:
            self.rbYScaleLin.setChecked(False)
            self.rbYScaleLog.setChecked(True)
        
        self.txtXLimMin.setText(str(self.config.get('plot.xaxis.min')))
        self.txtXLimMax.setText(str(self.config.get('plot.xaxis.max')))
        self.txtYLimMin.setText(str(self.config.get('plot.yaxis.min')))
        self.txtYLimMax.setText(str(self.config.get('plot.yaxis.max')))

        self.txtSteps.setText(str(self.config.get('plot.xaxis.steps')))


    def initialise_stack(self):
        with block_signals(self.cbSuperstrate) as cb:
            m = self.config.get('coating.superstrate')
            if cb.findText(m) < 0:
                cb.insertItem(0, m)
            cb.setCurrentIndex(cb.findText(m))
        with block_signals(self.cbSubstrate) as cb:
            m = self.config.get('coating.substrate')
            if cb.findText(m) < 0:
                cb.insertItem(0, m)
            cb.setCurrentIndex(cb.findText(m))
        self.txtLambda0.setText(str(self.config.get('coating.lambda0')))
        self.txtAOI.setText(str(self.config.get('coating.AOI')))

        layers = self.config.get('coating.layers')
        self.tblStack.setRowCount(len(layers))
        self.tblStack.setColumnCount(2)
        self.prototype = QTableWidgetItem('0')
        self.prototype.setTextAlignment(Qt.AlignRight)
        self.tblStack.setItemPrototype(self.prototype)
        with block_signals(self.tblStack) as tbl:
            for ii in range(len(layers)):
                tt = QTableWidgetItem(str(layers[ii][1]))
                it = QTableWidgetItem(str(layers[ii][0]))
                tt.setTextAlignment(Qt.AlignRight)
                it.setTextAlignment(Qt.AlignRight)
                tbl.setItem(ii,0,tt)
                tbl.setItem(ii,1,it)

    def get_layers(self):
        stack_d = []
        stack_n = []
        for row in range(self.tblStack.rowCount()):
            item_d = self.tblStack.item(row, 0)
            item_n = self.tblStack.item(row, 1)
            if item_d and item_n:
                stack_d.append(str(item_d.text()))
                stack_n.append(str(item_n.text()))
        return map(list, zip(stack_n, stack_d))

    def build_coating(self):
        substrate = str(self.cbSubstrate.currentText())
        superstrate = str(self.cbSuperstrate.currentText())
        
        return Coating(superstrate, substrate, self.get_layers())
        
    def closeEvent(self, event):
        if self.modified:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                        'You have unsaved changes, do you really want to discard those and quit?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()

    def float_conversion_error(self, text):
        QMessageBox.critical(self, 'Conversion Error',
            'The input "{0}" could not be converted to a floating point number.'.format(text))
    
    ### SLOTS - GENERIC

    @pyqtSlot()
    def handle_modified(self):
        self.update_title(changed=True)
    
    
    ### SLOTS - PLOT WINDOW

    @pyqtSlot()
    def on_btnUpdate_clicked(self):
        try:
            coating = self.build_coating()
        except materials.MaterialNotDefined as e:
            QMessageBox.critical(self, 'Material Error', str(e))
            return
        plotidx = self.cbPlotType.currentIndex()
        plottypes[plotidx][1](self.plotHandle, coating)
        self.pltMain.draw()

    
    ### SLOTS - STACK TAB

    @pyqtSlot()
    def on_btnRemoveLayer_clicked(self):
        self.tblStack.removeRow(self.tblStack.currentRow())
        self.config.set('coating.layers', self.get_layers())

    @pyqtSlot()
    def on_btnAddLayer_clicked(self):
        row = self.tblStack.currentRow()+1
        self.tblStack.insertRow(row)

    @pyqtSlot(int)
    def on_cbPlotType_currentIndexChanged(self, idx):
        self.config.set('plot.plottype', idx)

    @pyqtSlot(str)
    def on_cbSuperstrate_currentIndexChanged(self, text):
        self.config.set('coating.superstrate', text)

    @pyqtSlot(str)
    def on_cbSubstrate_currentIndexChanged(self, text):
        self.config.set('coating.substrate', text)
    
    @pyqtSlot()
    def on_txtLambda0_editingFinished(self):
        text = self.txtLambda0.text()
        try:
            self.config.set('coating.lambda0', float(text))
        except ValueError:
            self.float_conversion_error(text)
    
    @pyqtSlot()
    def on_txtAOI_editingFinished(self):
        text = self.txtAOI.text()
        try:
            self.config.set('coating.AOI', float(text))
        except ValueError:
            self.float_conversion_error(text)

    @pyqtSlot(int, int)
    def on_tblStack_cellChanged(self, row, col):
        self.config.set('coating.layers', self.get_layers())

    @pyqtSlot()
    def on_btnWizard_clicked(self):
        QMessageBox.information(self, 'Preparing for O.W.L.',
            'Sorry, the wizard is not available yet.')

    ### SLOTS - PLOT OPTIONS TAB

    @pyqtSlot(bool)
    def on_rbXLimAuto_clicked(self, checked):
        if checked:
            self.config.set('plot.xaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbYLimAuto_clicked(self, checked):
        if checked:
            self.config.set('plot.yaxis.limits', 'auto')

    @pyqtSlot(bool)
    def on_rbXLimUser_clicked(self, checked):
        if checked:
            self.config.set('plot.xaxis.limits', 'user')

    @pyqtSlot(bool)
    def on_rbYLimUser_clicked(self, checked):
        if checked:
            self.config.set('plot.yaxis.limits', 'user')

    @pyqtSlot()
    def on_txtXLimMin_editingFinished(self):
        text = self.txtXLimMin.text()
        try:
            self.config.set('plot.xaxis.min', float(text))
        except ValueError:
            self.float_conversion_error(text)

    @pyqtSlot()
    def on_txtXLimMax_editingFinished(self):
        text = self.txtXLimMax.text()
        try:
            self.config.set('plot.xaxis.max', float(text))
        except ValueError:
            self.float_conversion_error(text)

    @pyqtSlot()
    def on_txtYLimMin_editingFinished(self):
        text = self.txtYLimMin.text()
        try:
            self.config.set('plot.yaxis.min', float(text))
        except ValueError:
            self.float_conversion_error(text)

    @pyqtSlot()
    def on_txtYLimMax_editingFinished(self):
        text = self.txtYLimMax.text()
        try:
            self.config.set('plot.yaxis.max', float(text))
        except ValueError:
            self.float_conversion_error(text)

    @pyqtSlot()
    def on_txtSteps_editingFinished(self):
        text = self.txtSteps.text()
        try:
            self.config.set('plot.xaxis.steps', float(text))
        except ValueError:
            self.float_conversion_error(text)
    
    @pyqtSlot(bool)
    def on_rbXScaleLin_clicked(self, checked):
        if checked:
            self.config.set('plot.xaxis.scale', 'lin')
    
    @pyqtSlot(bool)
    def on_rbYScaleLin_clicked(self, checked):
        if checked:
            self.config.set('plot.yaxis.scale', 'lin')
    
    @pyqtSlot(bool)
    def on_rbXScaleLog_clicked(self, checked):
        if checked:
            self.config.set('plot.xaxis.scale', 'log')
    
    @pyqtSlot(bool)
    def on_rbYScaleLog_clicked(self, checked):
        if checked:
            self.config.set('plot.yaxis.scale', 'log')

    
    ### SLOTS - MATERIALS TAB

    @pyqtSlot()
    def update_material_list(self):
        # save selection
        sub = str(self.cbSubstrate.currentText())
        sup = str(self.cbSuperstrate.currentText())
        materials = [m for m in self.materials.list_materials()]
        self.lstMaterials.clear()
        self.cbSuperstrate.clear()
        self.cbSubstrate.clear()
        self.lstMaterials.addItems(materials)
        with block_signals(self.cbSubstrate) as cbsub, block_signals(self.cbSuperstrate) as cbsup:
            cbsub.addItems(sorted(materials))
            cbsup.addItems(sorted(materials))
            # if user added a numeric refractive index value, copy that back in
            if sub and not sub in materials:
                cbsub.addItem(sub)
            if sup and not sup in materials:
                cbsup.addItem(sup)
            # restore selection
            cbsub.setCurrentIndex(self.cbSubstrate.findText(sub))
            cbsup.setCurrentIndex(self.cbSuperstrate.findText(sup))

    @pyqtSlot()
    def on_btnAddMaterial_clicked(self):
        dlg = MaterialDialog(self)
        dlg.load_material()
        if dlg.exec_() == QDialog.Accepted:
            dlg.save_material()
            self.update_material_list()

    @pyqtSlot()
    def on_btnEditMaterial_clicked(self):
        row = self.lstMaterials.currentRow()
        if row >= 0:
            material = str(self.lstMaterials.item(row).text())
            dlg = MaterialDialog(self)
            dlg.load_material(material)
            if dlg.exec_() == QDialog.Accepted:
                dlg.save_material()

    @pyqtSlot()
    def on_btnDeleteMaterial_clicked(self):
        row = self.lstMaterials.currentRow()
        if row >= 0:
            material = str(self.lstMaterials.item(row).text())
            materials.MaterialLibrary.Instance().unregister(material)
            self.lstMaterials.takeItem(row)
            self.cbSuperstrate.removeItem(self.cbSuperstrate.findText(material))
            self.cbSubstrate.removeItem(self.cbSubstrate.findText(material))


    ### SLOTS - MENU

    @pyqtSlot()
    def on_actionExport_triggered(self):
        filename = QFileDialog.getSaveFileName(self, 'Export Plot',
                            splitext(self.filename)[0]+'.pdf', 'PDF (*.pdf)');
        if filename:
            self.pltMain.figure.savefig(str(filename))

    @pyqtSlot()
    def on_actionSave_triggered(self):
        filename = str(QFileDialog.getSaveFileName(self, 'Save Coating Project',
                            self.filename, 'Coating Project Files (*.cgp)'))
        if filename:
            self.config.save(filename)
            self.update_title(basename(filename))

    @pyqtSlot()
    def on_actionOpen_triggered(self):
        if self.modified:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                        'You have unsaved changes, do you really want to discard those?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        filename = str(QFileDialog.getOpenFileName(self, 'Open Coating Project',
                            '.', 'Coating Project Files (*.cgp)'))
        if filename:
            self.config.load(filename)
            self.update_title(basename(filename))
            self.initialise_plotoptions()
            self.initialise_materials()
            self.initialise_stack()
