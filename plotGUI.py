"""
This opens a gui and lets the user update with their chosen .dat
"""
# !/opt/anaconda3/bin/python

# need to make sure when creating app that I use python3 because that is in usr/local/bin, which is where my local
# python dist and py2app are located

import glob
import platform
import sys

# for export class
import matplotlib as mplb
import numpy as np
import pandas as pd
from cycler import cycler
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
# from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,
                             QMainWindow, QMessageBox, QWidget)
from pyqtgraph import (GraphicsLayoutWidget, LinearRegionItem, mkPen,
                       setConfigOptions)
from pyqtgraph.parametertree import Parameter, ParameterTree

# import csv_fig  # error appears when using this submodule
"""
TODO
[X] Add comments
[X] Allow user to select which column they'd like as their x axis
[ ] Add functionality to transpose data matrix
[X] Deselect all when plotting
"""


def is_number(s):
    """
    :param s:
    :return:
    stackexchange function to check if user input is a feasible number
    """
    try:
        float(s)

        return True
    except ValueError:
        return False


class PlotGUI(QWidget):
    """
    Main window of plotting app
    """
    def __init__(self):
        """
        Define initialization values of user inputs
        """
        super().__init__()
        self.file = r"Filename"
        self.prev_file = self.file
        self.current_file = r"Filename"
        self.plot_multiple = False
        self.plot_avg = False
        self.plot_stack = False
        self.plot_normal = False
        self.data_types = ['null']
        self.plot_count = 0
        self.plot_delimiter = ','
        self.start_x = "Default (x[0])"
        self.end_x = "Default (x[-1])"
        self.plot_axes = 'xlin, ylin'
        self.x_string = "Default"
        self.x_index = 0  # default value
        self.changedX = False
        self.possible_axis = {"xlog", "ylog", "xlin", "ylin"}
        self.real_axes = False
        self.select_all = True
        self.setAcceptDrops(True)
        self.lr = LinearRegionItem()
        self.region = [0, 0]
        self.window_string = f"width: {np.abs(self.region[1]-self.region[0]):.2f}; start: {self.region[0]:.2f}; end: {self.region[1]:.2f}"

        self.initUI()

        self.show()

    def initUI(self):
        """
        Create parametertrees and window
        :return:
        """

        self.params = [{
            'name':
            'Plot options',
            'type':
            'group',
            'children': [
                {
                    'name': 'Select all',
                    'type': 'bool',
                    'value': self.select_all,
                    'tip': "Turns off all plot lines"
                },
                {
                    'name': 'Plot multiple',
                    'type': 'bool',
                    'value': self.plot_multiple,
                    'tip': "This will plot multiple charts"
                },
                {
                    'name': 'Average',
                    'type': 'bool',
                    'value': self.plot_avg,
                    'tip': "This will average similarly named files"
                },
                {
                    'name': 'Normalize',
                    'type': 'bool',
                    'value': self.plot_normal,
                    'tip': "This will normalize data"
                },
                {
                    'name': 'Plot stack',
                    'type': 'bool',
                    'value': self.plot_stack,
                    'tip': "This will stack plots"
                },
                {
                    'name': 'Start x',
                    'type': 'str',
                    'value': self.start_x,
                    'tip': "This will start the plot at x val entered"
                },
                {
                    'name': 'End x',
                    'type': 'str',
                    'value': self.end_x,
                    'tip': "This will end the plot at x val entered"
                },
                {
                    'name': 'Axis scale',
                    'type': 'str',
                    'value': self.plot_axes,
                    'tip':
                    "xlin, ylin, xlog, ylog; default x,y lin if unspecified"
                },
                # {'name': 'Use filename as name', 'type': 'bool', 'value': self.plot_name, 'tip':
                #     "Uses data name in file if false, uses plot title if true"},
                {
                    'name': 'Delimiter',
                    'type': 'str',
                    'value': self.plot_delimiter,
                    'tip': "Spacing in data file"
                }
            ]
        }]

        self.filestuff = [{
            'name':
            'File',
            'type':
            'group',
            'children': [{
                'name': 'Update plot',
                'type': 'action'
            }, {
                'name': 'Clear all',
                'type': 'action'
            }, {
                'name': 'Clear last',
                'type': 'action'
            }, {
                'name': 'Choose file',
                'type': 'action'
            }, {
                'name': 'File:',
                'type': 'str',
                'value': self.file
            }, {
                'name': 'Create png',
                'type': 'action'
            }]
        }]

        self.xaxischilds = [{
            'name':
            'x axis',
            'type':
            'group',
            'children': [{
                'name': 'x axis',
                'type': 'str',
                'value': self.x_string,
                'tip': 'Type name for x axis data'
            }, {
                'name': 'Selection',
                'type': 'str',
                'value': self.window_string,
                'tip': 'Width of selection window'
            }]
        }]

        self.child_list = []
        self.plot_show = {}

        for name in self.data_types:
            self.child_list.append({'name': name, 'type': 'bool'})
            self.plot_show[name] = False

        self.plotlines = [{
            'name': 'Plot lines',
            'type': 'group',
            'children': self.child_list
        }]

        self.x = Parameter.create(name='xaxischilds',
                                  type='group',
                                  children=self.xaxischilds)

        self.p = Parameter.create(name='params',
                                  type='group',
                                  children=self.params)
        self.f = Parameter.create(name='filestuff',
                                  type='group',
                                  children=self.filestuff)
        self.l = Parameter.create(name='plotlines',
                                  type='group',
                                  children=self.plotlines)

        self.xa = ParameterTree()
        self.xa.setParameters(self.x, showTop=False)
        self.xa.setWindowTitle('X axis')

        self.t = ParameterTree()
        self.t.setParameters(self.p, showTop=False)
        self.t.setWindowTitle('Plot parameters')

        self.tf = ParameterTree()
        self.tf.setParameters(self.f, showTop=False)
        self.tf.setWindowTitle('File parameters')

        self.tff = ParameterTree()
        self.tff.setParameters(self.l, showTop=False)
        self.tff.setWindowTitle('Plot lines')

        Layout = QGridLayout()

        self.win = GraphicsLayoutWidget()
        self.showMaximized()

        setConfigOptions(foreground='w', background='k')

        self.setLayout(Layout)

        Layout.addWidget(self.tf, 0, 0, 2, 1)  # deleted some shit here
        Layout.addWidget(self.t, 0, 1, 2, 1)
        Layout.addWidget(self.tff, 0, 2, 1, 1)
        Layout.addWidget(self.xa, 1, 2, 1, 1)
        # position, then size (want full bottom row)
        Layout.addWidget(self.win, 2, 0, 2, 3)

        self.x.param('x axis', 'x axis').sigValueChanged.connect(self.xChoice)

        self.f.param('File',
                     'Choose file').sigActivated.connect(self.chooseFile)
        self.f.param('File', 'Update plot').sigActivated.connect(self.makePlot)
        self.f.param('File', 'Clear all').sigActivated.connect(self.clearPlot)
        self.f.param('File', 'Clear last').sigActivated.connect(self.clearLast)
        self.f.param('File', 'Create png').sigActivated.connect(self.exportPNG)

        self.p.param('Plot options',
                     'Select all').sigValueChanged.connect(self.selectAll)
        self.p.param('Plot options',
                     'Plot multiple').sigStateChanged.connect(self.plotMult)
        self.p.param('Plot options',
                     'Average').sigStateChanged.connect(self.plotAvg)
        self.p.param('Plot options',
                     'Normalize').sigStateChanged.connect(self.plotNormal)
        self.p.param('Plot options',
                     'Plot stack').sigStateChanged.connect(self.plotStack)
        self.p.param('Plot options',
                     'Start x').sigValueChanged.connect(self.startX)
        self.p.param('Plot options',
                     'End x').sigValueChanged.connect(self.endX)
        self.p.param('Plot options',
                     'Axis scale').sigValueChanged.connect(self.axesSet)
        self.p.param('Plot options',
                     'Delimiter').sigValueChanged.connect(self.setDelim)

    def dragEnterEvent(self, event):
        """
        Will allow user to drop data file onto gui for file input

        File locations are stored in fname
        :param e:
        :return:
        """

        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Auto-plots if file is valid
        :return:
        """
        files = [str(u.toLocalFile()) for u in event.mimeData().urls()]
        plot_stack = self.plot_stack

        for file in files:
            try:

                if not self.plot_stack and not self.plot_multiple and hasattr(
                        self, 'pl'):
                    self.clearLast()

                if len(files) > 1:
                    self.plot_stack = True

                self.file = file

                fileopen = open(self.file, 'r')
                self.prev_file = self.file

                self.lines = fileopen.readlines()
                fileopen.close()

                self.f.param('File',
                             'File:').setValue(self.file.split('/')[-1])
                self.makePlot()

            except FileNotFoundError:
                self.file = self.prev_file

            except UnicodeDecodeError:
                QMessageBox.about(
                    self, "Error",
                    "Plotter only excepts .txt, .csv, .dat, and .py filetypes")
                self.file = self.prev_file
                files.remove(file)

        self.plot_stack = plot_stack
        self.p.param('Plot options', 'Plot stack').setValue(self.plot_stack)

    def chooseFile(self):
        """
        Opens dialog and returns filename for plotting. If filename isn't found, returns file for a file on bprice
        computer... not super helpful for distribution and wi
        :return:
        """
        self.file = QFileDialog.getOpenFileName(
            self, "Plot file", "", "Text Files (*.txt);;Data Files (*.dat);;"
            "CSV (*.csv);;Python Files (*.py)")[0]
        try:
            fileopen = open(self.file, 'r')
            self.prev_file = self.file

            self.lines = fileopen.readlines()
            fileopen.close()
        except FileNotFoundError:
            self.file = r"No file selected"

        self.f.param('File', 'File:').setValue(self.file.split('/')[-1])

    def clearPlot(self):
        """
        This clears the whole plot window
        :return:
        """
        self.win.clear()
        try:
            delattr(self, 'pl')
        except AttributeError:
            QMessageBox.about(self, "Error", "No plot to clear.")
        self.plot_count = 0

    def clearLast(self):  # known bug where clear last clears
        # all if plot multiple has been deselected
        """
        This clears the last plot made. Can't clear more than one plot though, as self.pl no longer exists after it
        was cleared
        :return:
        """
        try:
            if self.plot_multiple:
                self.win.removeItem(self.pl)
            else:
                self.clearPlot()
            self.plot_count = 0
        except AttributeError:
            QMessageBox.about(self, "Error", "No plot to clear.")
        except:
            QMessageBox.about(
                self, "Error",
                "Clear last can only clear the most recent plot. "
                "There is not record of 'last' plot beside the one just cleared."
            )

    def plotShow(self, name):
        """
        This is used to choose which lines to show on a given plot
        :param name:
        :return:
        """

        if self.plot_show[name] is False:
            self.plot_show[name] = True
        else:
            self.plot_show[name] = False

        self.l.param('Plot lines', name).setValue(self.plot_show[name])

    def selectAll(self):
        """
        Selects all plots for easier choosing of one line
        :return:
        """

        for name in self.plot_show:
            self.plot_show[name] = self.p.param('Plot options',
                                                'Select all').value()
            self.l.param('Plot lines', name).setValue(self.plot_show[name])

    def xChoice(self):
        """
        Allows user to input name of data column they'd like as their x axis for plotting
        :return:
        """
        self.x_string = self.x.param('x axis', 'x axis').value()
        self.changedX = True

    def plotAvg(self):
        """
        Averages all similarly-named files if selected
        :return:
        """

        if self.plot_avg is False:
            self.plot_avg = True
        else:
            self.plot_avg = False
        self.p.param('Plot options', 'Average').setValue(self.plot_avg)

    def plotNormal(self):
        """
        Normalizes plotted lines to 1 if selected
        :return:
        """

        if self.plot_normal is False:
            self.plot_normal = True
        else:
            self.plot_normal = False

        self.p.param('Plot options', 'Normalize').setValue(self.plot_normal)

    def plotMult(self):
        """
        Makes a new graph in plot window to compare side by side
        :return:
        """

        if self.plot_multiple is False:
            self.plot_multiple = True
        else:
            self.plot_multiple = False
        self.p.param('Plot options',
                     'Plot multiple').setValue(self.plot_multiple)

    def regionSet(self):
        self.region = self.lr.getRegion()
        self.window_string = f"width: {np.abs(self.region[1]-self.region[0]):.2f}; start: {self.region[0]:.2f}; end: {self.region[1]:.2f}"
        self.x.param('x axis', 'Selection').setValue(self.window_string)

    def plotStack(self):
        """
        Plots new file over old file to compare on top
        :return:
        """

        #        if self.plot_stack is False:
        #            self.plot_stack = True
        #        else:
        #            self.plot_stack = False
        self.plot_stack = self.p.param('Plot options', 'Plot stack').value()
        self.p.param('Plot options', 'Plot stack').setValue(self.plot_stack)

    def startX(self):
        """
        Allows user to select plotting start time
        :return:
        """

        if is_number(self.p.param('Plot options', 'Start x').value()):
            self.start_x = self.p.param('Plot options', 'Start x').value()
        else:
            self.start_x = "Default (x[0])"
        self.p.param('Plot options', 'Start x').setValue(self.start_x)

    def endX(self):
        """
        Allows user to select plotting end time. Error handling controls if end < start, etc.
        :return:
        """

        if is_number(self.p.param('Plot options', 'End x').value()):
            if is_number(self.p.param('Plot options', 'Start x').value()):
                if float(self.p.param('Plot options',
                                      'Start x').value()) < \
                        float(self.p.param('Plot options', 'End x').value()):
                    self.end_x = self.p.param('Plot options', 'End x').value()
                else:
                    QMessageBox.about(self, "Error",
                                      "End time before start time.")
                    self.end_x = "Default (x[-1])"
            else:
                self.end_x = float(
                    self.p.param('Plot options', 'End x').value())
        else:
            self.end_x = "Default (x[-1])"
        self.p.param('Plot options', 'End x').setValue(self.end_x)

    def setDelim(self):
        """Used for non csv files, can plot tab sep or space sep"""

        self.plot_delimiter = self.p.param('Plot options', 'Delimiter').value()

    def axesSet(self):
        """
        Allows user to choose if they want to do log or lin axes on either. Error handling for undefined values if
        values are zero or negative.
        :return:
        """
        axes = [
            ii.strip(' ') for ii in self.p.param(
                'Plot options', 'Axis scale').value().split(',')
        ]

        if all(item in self.possible_axis for item in axes):
            self.each_axis = axes

            self.real_axes = True

        else:
            self.each_axis = ["xlin", "ylin"]
            self.plot_axes = 'xlin, ylin'

            self.real_axes = False
            self.start_x = "Default (x[0])"

            self.p.param('Plot options', 'Axis scale').setValue(self.plot_axes)
            self.p.param('Plot options', 'Start x').setValue(self.start_x)

    def makePlot(self):
        """
        Extracts data and sets up plotting window
        :return:
        """

        try:  # handles how many plots exist and how to clear them depending on user options

            if self.plot_stack:
                if not hasattr(self, 'pl'):
                    self.pl = self.win.addPlot()
                    self.legend = self.pl.addLegend()
                else:
                    pass
            elif self.plot_multiple:
                # this will create additional plots in same window instead of re-plotting
                self.pl = self.win.addPlot()
                self.legend = self.pl.addLegend()
            else:
                self.win.clear()
                self.pl = self.win.addPlot()
                self.legend = self.pl.addLegend()

            self.pl.addItem(self.lr)
            self.lr.sigRegionChanged.connect(self.regionSet)

            self.begin_idx = self.begin_line = self.data_type = self.footerskip = - \
                1  # set to determine if a file
            # doesn't actually have any plottable data

            self.getLines()

            if self.begin_line == -1:
                QMessageBox.about(
                    self, "Error",
                    "Delimiter not in file. Attempting to use csv.")
                self.plot_delimiter = ','

                self.getLines()

            if not self.data_types:  # used to make index column if file doesn't have it
                try:
                    data = np.loadtxt(self.file, delimiter=self.plot_delimiter)
                    self.data = np.hstack(
                        (np.reshape(np.array(list(range(len(data)))),
                                    (len(data), 1)),
                         data))  # numerical index for x axis
                    self.data_types = ['Index'] + [
                        f"Value{ii}" for ii in range(np.shape(data)[1])
                    ]
                except OSError:
                    QMessageBox.about(
                        self, "Error",
                        "No file chosen. Reverting to previous file.")
                    self.file = self.current_file
                    self.f.param('File',
                                 'File:').setValue(self.file.split('/')[-1])
                    data = np.loadtxt(self.file, delimiter=self.plot_delimiter)
                    self.data = np.hstack(
                        (np.reshape(np.array(list(range(len(data)))),
                                    (len(data), 1)),
                         data))  # numerical index for x axis
                    self.data_types = ['Index'] + [
                        f"Value{ii}" for ii in range(np.shape(data)[1])
                    ]

            else:
                try:
                    self.data = np.loadtxt(self.file,
                                           delimiter=self.plot_delimiter,
                                           skiprows=self.begin_line - 1)
                except ValueError:
                    self.data = pd.read_csv(self.file,
                                            sep=self.plot_delimiter,
                                            header=self.begin_line - 1,
                                            skipfooter=self.footerskip,
                                            engine='python',
                                            index_col=False).to_numpy()

            if self.plot_avg:  # handles averaging stupidly... just adds columns and divides by number of files
                if is_number(self.file.split('.')[-2][-3:]):
                    self.dataset = self.file.split('.')[-2][:-3]
                    filelist = glob.glob(self.dataset + '*' +
                                         self.file.split('.')[-1])
                else:
                    self.dataset = self.file.split('.')[-2]
                    filelist = glob.glob(self.dataset + '*' +
                                         self.file.split('.')[-1])

                datalist = np.zeros(np.shape(self.data))
                count = 0

                for file in filelist:
                    try:
                        new_data = np.loadtxt(self.file,
                                              delimiter=self.plot_delimiter,
                                              skiprows=self.begin_line - 1)

                        if np.shape(datalist)[1] == np.shape(new_data)[1] + 1:
                            datalist[:, 1:] = new_data
                            datalist[:, 0] = np.array(list(range(len(data))))
                        else:
                            datalist = datalist + new_data

                    except ValueError:
                        datalist = datalist + pd.read_csv(
                            file,
                            sep=self.plot_delimiter,
                            header=self.begin_line - 1,
                            skipfooter=self.footerskip,
                            engine='python',
                            index_col=False).to_numpy()
                    count += 1

                self.data = datalist / count

            # if is_number(self.start_x):  # selects part of data that occurs after the user-specified start x
            #     start = float(self.start_x)
            #     if start <= max(self.data[:, self.x_index]):
            #         self.data = self.data[np.where(self.data[:, self.x_index] >= start)]
            #     else:
            #         QMessageBox.about(self, "Error", "Start x is larger than max x for file.")
            #         self.start_x = "Default (x[0])"
            #     self.p.param('Plot options', 'Start x').setValue(self.start_x)

            self.plot_name = self.file.split('/')[-1].split('.')[0].replace(
                '_', ' ')

            if self.plot_stack:
                self.plot_name = ' '.join(self.plot_name.split(' ')[:-1])

                if self.plot_avg:
                    self.plot_name = self.plot_name + ' average'

            elif self.plot_avg:
                self.plot_title = ' '.join(
                    self.plot_name.split(' ')[:-1]) + ' average'

            else:
                self.plot_title = self.plot_name

            self.updatePlot()

        except AttributeError:
            QMessageBox.about(self, "Error",
                              "That file did not parse correctly.")

        except ValueError:
            QMessageBox.about(
                self, "Error",
                "This is not a comma-separated file and the correct "
                "delimiter was not specified.")

        except FileNotFoundError:
            QMessageBox.about(self, "Error", "No file chosen. Can't update.")

        self.p.param('Plot options', 'Delimiter').setValue(self.plot_delimiter)

    def getLines(self):
        """
        Finds lines where data lives. That info is used in numpy.loadtxt to
        skiprows and pandas.read_csv to skip header and footer.
        :return:
        """

        strippedlines = [ii.rstrip('\n').rstrip(',') for ii in self.lines]

        for line in strippedlines:
            items = [is_number(ii) for ii in line.split(self.plot_delimiter)]

            if not all(items):
                pass
            else:
                self.begin_line = strippedlines.index(line)

                if self.begin_line == 0:
                    self.data_types = False
                else:
                    self.data_type = self.begin_line - 1
                    self.data_types = [
                        ii.rstrip('\n').strip(' ') for ii in strippedlines[
                            self.data_type].split(self.plot_delimiter)
                    ]

                break

        if self.begin_line != -1:
            for line in strippedlines[::-1]:
                items = [
                    is_number(ii) for ii in line.split(self.plot_delimiter)
                ]

                if all(items):
                    self.end_line = strippedlines.index(line) + 1

                    break
                else:
                    self.end_line = strippedlines.index(strippedlines[-1])

            self.footerskip = len(strippedlines) - self.end_line

    def plotLine(self):
        """
        Recursive parametertree creation that depends on number of datatypes in file. Skips over the first data type
        -- assumed to be x axis in this software.
        :return:
        """

        if (self.file != self.current_file) or self.changedX:
            self.child_list = []
            self.plot_show = {}

            for name in self.data_types:
                name = name.rstrip('\n').strip(' ')

                if self.data_types.index(name) != self.x_index:
                    self.child_list.append({
                        'name':
                        name,
                        'type':
                        'bool',
                        'value':
                        self.p.param('Plot options', 'Select all').value(),
                        'tip':
                        f"Plot {name} if selected"
                    })
                    self.plot_show[name] = self.p.param(
                        'Plot options', 'Select all').value()

            # self.start_x = "Default (x[0])"  # this part will reset x axis if a new file is chosen. Not sure yet if
            # that's what I want
            # self.end_x = "Default (x[:])"
            #
            # self.p.param('Plot options', 'Start x').setValue(self.start_x)
            # self.p.param('Plot options', 'End x').setValue(self.end_x)

            self.plotlines = [{
                'name': 'Plot lines',
                'type': 'group',
                'children': self.child_list,
            }]

            self.l = Parameter.create(name='plotlines',
                                      type='group',
                                      children=self.plotlines)

            self.tff.setParameters(self.l, showTop=False)

            self.changedX = False

        for name in self.plot_show:
            self.plot_show[name] = self.l.param('Plot lines', name).value()

    def updatePlot(self):
        """
        Activated when user clicks Update Plot. (Re)draws lines depending on user selections.
        :return:
        """

        xset = False

        text_data_types = [ii.lower() for ii in self.data_types]
        found_idx = False

        for ii in range(len(text_data_types)):
            if self.x_string.strip(' ').lower() in text_data_types[ii]:
                self.x_index = ii
                found_idx = True

                break

        if not found_idx:
            self.x_index = 0

        self.x.param('x axis',
                     'x axis').setValue(self.data_types[self.x_index])

        self.plotLine()

        if is_number(self.start_x):
            if float(self.start_x) < np.max(self.data[:, self.x_index]):
                self.data = self.data[np.where(
                    self.data[:, self.x_index] >= float(self.start_x))]
            else:
                QMessageBox.about(self, "Error",
                                  "Start x is greater than max x.")
                self.p.param('Plot options',
                             'Start x').setValue("Default (x[0])")

        if self.real_axes:  # handles cases of user input axes types

            if "xlog" in self.each_axis and "ylog" in self.each_axis:
                for ii in range(0, len(self.data_types)):
                    if ii != self.x_index:
                        self.data[:, ii] = np.abs(self.data[:, ii])
                self.pl.setLogMode(True, True)
                xset = True
            elif "xlog" in self.each_axis:
                self.pl.setLogMode(True, False)
                xset = True
            elif "ylog" in self.each_axis:
                for ii in range(0, len(self.data_types)):
                    if ii != self.x_index:
                        if 0 in self.data[:, ii]:
                            self.plot_show[self.data_types[ii].rstrip(
                                '\n')] = False
                            self.l.param(
                                'Plot lines',
                                self.data_types[ii].rstrip('\n')).setValue(
                                    self.plot_show[self.data_types[ii].rstrip(
                                        '\n')])
                        else:
                            self.data[:, ii] = np.abs(self.data[:, ii])
                self.pl.setLogMode(False, True)
            else:
                self.pl.setLogMode(False, False)

            if xset:

                try:
                    start = float(self.start_x)
                except ValueError:
                    start = -1

                if start > 0:  # should pass string start times as well as negatives
                    try:
                        if all(self.data[:, self.x_index]) <= 0:
                            self.data[:, self.x_index] = np.abs(
                                self.data[:, self.x_index])
                        self.data = self.data[np.where(
                            self.data[:, self.x_index] >= start)]
                        self.start_x = self.data[np.where(
                            self.data[:, self.x_index] >= start)][0][
                                self.x_index]
                        self.p.param('Plot options', 'Start x').setValue(
                            np.round(self.start_x, 8))
                    except IndexError:
                        QMessageBox.about(
                            self, "Error",
                            "All x values are zero so this can't be put on a log plot."
                        )
                else:
                    try:
                        self.data_prev = self.data

                        if all(self.data[:, self.x_index]) <= 0:
                            self.data[:, self.x_index] = np.abs(
                                self.data[:, self.x_index])
                        self.data = self.data[np.where(
                            self.data[:, self.x_index] > 0)]
                        self.start_x = self.data[np.where(
                            self.data[:, self.x_index] > 0)][0][self.x_index]

                        if len(self.data[:, self.x_index]) != len(
                                self.data_prev[:, self.x_index]):
                            QMessageBox.about(
                                self, "Error",
                                "Can't have negatives or zeros for log axis.")
                            self.p.param('Plot options',
                                         'Start x').setValue(self.start_x)
                    except IndexError:
                        QMessageBox.about(
                            self, "Error",
                            "All x values are zero so this can't be put on a lot plot."
                        )

        if self.plot_normal:  # normalizes data to 1
            for ii in range(0, len(self.data_types)):
                if ii != self.x_index:
                    if np.max(np.absolute(self.data[:, ii])) == 0:
                        pass
                    else:
                        self.data[:, ii] = self.data[:, ii] / \
                            np.max(np.absolute(self.data[:, ii]))

            self.pl.setLabel('left', 'Magnitude (normalized)')
        else:
            self.pl.setLabel('left', 'Magnitude')

        # exception handling for start and end time cases

        if is_number(self.end_x) and not is_number(self.start_x):
            if float(self.end_x) > np.min(self.data[:, self.x_index]):
                self.data = self.data[np.where(
                    self.data[:, self.x_index] <= float(self.end_x))]
            else:
                QMessageBox.about(self, "Error",
                                  "End x is less than default Start x")
                self.p.param('Plot options',
                             'End x').setValue("Default (x[-1])")
        elif is_number(self.end_x) and is_number(self.start_x):
            if float(self.end_x) > float(self.start_x):
                self.data = self.data[np.where(
                    self.data[:, self.x_index] <= float(self.end_x))]
            else:
                QMessageBox.about(self, "Error", "End x is less than Start x")
                self.p.param('Plot options',
                             'End x').setValue("Default (x[-1])")

        if self.plot_stack:  # plots overtop of last and plots in new color
            for key in self.plot_show:
                if self.plot_show[key]:
                    ii = self.data_types.index(key)

                    if ii != self.x_index:
                        self.pl.plot(self.data[:, self.x_index],
                                     self.data[:, ii],
                                     pen=mkPen(ii + self.plot_count, width=3),
                                     name=self.data_types[ii].rstrip('\n') +
                                     "--" + self.plot_name)
                    self.plot_count += 1

        else:
            for key in self.plot_show:
                if self.plot_show[key]:
                    ii = self.data_types.index(key)

                    if ii != self.x_index:
                        self.pl.plot(self.data[:, self.x_index],
                                     self.data[:, ii],
                                     pen=mkPen(ii, width=3),
                                     name=self.data_types[ii].rstrip('\n'))
            self.pl.setTitle(self.plot_title)

        self.pl.enableAutoRange()

        self.pl.setLabel('bottom', self.data_types[self.x_index])

        self.pl.show()

        self.current_file = self.file

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Enter:
            self.makePlot()
        elif e.key(
        ) == 16777220:  # enter for Mac, will need to find out enter for windows
            self.makePlot()
        # else:
        #     QMessageBox.about(self, "Error", f"No command bound to {e.key()}.")

    def exportPNG(self):
        window = MainWindow(self)


"""
This allows a user to import a csv file from plot_gui app export and the user can live-update their matplotlib plot
in window for final export to png
"""

mplb.use('QT5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.file = "Filename"
        self.current_file = self.file
        self.title = "Title"
        self.yax = "Y"
        self.xax = "X"
        self.yticks = "Default"
        self.xticks = "Default"
        self.log = "x, y, or 'x, y'"
        self.labels = "Default"
        self.font = 14
        self.x_mode = self.y_mode = False
        self.bw = False

        self.xticks_entered = self.yticks_entered = self.xlabel_entered = \
            self.ylabel_entered = self.title_entered = self.user_labels = \
            False

        self.labels_entered = True

        mplb.rcParams.update({
            'figure.autolayout': True,
            'font.size': self.font
        })

        self.initUI()
        self.show()

    def initUI(self):
        self.plot = MplCanvas(self, width=5, height=4, dpi=100)

        self.default_cycle = mplb.rcParams['axes.prop_cycle']
        co_cyc = cycler(
            c=['#000000', '#737373', '#262626', '#999999', '#4d4d4d'])
        lin_cyc = cycler('ls', ['-', '--', '-.'])
        self.new_cycle = lin_cyc * co_cyc

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
                'name': 'B & W',
                'type': 'bool',
                'value': self.bw,
                'tip': 'Creates plot with grayscale on'
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
        self.params.param('Plot options',
                          'B & W').sigValueChanged.connect(self.setBW)

        # self.toolbar = NavigationToolbar(sc, self)

        layout = QHBoxLayout()
        layout.addWidget(self.tree, 2)
        layout.addWidget(self.plot, 3)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # self.showMaximized()

    def setBW(self):
        self.bw = self.params.param('Plot options', 'B & W').value()

        if self.bw:
            mplb.rcParams.update({'axes.prop_cycle': self.new_cycle})
        else:
            mplb.rcParams.update({'axes.prop_cycle': self.default_cycle})

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
        try:
            try:
                self.data = np.loadtxt(self.file,
                                       delimiter=self.plot_delimiter,
                                       skiprows=self.begin_line - 1)
            except ValueError:
                self.data = pd.read_csv(self.file,
                                        engine='python',
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
            self.current_file = self.file
        except FileNotFoundError:
            if self.current_file != 'Filename':
                self.file = self.current_file
                try:
                    self.data = np.loadtxt(self.file,
                                           delimiter=self.plot_delimiter,
                                           skiprows=self.begin_line - 1)
                except ValueError:
                    self.data = pd.read_csv(self.file,
                                            engine='python',
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
                        self.plot.axes.get_yticklabels().set_fontsize(
                            self.font)
                    except AttributeError:
                        pass

                if self.xticks_entered:
                    self.plot.axes.set_xticks(self.xticks)
                    try:
                        self.plot.axes.get_xticklabels().set_fontsize(
                            self.font)
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
                        self.plot.axes.plot(self.data[:, 0],
                                            self.data[:, ii + 1])

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

                self.params.param('Plot options',
                                  'File:').setValue(self.file.split('/')[-1])
            else:
                pass

    def exportPNG(self):

        self.plot.fig.savefig('.'.join(self.file.split('.')[:-1]) + '.png')


def main():
    app = QApplication(sys.argv)
    window = PlotGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
else:
    main()
