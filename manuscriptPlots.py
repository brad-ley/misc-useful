from pathlib import Path as P
from pathlib import PurePath as PP

import PIL
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('science')

"""
filename need to be full path to file:
-- on Mac you can get this by right-clicking and then
holding option and selecting 'Copy as Pathname'
-- on Windows you can get this by holding shift before rightclicking and then
selecting 'Copy as path'
"""
FILENAME = 'C:/full/path/to/file/goes/here.dat' 
FILENAME = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/25/sample 1 (unenriched)/absorption_LightOn_sample2022125107_exp.txt' 
"""
setting axis labels, etc
"""
# legend_names = ['line 1', 'line 2'] # add as many legend names as you want to be plotted on same x axis
legend_names = ['absorption'] # add as many legend names as you want to be plotted on same x axis
x_Label = 'sample x label' # x axis label
y_Label = 'sample y label' # y axis label
x_tickLabels = True # set to false to remove x axis tick labels
x_ticks = True # make False to get rid of x axis tick labels (good for arbitrary unit data)
y_tickLabels = True # set to false to remove y axis tick labels
y_ticks = True # make False to get rid of y axis tick labels (good for arbitrary unit data)
savename = 'sample save name' # how to name file that will be saved

def main(f):
    fig, ax = plt.subplots()
    try:
        data = np.loadtxt(f)
    except:
        try:
            data = np.loadtxt(f, delimiter=', ')
        except:
            data = np.loadtxt(f, delimiter='\t')
    for i, n in enumerate(legend_names):
        plt.plot(data[:, 0], data[:, 1 + i], label=n)
    plt.xlabel(x_Label)
    plt.ylabel(y_Label)
    if not x_ticks:
        ax.set_xticks([])
    if not x_tickLabels:
        ax.set_xticklabels([])
    if not y_ticks:
        ax.set_yticks([])
    if not y_tickLabels:
        ax.set_yticklabels([])

    plt.legend()
    plt.savefig(P(f).parent.joinpath(f"{savename}.tif"),dpi=300)


if __name__ == "__main__":
    main(FILENAME)
    plt.show()
