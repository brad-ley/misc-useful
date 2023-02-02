import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from readDataFile import read

import PIL
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumtrapz
from makeAbsDisp import make

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
    header, data = read(P(filename))
    fig, ax = plt.subplots()
    x = data[:, 1] * 1e4
    y = data[:, 4]
    ax.plot(x, y, label='Abs')
    pk2pk = np.abs(x[np.argmin(y)] - x[np.argmax(y)])
    ax.plot(x[:-1], cumtrapz(-y), label='Int')
    top = np.where(y > 0.5*np.max(y))
    fwhm = np.abs(x[top[0][0]] - x[top[0][-1]])
    ax.legend()
    print(f'{"pk2pk:":<6}{pk2pk:>4.2f}\n{"fwhm:":<6}{fwhm:>4.2f}\n')

if __name__ == "__main__":
    filename = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/1/31/M01_1mA_u_rephased.dat' 
    main(filename)
    plt.show()
