"""
This opens a gui and lets the user update with their chosen .dat
"""
# !/usr/bin/python

# need to make sure when creating app that I use python3 because that is in usr/local/bin, which is where my local
# python dist and py2app are located

import glob
import sys
import platform
# import csv_fig  # error appears when using this submodule

import numpy as np
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pyqtgraph import *
from pyqtgraph.parametertree import *

# import plt_fig
"""
TODO
[ ] Add comments
[ ] Add button to export plot with Matplotlib and save to .png -- weird bug in export pyqtgraph for some reason
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
        # self.plot_name = False
        self.data_types = ['null']
        self.plot_count = 0
        self.plot_delimiter = ','
        self.start_x = "Default (x[0])"
        self.end_x = "Default (x[-1])"
        self.plot_axes = 'xlin, ylin'
        # self.possible_axis = [
        #     "xlog, ylog", "xlin, ylin", "xlog, ylin", "xlin, ylog"
        # ]
        self.possible_axis = {"xlog", "ylog", "xlin", "ylin"}
        self.real_axes = False
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
                    'tip': "xlin, ylin, xlog, ylog; default x,y lin if unspecified"
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
            'children': [
                {
                    'name': 'Update plot',
                    'type': 'action'
                },
                {
                    'name': 'Clear all',
                    'type': 'action'
                },
                {
                    'name': 'Clear last',
                    'type': 'action'
                },
                {
                    'name': 'Choose file',
                    'type': 'action'
                },
                {
                    'name': 'File:',
                    'type': 'str',
                    'value': self.file
                },
                # {
                #     'name': 'Create png',
                #     'type': 'action'
                # }
            ]
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

        self.p = Parameter.create(name='params',
                                  type='group',
                                  children=self.params)
        self.f = Parameter.create(name='filestuff',
                                  type='group',
                                  children=self.filestuff)
        self.l = Parameter.create(name='plotlines',
                                  type='group',
                                  children=self.plotlines)

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

        Layout.addWidget(self.tf, 0, 1)  # deleted some shit here
        Layout.addWidget(self.t, 0, 2)
        Layout.addWidget(self.tff, 0, 3)
        Layout.addWidget(self.win, 1, 0, 1, 4)  # position, then size (want full bottom row)

        self.f.param('File',
                     'Choose file').sigActivated.connect(self.chooseFile)
        self.f.param('File', 'Update plot').sigActivated.connect(self.makePlot)
        self.f.param('File', 'Clear all').sigActivated.connect(self.clearPlot)
        self.f.param('File', 'Clear last').sigActivated.connect(self.clearLast)
        # self.f.param('File', 'Create png').sigActivated.connect(self.makePNG)

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

    def chooseFile(self):
        """
        Opens dialog and returns filename for plotting. If filename isn't found, returns file for a file on bprice
        computer... not super helpful for distribution and wi
        :return:
        """
        self.file = QFileDialog.getOpenFileName(
            self, "Plot file", "", "Data Files (*.dat);;CSV (*.csv);;"
                                   "Text Files (*.txt);;Python Files (*.py)")[0]
        try:
            fileopen = open(self.file, 'r')
            self.prev_file = self.file

            self.lines = fileopen.readlines()
            fileopen.close()
        except FileNotFoundError:
            # try:
            #     self.file = self.prev_file
            #
            #     if self.file == "Filename":  # this part will only work on bprice machine
            #     # - might be good to generalize
            #         if platform.system() == 'Darwin':
            #             self.file = r"/Users/Brad/Documents/Research/2020/Data/20200309" \
            #                         r"/M01_174_108_mono_activated_410nm_Scan000.dat"
            #         elif platform.system() == 'Windows':
            #             self.file = r"C:\Users\bdprice\Documents\Data\UV Vis\PR\20200309" \
            #                         r"\E108Q 174 Monomer\M01_174_108_mono_activated_410nm_Scan000.dat"
            #     fileopen = open(self.file, 'r')
            #
            #     self.lines = fileopen.readlines()
            #     fileopen.close()
            # except FileNotFoundError:
            #     self.file = r"File not found (or maybe not selected)"
            self.file = r"No file selected"  # simplified code here for distribution purposes

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

    # def makePNG(self):
    #     try:
    #         csv_fig.main()
    #     except:
    #         pass

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

    def plotStack(self):
        """
        Plots new file over old file to compare on top
        :return:
        """
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

    def startX(self):
        """
        Allows user to select plotting start time
        :return:
        """
        if is_number(self.p.param('Plot options', 'Start x').value()):
            self.start_x = self.p.param('Plot options',
                                        'Start x').value()
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
                    self.end_x = self.p.param('Plot options',
                                              'End x').value()
                else:
                    QMessageBox.about(
                        self, "Error",
                        "End time before start time.")
                    self.end_x = "Default (x[-1])"
            else:
                self.end_x = float(self.p.param('Plot options', 'End x').value())
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
        axes = [ii.strip(' ') for ii in self.p.param('Plot options',
                                                     'Axis scale').value().split(',')]

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

            if self.plot_multiple:
                # this will create additional plots in same window instead of re-plotting
                self.pl = self.win.addPlot()
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

            self.begin_idx = self.begin_line = self.data_type = self.footerskip = -1  # set to determine if a file
            # doesn't actually have any plottable data

            self.getLines()

            if self.begin_line == -1:
                QMessageBox.about(
                    self, "Error",
                    "Delimiter not in file. Attempting to use csv.")
                self.plot_delimiter = ','

                self.getLines()

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
                    datalist = datalist + pd.read_csv(
                        file,
                        sep=self.plot_delimiter,
                        header=self.begin_line - 1,
                        skipfooter=self.footerskip,
                        engine='python',
                        index_col=False).to_numpy()
                    count += 1

                self.data = datalist / count

            if is_number(self.start_x):
                start = float(self.start_x)
                if start <= max(self.data[:, 0]):
                    self.data = self.data[np.where(self.data[:, 0] >= start)]
                else:
                    QMessageBox.about(self, "Error", "Start x is larger than max x for file.")
                    self.start_x = "Default (x[0])"
                self.p.param('Plot options', 'Start x').setValue(self.start_x)

            self.plot_name = self.file.split('/')[-1].split('.')[0].replace(
                '_', ' ')

            if self.plot_stack:
                self.plot_name = ' '.join(self.plot_name.split(' ')[:-1])

                if self.plot_avg:
                    self.plot_name = ' '.join(
                        self.plot_name.split(' ')[:-1]) + 'average'

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

        self.plotLine()

    def plotLine(self):

        if self.file != self.current_file:
            self.child_list = []
            self.plot_show = {}

            for name in self.data_types:
                name = name.rstrip('\n').strip(' ')
                if self.data_types.index(name) != 0:
                    self.child_list.append({'name': name, 'type': 'bool', 'value': True, 'tip': f"Plot {name} if "
                                                                                                "selected"})
                    self.plot_show[name] = True

            self.plotlines = [{
                'name': 'Plot lines',
                'type': 'group',
                'children': self.child_list,
            }]

            self.l = Parameter.create(name='plotlines',
                                      type='group',
                                      children=self.plotlines)

            self.tff.setParameters(self.l, showTop=False)

        for name in self.plot_show:
            self.plot_show[name] = self.l.param('Plot lines', name).value()

            # self.l.param('Plot lines',
            #              name).sigStateChanged.connect(lambda: self.plotShow(name))

    def updatePlot(self):

        xset = False

        if self.real_axes:

            if "xlog" in self.each_axis and "ylog" in self.each_axis:
                for ii in range(1, len(self.data_types)):
                    self.data[:, ii] = np.abs(self.data[:, ii])
                self.pl.setLogMode(True, True)
                xset = True
            elif "xlog" in self.each_axis:
                self.pl.setLogMode(True, False)
                xset = True
            elif "ylog" in self.each_axis:
                for ii in range(1, len(self.data_types)):
                    self.data[:, ii] = np.abs(self.data[:, ii])
                self.pl.setLogMode(False, True)
            else:
                self.pl.setLogMode(False, False)

            if xset:

                try:
                    start = float(self.start_x)
                except ValueError:
                    start = -1

                if start > 0:  # should catch string start times as well as negatives
                    self.data = self.data[np.where(self.data[:, 0] > start)]
                    self.start_x = self.data[np.where(
                        self.data[:, 0] > start)][0][0]
                    self.p.param('Plot options', 'Start x').setValue(
                        np.round(self.start_x, 8))
                else:
                    self.data = self.data[np.where(self.data[:, 0] > 0)]
                    self.start_x = self.data[np.where(
                        self.data[:, 0] > 0)][0][0]
                    QMessageBox.about(self, "Error", "Can't have negatives or zeros for log axis.")
                    self.p.param('Plot options', 'Start x').setValue(
                        "Default (x[0])")


        if self.plot_normal:
            for ii in range(1, len(self.data_types)):
                if np.max(np.absolute(self.data[:, ii])) == 0:
                    pass
                else:
                    self.data[:, ii] = self.data[:, ii] / \
                                       np.max(np.absolute(self.data[:, ii]))

            self.pl.setLabel('left', 'Magnitude (normalized)')
        else:
            self.pl.setLabel('left', 'Magnitude')

        if is_number(self.end_x) and not is_number(self.start_x):
            if float(self.end_x) > np.min(self.data[:, 0]):
                self.data = self.data[np.where(self.data[:, 0] <= float(self.end_x))]
            else:
                QMessageBox.about(self, "Error", "End x is less than default Start x")
                self.p.param('Plot options', 'End x').setValue("Default (x[-1])")
        elif is_number(self.end_x) and is_number(self.start_x):
            if float(self.end_x) > float(self.start_x):
                self.data = self.data[np.where(self.data[:, 0] <= float(self.end_x))]
            else:
                QMessageBox.about(self, "Error", "End x is less than Start x")
                self.p.param('Plot options', 'End x').setValue("Default (x[-1])")

        if self.plot_stack:
            for key in self.plot_show:
                if self.plot_show[key]:
                    ii = self.data_types.index(key)

                    if ii != 0:
                        self.pl.plot(self.data[:, 0],
                                     self.data[:, ii],
                                     pen=ii + self.plot_count,
                                     name=self.data_types[ii].rstrip('\n') + "--" + self.plot_name)
                    self.plot_count += 1

        else:
            for key in self.plot_show:
                if self.plot_show[key]:
                    ii = self.data_types.index(key)

                    if ii != 0:
                        self.pl.plot(self.data[:, 0],
                                     self.data[:, ii],
                                     pen=ii,
                                     name=self.data_types[ii].rstrip('\n'))
            self.pl.setTitle(self.plot_title)

        self.pl.enableAutoRange()

        self.pl.setLabel('bottom', self.data_types[0])

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
