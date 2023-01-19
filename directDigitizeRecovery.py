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


def main(folder):
    files = [ii for ii in P(folder).iterdir() if ii.name.endswith('.dat')]
    for i, f in enumerate(files):
        header, data = read(f)
        if 'offres' in f.stem.lower():
            off = data[:, 1] + 1j * data[:, 2]
        else:
            on = data[:, 1] + 1j * data[:, 2]
    diff = np.abs(on) - np.abs(off)    
    fig, ax = plt.subplots()
    ax.plot(data[:, 0]*1e6, diff, label='Abs diff')
    ax.legend()
    ax.set_ylabel('$\Delta_{sig}$ (V)')
    ax.set_xlabel('Time ($\mu$s)')
    fig.savefig(P(folder).joinpath('fig.png'), dpi=400)


if __name__ == "__main__":
    folder = '/Volumes/GoogleDrive/My Drive/Research/Data/2023/1/11/RSH with RM/CoPolar minimum time traces'
    main(folder)
    plt.show()
