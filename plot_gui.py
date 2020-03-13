"""
This opens a gui and lets the user update with their chosen .dat
"""
#!/usr/bin/python

from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pyqtgraph import *
from pyqtgraph.parametertree import *
import sys
import glob
import pandas as pd
import numpy as np

"""
Add button to export plot with Matplotlib and save to .png -- weird bug in export pyqtgraph for some reason
"""


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class PlotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.file = r"Filename"
        self.prev_file = self.file
        self.plot_multiple = False
        self.plot_avg = False
        self.plot_stack = False
        self.plot_normal = False
        # self.plot_name = False
        self.plot_count = 0
        self.plot_delimiter = ','
        self.start_time = "Default (time[0])"
        self.initUI()

        self.show()

    def initUI(self):

        self.params = [
            {'name': 'Plot options', 'type': 'group', 'children': [
                {'name': 'Plot multiple', 'type': 'bool', 'value': self.plot_multiple, 'tip':
                    "This will plot multiple charts"},
                {'name': 'Average', 'type': 'bool', 'value': self.plot_avg, 'tip':
                    "This will average similarly named files"},
                {'name': 'Normalize', 'type': 'bool', 'value': self.plot_normal, 'tip':
                    "This will normalize data"},
                {'name': 'Plot stack', 'type': 'bool', 'value': self.plot_stack, 'tip':
                    "This will stack plots"},
                {'name': 'Start time', 'type': 'str', 'value': self.start_time, 'tip':
                    "This will start the plot at time entered"},
                # {'name': 'Use filename as name', 'type': 'bool', 'value': self.plot_name, 'tip':
                #     "Uses data name in file if false, uses plot title if true"},
                {'name': 'Delimiter', 'type': 'str', 'value': self.plot_delimiter, 'tip':
                    "Spacing in data file"}
            ]}]

        self.filestuff = [{'name': 'File', 'type': 'group', 'children': [
            {'name': 'Update plot', 'type': 'action'},
            {'name': 'Clear all', 'type': 'action'},
            {'name': 'Clear last', 'type': 'action'},
            {'name': 'Choose file', 'type': 'action'},
            {'name': 'File:', 'type': 'str', 'value': self.file},
            # {'name': 'Export last', 'type': 'action'}
        ]}]

        self.p = Parameter.create(name='params', type='group', children=self.params)
        self.f = Parameter.create(name='filestuff', type='group', children=self.filestuff)

        self.t = ParameterTree()
        self.t.setParameters(self.p, showTop=False)
        self.t.setWindowTitle('Plot parameters')

        self.tf = ParameterTree()
        self.tf.setParameters(self.f, showTop=False)
        self.tf.setWindowTitle('File parameters')

        Layout = QGridLayout()

        self.win = GraphicsLayoutWidget()
        self.showMaximized()

        setConfigOptions(foreground='w', background='k')

        self.setLayout(Layout)

        Layout.addWidget(self.tf, 0, 1)  # deleted some shit here
        Layout.addWidget(self.t, 0, 2)
        Layout.addWidget(self.win, 1, 0, 1, 3)

        self.f.param('File', 'Choose file').sigActivated.connect(self.chooseFile)
        self.f.param('File', 'Update plot').sigActivated.connect(self.makePlot)
        self.f.param('File', 'Clear all').sigActivated.connect(self.clearPlot)
        # self.f.param('File', 'Export last').sigActivated.connect(self.exportPlot)
        self.f.param('File', 'Clear last').sigActivated.connect(self.clearLast)
        self.p.param('Plot options', 'Plot multiple').sigStateChanged.connect(self.plotMult)
        self.p.param('Plot options', 'Average').sigStateChanged.connect(self.plotAvg)
        self.p.param('Plot options', 'Normalize').sigStateChanged.connect(self.plotNormal)
        self.p.param('Plot options', 'Plot stack').sigStateChanged.connect(self.plotStack)
        self.p.param('Plot options', 'Start time').sigValueChanged.connect(self.startTime)
        # self.p.param('Plot options', 'Use filename as name').sigValueChanged.connect(self.plotName)
        self.p.param('Plot options', 'Delimiter').sigValueChanged.connect(self.setDelim)

    def chooseFile(self):
        self.file = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                "", "Data Files (*.dat);;CSV (*.csv);;"
                                                    "Text Files (*.txt);;Python Files (*.py)")[0]
        try:
            fileopen = open(self.file, 'r')
            self.prev_file = self.file
        except:
            # QMessageBox.about(self, "Error", "No file chosen.")
            self.file = self.prev_file
            if self.file == "Filename":
                self.file = r"C:\Users\bdprice\Documents\Data\UV Vis\PR\20200309" \
                            r"\E108Q 174 Monomer\M01_174_108_mono_activated_410nm_Scan000.dat"
            fileopen = open(self.file, 'r')

        self.f.param('File', 'File:').setValue(self.file.split('/')[-1])
        self.lines = fileopen.readlines()
        fileopen.close()

    def clearPlot(self):
        self.win.clear()
        try:
            delattr(self, 'pl')
        except AttributeError:
            QMessageBox.about(self, "Error", "No plot to clear.")
        self.plot_count = 0

    def clearLast(self):
        try:
            if self.plot_multiple:
                self.win.removeItem(self.pl)
            else:
                self.clearPlot()
            self.plot_count = 0
        except AttributeError:
            QMessageBox.about(self, "Error", "No plot to clear.")

    def plotAvg(self):
        if self.plot_avg is False:
            self.plot_avg = True
        else:
            self.plot_avg = False
        self.p.param('Plot options', 'Average').setValue(self.plot_avg)

    def plotNormal(self):
        if self.plot_normal is False:
            self.plot_normal = True
        else:
            self.plot_normal = False

        self.p.param('Plot options', 'Normalize').setValue(self.plot_normal)

    def plotMult(self):
        if self.plot_multiple is False:
            self.plot_multiple = True
        else:
            self.plot_multiple = False
        self.p.param('Plot options', 'Plot multiple').setValue(self.plot_multiple)

    def plotStack(self):
        if self.plot_stack is False:
            self.plot_stack = True
        else:
            self.plot_stack = False
        self.p.param('Plot options', 'Plot stack').setValue(self.plot_stack)

    # def plotName(self):
    #     if self.plot_name is False:
    #         self.plot_name = True
    #     else:
    #         self.plot_name = False
    #     self.p.param('Plot options', 'Use filename as name').setValue(self.plot_name)

    def startTime(self):
        if is_number(self.p.param('Plot options', 'Start time').value()):
            self.start_time = self.p.param('Plot options', 'Start time').value()
        else:
            self.start_time = "Default (time[0])"
        self.p.param('Plot options', 'Start time').setValue(self.start_time)

    def setDelim(self):

        self.plot_delimiter = self.p.param('Plot options', 'Delimiter').value()

    def makePlot(self):

        try:

            if self.plot_multiple:
                self.pl = self.win.addPlot()  # this will create additional plots in same window instead of re-plotting
                self.legend = self.pl.addLegend()
            elif self.plot_stack:
                if not hasattr(self, 'pl'):
                    self.pl = self.win.addPlot()
                    self.legend = self.pl.addLegend()
                else:
                    pass
            else:
                self.win.clear()
                self.pl = self.win.addPlot()
                self.legend = self.pl.addLegend()

            self.begin_idx = self.begin_line = self.data_type = self.data_types = self.footerskip = -1

            self.getLines()

            if self.begin_line == -1:
                QMessageBox.about(self, "Error", "Delimiter not in file. Attempting to use csv.")
                self.plot_delimiter = ','

                self.getLines()

            self.data = pd.read_csv(self.file, sep=self.plot_delimiter, header=self.begin_line - 1,
                                    skipfooter=self.footerskip, engine='python',
                                    index_col=False).to_numpy()

            if self.plot_avg:
                if is_number(self.file.split('.')[-2][-3:]):
                    self.dataset = self.file.split('.')[-2][:-3]
                    filelist = glob.glob(self.dataset + '*' + self.file.split('.')[-1])
                else:
                    self.dataset = self.file.split('.')[-2]
                    filelist = glob.glob(self.dataset + '*' + self.file.split('.')[-1])

                datalist = np.zeros(np.shape(self.data))
                count = 0
                for file in filelist:
                    datalist = datalist + pd.read_csv(file,
                                                      sep=self.plot_delimiter, header=self.begin_line - 1,
                                                      skipfooter=self.footerskip, engine='python',
                                                      index_col=False).to_numpy()
                    count += 1

                self.data = datalist / count

            if is_number(self.start_time):
                start = float(self.start_time)
                self.data = self.data[np.where(self.data[:, 0] >= start)]

            self.plot_name = self.file.split('/')[-1].split('.')[0].replace('_', ' ')

            # if self.plot_avg or self.plot_name:
            #     self.plot_title = ' '.join(self.plot_name.split(' ')[:-1]) + ' average'
            # elif self.plot_stack:
            #     self.plot_name = ' '.join(self.plot_name.split(' ')[:-1]) + ' average'
            # else:
            #     self.plot_title = self.plot_name

            if self.plot_stack:
                self.plot_name = ' '.join(self.plot_name.split(' ')[:-1])
            elif self.plot_avg:
                self.plot_name = ' '.join(self.plot_name.split(' ')[:-1]) + ' average'
            else:
                self.plot_title = self.plot_name

            self.updatePlot()

        except AttributeError:
            QMessageBox.about(self, "Error", "That file did not parse correctly.")

        except ValueError:
            QMessageBox.about(self, "Error", "This is not a comma-separated file and the correct "
                                             "delimiter was not specified.")

        self.p.param('Plot options', 'Delimiter').setValue(self.plot_delimiter)

    def getLines(self):

        strippedlines = [ii.rstrip('\n').rstrip(',') for ii in self.lines]

        for line in strippedlines:
            items = [is_number(ii) for ii in line.split(self.plot_delimiter)]
            if not all(items):
                pass
            else:
                self.begin_line = strippedlines.index(line)
                self.data_type = self.begin_line - 1
                self.data_types = [ii.rstrip('"').lstrip('"') for ii
                                   in strippedlines[self.data_type].split(self.plot_delimiter)]
                break

        if self.begin_line != -1:
            for line in strippedlines[::-1]:
                items = [is_number(ii) for ii in line.split(self.plot_delimiter)]
                if all(items):
                    self.end_line = strippedlines.index(line) + 1
                    break
                else:
                    self.end_line = strippedlines.index(strippedlines[-1])

            self.footerskip = len(strippedlines) - self.end_line

    def updatePlot(self):

        if self.plot_normal:
            for ii in range(1, len(self.data_types)):
                if np.max(np.absolute(self.data[:, ii])) == 0:
                    pass
                else:
                    self.data[:, ii] = self.data[:, ii] / np.max(np.absolute(self.data[:, ii]))

        if self.plot_stack:
            for ii in range(1, len(self.data_types)):
                self.pl.plot(self.data[:, 0], self.data[:, ii], pen=ii + self.plot_count, name=self.plot_name)
            self.plot_count += 1
        else:
            for ii in range(1, len(self.data_types)):
                self.pl.plot(self.data[:, 0], self.data[:, ii], pen=ii, name=self.data_types[ii].rstrip('\n'))
            self.pl.setTitle(self.plot_title)

        self.pl.enableAutoRange()
        if self.plot_normal:
            self.pl.setLabel('left', 'Magnitude (normalized)')
        else:
            self.pl.setLabel('left', 'Magnitude')
        self.pl.setLabel('bottom', self.data_types[0])

        self.pl.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Enter:
            self.makePlot()
        elif e.key() == 16777220:  # enter for Mac, will need to find out enter for windows
            self.makePlot()
        else:
            QMessageBox.about(self, "Error", f"No command bound to {e.key()}.")


def main():
    app = QApplication(sys.argv)
    window = PlotGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
else:
    main()
