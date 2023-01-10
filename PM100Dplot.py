import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from readDataFile import read

import PIL
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import rc
plt.style.use(['science'])
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['xtick.major.size'] = 5
plt.rcParams['xtick.major.width'] = 1
plt.rcParams['xtick.minor.size'] = 2
plt.rcParams['xtick.minor.width'] = 1
plt.rcParams['ytick.major.size'] = 5
plt.rcParams['ytick.major.width'] = 1
plt.rcParams['ytick.minor.size'] = 2
plt.rcParams['ytick.minor.width'] = 1
plt.rcParams['lines.linewidth'] = 2


def main(filename):
    header, data = read(filename, delimiter='\t')
    fig, ax = plt.subplots()    
    ax.plot(data[:, 1]*1e-3, data[:, 0]*1e3)
    ax.set_ylabel('mJ')
    ax.set_xlabel('Time (s)')
    ax.text(0.1, 0.6, '$I_{d}=135$ mA', transform=ax.transAxes)
    ax.text(0.55, 0.25, '$I_{d}=140$ mA', transform=ax.transAxes)
    fig.savefig(P(filename).parent.joinpath(P(filename).stem + '_fig.png'), dpi=400)


if __name__ == "__main__":
    filename = '/Volumes/GoogleDrive/My Drive/Research/Data/2023/1/10/DATA01.CSV'
    main(filename)
    plt.show()
