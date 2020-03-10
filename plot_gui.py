"""
This opens a gui and lets the user update with their chosen .dat
"""

#!/usr/bin/env python3

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
To do: add plot stacking option to compare multiple different plots
Add button to export plot with Matplotlib and save to .png
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
        self.plot_multiple = False
        self.plot_avg = False
        self.start_time = "Default (i.e. time[0])"
        self.initUI()

        self.show()

    def initUI(self):

        self.params = [
            {'name': 'Plot options', 'type': 'group', 'children': [
                {'name': 'Plot multiple', 'type': 'bool', 'value': self.plot_multiple, 'tip':
                    "This will plot multiple charts"},
                {'name': 'Average', 'type': 'bool', 'value': self.plot_avg, 'tip':
                    "This will average similarly named files"},
                {'name': 'Start time', 'type': 'str', 'value': self.start_time, 'tip':
                    "This will start the plot at time entered"}
        ]}]

        self.filestuff = [{'name': 'File', 'type': 'group', 'children': [
                {'name': 'Update plot', 'type': 'action'},
                {'name': 'Choose file', 'type': 'action'},
                {'name': 'File:', 'type': 'str', 'value': self.file}
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
        self.p.param('Plot options', 'Plot multiple').sigStateChanged.connect(self.plotMult)
        self.p.param('Plot options', 'Average').sigStateChanged.connect(self.plotAvg)
        self.p.param('Plot options', 'Start time').sigValueChanged.connect(self.startTime)

    def chooseFile(self):
        self.file = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                "", "Data Files (*.dat);;CSV (*.csv);;Python Files (*.py)")[0]
        try:
            fileopen = open(self.file, 'r')
            self.prev_file = self.file
        except:
            # QMessageBox.about(self, "Error", "No file chosen.")
            self.file = self.prev_file
            fileopen = open(self.file, 'r')

        self.f.param('File', 'File:').setValue(self.file.split('/')[-1])
        self.lines = fileopen.readlines()
        fileopen.close()


    def plotAvg(self):
        if self.plot_avg is False:
            self.plot_avg = True
        else:
            self.plot_avg = False
        self.p.param('Plot options', 'Average').setValue(self.plot_avg)


    def plotMult(self):
        if self.plot_multiple is False:
            self.plot_multiple = True
        else:
            self.plot_multiple = False
        self.p.param('Plot options', 'Plot multiple').setValue(self.plot_multiple)


    def startTime(self):
        if is_number(self.p.param('Plot options', 'Start time').value()):
            self.start_time = self.p.param('Plot options', 'Start time').value()
        else:
            self.start_time = "Default (i.e. time[0])"
        self.p.param('Plot options', 'Start time').setValue(self.start_time)


    def makePlot(self):

        if self.plot_multiple:
            pass  # this will create additional plots in same window instead of re-plotting
        else:
            self.win.clear()

        self.pl = self.win.addPlot()

        self.begin_idx = self.begin_line = self.data_type = self.data_types = -1

        for line in self.lines:
            items = [is_number(ii) for ii in line.split(',')]
            if not any(items):
                pass
            else:
                self.begin_line = self.lines.index(line)
                self.data_type = self.begin_line - 1
                self.data_types = self.lines[self.data_type].split(',')
                break

        try:
            self.data = np.array(pd.read_csv(self.file, sep=',', header=self.begin_line - 1, engine='python'))

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
                    datalist = datalist + np.array(pd.read_csv(file,
                                                               sep=',', header=self.begin_line - 1,
                                                               engine='python'))
                    count += 1

                self.data = datalist / count

            if is_number(self.start_time):
                start = float(self.start_time)
                self.data = self.data[np.where(self.data[:, 0] >= start)]

            self.plot_title = self.file.split('/')[-1].split('.')[0].replace('_', ' ')

            if self.plot_avg:
                self.plot_title = ' '.join(self.plot_title.split(' ')[:-1]) + ' average'

            self.updatePlot()

        except:

            QMessageBox.about(self, "Error", "That file did not parse correctly.")


    def updatePlot(self):

        self.legend = self.pl.addLegend()
        self.pl.setTitle(self.plot_title)
        self.pl.enableAutoRange()
        self.pl.setLabel('left', 'Magnitude')
        self.pl.setLabel('bottom', self.data_types[0])

        for ii in range(1, len(self.data_types)):
            self.pl.plot(self.data[:, 0], self.data[:, ii], pen=ii, name=self.data_types[ii].rstrip('\n'))

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
