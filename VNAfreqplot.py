import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from readDataFile import read

import PIL
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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


def main(filename, ax):
    data = pd.read_csv(filename, header=6, skipfooter=2, engine='python')
    ax.plot(data['Freq(Hz)']*1e-9, data[data.columns[1]])

    return ax

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(8,6))
    filename = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/4/4/VNA test/newWafer-FSweep.csv'
    ax = main(filename, ax)
    plt.show()
