"""
This allows a user to import a csv file from plot_gui app export and the user can live-update their matplotlib plot
in window for final export to png
"""

import sys

import matplotlib as mplb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pyqtgraph import *
from pyqtgraph.parametertree import *

mplb.use('QT5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.file = "Filename"
        self.title = "Title"
        self.yax = "Y"
        self.xax = "X"
        self.yticks = "Default"
        self.xticks = "Default"
        self.log = "x, y, or 'x, y'"
        self.labels = "Default"
        self.font = 14
        self.x_mode = self.y_mode = False

        self.xticks_entered = self.yticks_entered = self.xlabel_entered = \
            self.ylabel_entered = self.title_entered = self.user_labels =\
            False

        self.labels_entered = True

        mplb.rcParams.update({
            'figure.autolayout': True,
            'font.size': self.font
        })
        plt.rcParams.update({
            'figure.autolayout': True,
            'font.size': self.font
        })

        self.initUI()
        self.show()

    def initUI(self):
        self.plot = MplCanvas(self, width=5, height=4, dpi=100)

        self.entries = [{
            'name':
            'Plot options',
            'type':
            'group',
            'children': [{
                'name': 'Choose file',
                'type': 'action',
            }, {
                'name': 'File:',
                'type': 'str',
                'value': self.file,
                'tip': 'Name of chosen file'
            }, {
                'name': 'Title:',
                'type': 'str',
                'value': self.title,
                'tip': 'Title of plot window'
            }, {
                'name': 'Y-axis:',
                'type': 'str',
                'value': self.yax,
                'tip': 'Y-axis label'
            }, {
                'name': 'Y ticks:',
                'type': 'str',
                'value': self.yticks,
                'tip': 'Y-axis ticks'
            }, {
                'name': 'X-axis:',
                'type': 'str',
                'value': self.xax,
                'tip': 'X-axis label'
            }, {
                'name': 'X ticks:',
                'type': 'str',
                'value': self.xticks,
                'tip': 'X-axis ticks'
            }, {
                'name': 'Log:',
                'type': 'str',
                'value': self.log,
                'tip': "x, y, or 'x, y'"
            }, {
                'name': 'Plot labels:',
                'type': 'str',
                'value': self.labels,
                'tip': 'Comma-separated legend entries'
            }, {
                'name': 'Font size:',
                'type': 'str',
                'value': self.font,
                'tip': 'Standard for figures is 16'
            }, {
                'name': 'Update plot',
                'type': 'action'
            }, {
                'name': 'Export png',
                'type': 'action'
            }]
        }]

        self.params = Parameter.create(name='entries',
                                       type='group',
                                       children=self.entries)

        self.tree = ParameterTree()
        self.tree.setParameters(self.params, showTop=False)
        self.tree.setWindowTitle('Plot options')

        self.params.param('Plot options',
                          'Choose file').sigActivated.connect(self.chooseFile)
        self.params.param('Plot options',
                          'Update plot').sigActivated.connect(self.updatePlot)
        self.params.param('Plot options',
                          'Export png').sigActivated.connect(self.exportPNG)
        self.params.param('Plot options',
                          'Title:').sigValueChanged.connect(self.setTitle)
        self.params.param('Plot options',
                          'Y-axis:').sigValueChanged.connect(self.setYax)
        self.params.param('Plot options',
                          'Y ticks:').sigValueChanged.connect(self.setYTicks)
        self.params.param('Plot options',
                          'X-axis:').sigValueChanged.connect(self.setXax)
        self.params.param('Plot options',
                          'X ticks:').sigValueChanged.connect(self.setXTicks)
        self.params.param('Plot options',
                          'Log:').sigValueChanged.connect(self.setLog)
        self.params.param('Plot options',
                          'Plot labels:').sigValueChanged.connect(
                              self.setLabels)
        self.params.param('Plot options',
                          'Font size:').sigValueChanged.connect(
                              self.setFontSize)

        # self.toolbar = NavigationToolbar(sc, self)

        layout = QHBoxLayout()
        layout.addWidget(self.tree, 2)
        layout.addWidget(self.plot, 3)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # self.showMaximized()

    def setYTicks(self):
        if self.params.param('Plot options', 'Y ticks:').value() != "Default":
            if self.params.param('Plot options',
                                 'Y ticks:').value() == (' ' or ''):
                self.yticks = []
                self.yticks_entered = True
            else:
                try:
                    self.yticks = [
                        float(ii.strip(' ')) for ii in self.params.param(
                            'Plot options', 'Y ticks:').value().split(',')
                    ]
                    self.yticks_entered = True
                except ValueError:
                    self.params.param('Plot options',
                                      'Y ticks:').setValue("Default")

    def setXTicks(self):
        if self.params.param('Plot options', 'X ticks:').value() != "Default":
            if self.params.param('Plot options',
                                 'X ticks:').value() == (' ' or ''):
                self.xticks = []
                self.xticks_entered = True
            else:
                try:
                    self.xticks = [
                        float(ii.strip(' ')) for ii in self.params.param(
                            'Plot options', 'X ticks:').value().split(',')
                    ]
                    self.xticks_entered = True
                except ValueError:
                    self.params.param('Plot options',
                                      'X ticks:').setValue("Default")

    def setLog(self):
        log = self.params.param('Plot options', 'Log:').value()
        log_set = set([ii.strip(' ') for ii in log.split(',')])

        if 'x' in log_set:
            self.x_mode = True
        else:
            self.x_mode = False

        if 'y' in log_set:
            self.y_mode = True
        else:
            self.y_mode = False

    def setXax(self):
        if self.params.param('Plot options', 'X-axis:').value() != "X":
            self.xax = self.params.param('Plot options', 'X-axis:').value()
            self.xlabel_entered = True

    def setYax(self):
        if self.params.param('Plot options', 'Y-axis:').value() != "Y":
            self.yax = self.params.param('Plot options', 'Y-axis:').value()
            self.ylabel_entered = True

    def setTitle(self):
        if self.params.param('Plot options', 'Title:').value() != "Title":
            self.title = self.params.param('Plot options', 'Title:').value()
            self.title_entered = True

    def setLabels(self):
        self.labels = self.params.param('Plot options', 'Plot labels:').value()

        if self.labels != "Default":
            if self.labels == (' ' or ''):
                self.labels_entered = False
            else:
                self.labels = [
                    ii.strip(' ') for ii in self.params.param(
                        'Plot options', 'Plot labels:').value().split(',')
                ]
                self.labels_entered = True
                self.user_labels = True
        else:
            self.labels = "Default"
            self.params.param('Plot options',
                              'Plot labels:').setValue(self.labels)
            self.labels_entered = True
            self.user_labels = False

    def setFontSize(self):
        try:
            self.font = int(
                self.params.param('Plot options', 'Font size:').value())
            mplb.rcParams.update({'font.size': self.font})
            plt.rcParams.update({'font.size': self.font})
        except ValueError:
            self.params.param('Plot options', 'Font size:').setValue(self.font)

    def chooseFile(self):
        """
        Opens dialog and returns filename for plotting. If filename isn't found, returns file for a file on bprice
        computer... not super helpful for distribution and wi
        :return:
        """
        self.file = QFileDialog.getOpenFileName(
            self, "Plot file", "", "CSV (*.csv);;Data Files (*.dat);;"
            "Text Files (*.txt)")[0]
        try:
            fileopen = open(self.file, 'r')
            self.prev_file = self.file

            self.lines = fileopen.readlines()
            fileopen.close()

        except FileNotFoundError:
            self.file = r"No file selected"

        self.params.param('Plot options',
                          'File:').setValue(self.file.split('/')[-1])

    def updatePlot(self):
        self.data = pd.read_csv(self.file, engine='python',
                                index_col=False).to_numpy()

        self.plot.axes.cla()

        if self.ylabel_entered:
            self.plot.axes.set_ylabel(self.yax)
            self.plot.axes.yaxis.label.set_fontsize(self.font)

        if self.xlabel_entered:
            self.plot.axes.set_xlabel(self.xax)
            self.plot.axes.xaxis.label.set_fontsize(self.font)

        if self.title_entered:
            self.plot.axes.set_title(self.title)
            self.plot.axes.title.set_fontsize(self.font)

        if self.yticks_entered:
            self.plot.axes.set_yticks(self.yticks)
            try:
                self.plot.axes.get_yticklabels().set_fontsize(self.font)
            except AttributeError:
                pass

        if self.xticks_entered:
            self.plot.axes.set_xticks(self.xticks)
            try:
                self.plot.axes.get_xticklabels().set_fontsize(self.font)
            except AttributeError:
                pass

        # self.plot.axes.tight_layout()

        if self.labels_entered and not self.user_labels:
            self.labels = []

            for ii in range(1, len(self.data[0, :])):
                self.labels.append(f"Data {ii}")
            self.labels_entered = True

        if self.labels_entered:
            for ii in range(len(self.data[0, :]) - 1):
                self.plot.axes.plot(self.data[:, 0],
                                    self.data[:, ii + 1],
                                    label=self.labels[ii])
            # self.plot.axes.legend()
            self.plot.axes.legend().set_draggable(True)
            # print(self.plot.axes.legend().get_window_extent())
        else:
            for ii in range(len(self.data[0, :]) - 1):
                self.plot.axes.plot(self.data[:, 0], self.data[:, ii + 1])

        if self.y_mode:
            self.plot.axes.set_yscale('log')
        else:
            self.plot.axes.ticklabel_format(axis='y',
                                            style='sci',
                                            scilimits=(-2, 2),
                                            useMathText=True)

        if self.x_mode:
            self.plot.axes.set_xscale('log')
        else:
            self.plot.axes.ticklabel_format(axis='x',
                                            style='sci',
                                            scilimits=(-2, 2),
                                            useMathText=True)

        self.plot.draw()

    def exportPNG(self):

        self.plot.fig.savefig('.'.join(self.file.split('.')[:-1]) + '.png')


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
else:
    main()
