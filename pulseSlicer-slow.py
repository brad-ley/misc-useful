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


def main(folder):
    files = [ii for ii in P(folder).iterdir() if ii.name.endswith('.dat')]

    fig, ax = plt.subplots(figsize=(8, 6), layout='constrained')

    files.sort(key=lambda x: int(''.join(x.stem.replace(
        '-', ' ').split('_')[:-1]).split(' ')[-1].replace('ns', '')))
    files.reverse()

    for i, f in enumerate(files):
        lines = f.read_text()

        for index, line in enumerate(lines.split('\n')):
            if 'delta t,' in line:
                t_step = float(line.replace('delta t,', '').strip())

                break
        data = pd.read_csv(f, header=4)
        y = data[data.columns[-1]]
        time = np.linspace(0, len(y) * t_step, len(y))

        time -= time[np.where(np.abs(np.abs(y) > 0.5*np.max(np.abs(y))))[0][0]]
        time *= 1e6

        label = ''.join(f.stem.replace('-', ' ').split('_')[:-1])
        # ax.plot(time, y/np.max(y)+i, label=label)
        ax.plot(time, y, label=label)
    ax.set_xlim([-0.1, 0.5])
    ax.set_ylim([-5e-4, 1.25e-3])
    ax.set_xlabel('Time ($\mu$s)')
    ax.set_ylabel('Amplitude (V)')
    ax.legend()
    fig.savefig(P(folder).joinpath('figure.png'), dpi=400)


if __name__ == "__main__":
    folder = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/4/25/positive/both-on'
    # folder = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/4/25/negative/'
    main(folder)
    plt.show()
