import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from matplotlib import rc

from readDataFile import read

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
    data = pd.read_csv(filename, header=8, skipfooter=2, engine='python')
    data.columns = ['time', 'mag', 'phase']
    if 'Si2inch' in filename.stem:
        raw = data.loc[:, 'mag'] + 1j * data.loc[:, 'phase']
        data['mag'] = np.abs(raw)
        data['phase'] = np.angle(raw)
    data['time'] *= 1e6
    trig = np.where(data['mag'] > np.max(data['mag']) * 0.5)[0][0]
    data['time'] -= data['time'][trig] - 1
    # data['mag'] /= data['mag'][trig]
    ax.plot(data['time'], data['mag'], label=filename.stem.replace('-',' '))
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(layout='constrained', figsize=(8,6))
    folder = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/4/12/20230412/front surface expand' 
    for _, f in enumerate(sorted([ii for ii in P(folder).iterdir() if ii.name.endswith('.csv')])):
        ax = main(f, ax)
    ax.set_xlabel('Time ($\mu$s)')
    ax.set_ylabel('Reflectivity')
    ax.set_xlim([140, 210])
    # ax.set_xlim([-10, 60])
    ax.legend()
    fig.savefig(P(folder).joinpath('plot_relaxations.png'), dpi=500)
    plt.show()
