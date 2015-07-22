#!/usr/bin/env python
# This work is licensed under the Creative Commons Attribution-NonCommercial-
# ShareAlike 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.

import re

from os.path import basename, splitext
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

import plothandler
import wizard
from dielectric.materials import MaterialLibrary
from dielectric.coating import Coating
from utils.config import Config
from utils import compare_versions, version_number, version_string
from helpers import export_data, block_signals, float_set_from_lineedit
from materialDialog import MaterialDialog
from wizard import Wizard


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.config = Config.Instance()
        self.config.load_default('default.cgp')
        self.materials = MaterialLibrary.Instance()
        uic.loadUi('gui/ui_mainWindow.ui', self)
 
        self.plotHandle = self.pltMain.figure.add_subplot(111)
        color = self.palette().color(QPalette.Background)
        self.pltMain.figure.set_facecolor(color.getRgbF()[0:3])

        cid = self.pltMain.figure.canvas.mpl_connect('motion_notify_event', 
            lambda ev: self.mpl_on_mouse_move(ev))

        self.update_title('untitled')
        self.config.set_callback(self.handle_modified)

        self.empty_plotoptions_widget = self.gbPlotWidget.layout().itemAt(0).widget()
        self.plots = plothandler.collect_plots()

        self.initialise_plotoptions()
        self.initialise_materials()
        self.initialise_stack()

        geometry = self.config.get('window_geometry')
        if geometry:
            geometry = QByteArray.fromHex(self.config.get('window_geometry'))
            self.restoreGeometry(geometry)

        self.stbStatus.showMessage(version_string)

    def update_title(self, filename=None, changed=False):
        if changed:
            flag = '*'
            self.modified = True
        else:
            flag = ''
            self.modified = False
        if filename:
            self.filename = filename

        self.setWindowTitle('CoatingGUI - {0}{1}'.format(self.filename, flag))

    def initialise_materials(self):
        self.materials.load_materials()
        self.update_material_list()

    def initialise_plotoptions(self):
        with block_signals(self.cbPlotType) as cb:
            cb.clear()
            for k,v in self.plots.iteritems():
                cb.addItem(v['description'], k)
            setplot = self.config.get('plot.plottype')
            cb.setCurrentIndex(cb.findData(setplot))
            self.update_plot_widget(setplot)
        
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
                tbl.setItem(ii,1,tt)
                tbl.setItem(ii,0,it)

    def get_layers(self):
        stack_d = []
        stack_n = []
        for row in range(self.tblStack.rowCount()):
            item_d = self.tblStack.item(row, 1)
            item_n = self.tblStack.item(row, 0)
            if item_d and item_n:
                try:
                    stack_d.append(float(item_d.text()))
                    stack_n.append(str(item_n.text()))
                except ValueError:
                    self.float_conversion_error(str(item_d.text()))
        return map(list, zip(stack_n, stack_d))

    def build_coating(self):
        #substrate = str(self.cbSubstrate.currentText())
        #superstrate = str(self.cbSuperstrate.currentText())
        
        #return Coating(superstrate, substrate, self.get_layers())
        return Coating.create_from_config(self.config)
        
    def closeEvent(self, event):
        if self.modified and not self.config.get('do_not_ask_on_quit'):
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

    # matplotlib slot
    def mpl_on_mouse_move(self, event):
        if event.xdata and event.ydata:
            yformat = self.plotHandle.yaxis.get_major_formatter()
            xformat = self.plotHandle.xaxis.get_major_formatter()
            self.stbStatus.showMessage(u'x={:} y={:}'.format(xformat.format_data_short(event.xdata),
                                                             yformat.format_data_short(event.ydata)))    
    
    ### SLOTS - PLOT WINDOW

    @pyqtSlot()
    def on_btnUpdate_clicked(self):
        try:
            coating = self.build_coating()
        except materials.MaterialNotDefined as e:
            QMessageBox.critical(self, 'Material Error', str(e))
            return
        idx = self.cbPlotType.currentIndex()
        plot = str(self.cbPlotType.itemData(idx).toString())

        self.pltMain.figure.clear()
        self.plotHandle = self.pltMain.figure.add_subplot(111)
        klass = self.plots[plot]['plotter']
        plot = klass(self.plotHandle)
        plot.plot(coating)
        self.pltMain.draw()

    @pyqtSlot(str)
    def update_plot_widget(self, plot):
        # if plot has it's own widget, then load it
        klass = self.plots[plot]['options']
        if klass:
            widget = klass(self.gbPlotWidget)
        else:
            widget = self.empty_plotoptions_widget

        old_widget = self.gbPlotWidget.layout().takeAt(0).widget()
        old_widget.setParent(None)
        self.gbPlotWidget.layout().addWidget(widget)
        self.gbPlotWidget.update()
        
    ### SLOTS - STACK TAB

    @pyqtSlot()
    def on_btnRemoveLayer_clicked(self):
        self.tblStack.removeRow(self.tblStack.currentRow())
        self.config.set('coating.layers', self.get_layers())

    @pyqtSlot()
    def on_btnAddLayer_clicked(self):
        row = self.tblStack.currentRow()+1
        self.tblStack.insertRow(row)

    @pyqtSlot()
    def on_btnClearStack_clicked(self):
        self.config.set('coating.layers', [])
        self.initialise_stack()

    @pyqtSlot(str)
    def on_cbSuperstrate_currentIndexChanged(self, text):
        self.config.set('coating.superstrate', str(text))

    @pyqtSlot(str)
    def on_cbSubstrate_currentIndexChanged(self, text):
        self.config.set('coating.substrate', str(text))
    
    @pyqtSlot()
    def on_txtLambda0_editingFinished(self):
        float_set_from_lineedit(self.txtLambda0, self.config, 'coating.lambda0', self)
    
    @pyqtSlot()
    def on_txtAOI_editingFinished(self):
        float_set_from_lineedit(self.txtAOI, self.config, 'coating.AOI', self)

    @pyqtSlot(int, int)
    def on_tblStack_cellChanged(self, row, col):
        txt = self.tblStack.item(row, col).text()
        if col == 1:
            xlambda = 0.0
            # auto-convert L/x or l/x or just /x to lambda/x thicknesses
            m = re.match('^[Ll]?/(\d+)$', txt)
            if m:
                xlambda = 1.0/int(m.groups()[0])
            else:
                # auto-convert *x to x*lambda/4 thicknesses
                m = re.match('^\*([\d\.]+)$', txt)
                if m:
                    xlambda = 0.25*float(m.groups()[0])

            if xlambda > 0.0:
                mat = self.tblStack.item(row, col-1).text()
                try:
                    mat = self.materials.get_material(str(mat))
                    lambda0 = self.config.get('coating.lambda0')
                    t_lox = xlambda * lambda0/mat.n(lambda0)
                    with block_signals(self.tblStack) as tbl:
                        tbl.item(row, col).setText('{:.1f}'.format(t_lox))
                except materials.MaterialNotDefined:
                    pass

        self.config.set('coating.layers', self.get_layers())

    @pyqtSlot()
    def on_btnWizard_clicked(self):
        wizard = Wizard(self)
        if wizard.run():
            self.initialise_stack()

    ### SLOTS - PLOT TAB

    @pyqtSlot(int)
    def on_cbPlotType_currentIndexChanged(self, plotidx):
        plot = str(self.cbPlotType.itemData(plotidx).toString())
        self.update_plot_widget(plot) 
        self.config.set('plot.plottype', plot)


    ### SLOTS - MATERIALS TAB

    @pyqtSlot()
    def update_material_list(self):
        # save selection
        sub = str(self.cbSubstrate.currentText())
        sup = str(self.cbSuperstrate.currentText())
        materials = [m for m in self.materials.list_materials()]
        self.lstMaterials.clear()
        self.lstMaterials.addItems(materials)
        with block_signals(self.cbSubstrate) as cbsub, block_signals(self.cbSuperstrate) as cbsup:
            self.cbSuperstrate.clear()
            self.cbSubstrate.clear()
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
    def on_actionExportData_triggered(self):
        xdata = []
        ydata = []
        labels = []
        xlabel = ''
        for ax in self.pltMain.figure.axes:
            if not xlabel:
                xlabel = ax.get_xlabel()
            legend = ax.get_legend()
            if legend:
                for t in legend.get_texts():
                    labels.append(t.get_text())
            for line in ax.lines:
                xdata.append(line.get_xdata())
                ydata.append(line.get_ydata())
        
        labels.insert(0, xlabel)
        # TODO: y labels, plot title?

        if len(ydata) == 0:
            QMessageBox.information(self, 'Empty plot not exported',
                'Plot is empty, so there\'s no data to be exported.', QMessageBox.Ok)
            return

        filename = QFileDialog.getSaveFileName(self, 'Export Plot Data',
                            splitext(self.filename)[0]+'.dat', 'ASCII Data (*.dat)');
        if filename:
            export_data(str(filename), xdata, ydata, labels)

    @pyqtSlot()
    def on_actionSave_triggered(self):
        filename = str(QFileDialog.getSaveFileName(self, 'Save Coating Project',
                            self.filename, 'Coating Project Files (*.cgp)'))
        if filename:
            geometry = self.saveGeometry().toHex().data()
            self.config.set('window_geometry', geometry)
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

            if compare_versions(version_number, self.config.get('version_number')) < 0:
                QMessageBox.warning(self, 'Newer file version detected',
                    'This coating project was created with a newer version of CoatingGUI. This may or may not work out well...', QMessageBox.Ok)
            self.initialise_plotoptions()
            self.initialise_materials()
            self.initialise_stack()

    @pyqtSlot()
    def on_actionAbout_triggered(self):
        QMessageBox.about(self, version_string,
            """
Please visit GitHub to obtain the latest version of this software:
https://www.github.com/sestei/dielectric

This work is licensed under the Creative Commons Attribution-NonCommercial-
ShareAlike 4.0 International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
            """)
