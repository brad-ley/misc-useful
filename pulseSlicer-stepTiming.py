import ast
import os
import re
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from matplotlib import rc
from scipy.signal import find_peaks

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


def main(folder, signal, background, title=''):
    folder = P(folder)
    try:
        real = int(signal)
        background = int(background)
    except TypeError:
        raise Exception('Signal and background need to be integers (MXX)')

    sigfs = [ii for ii in folder.iterdir(
    ) if (ii.stem.startswith(f'M{signal:02d}') or ii.stem.startswith(f'M{background:02d}')) and ii.name.endswith('.dat') and not 'blocked' in ii.name.lower()]
    sigfs.sort()
    backgroundfs = [ii for ii in folder.iterdir(
    ) if (ii.stem.startswith(f'M{signal:02d}') or ii.stem.startswith(f'M{background:02d}')) and ii.name.endswith('.dat') and 'blocked' in ii.name.lower()]
    backgroundfs.sort()
    dt = 1e-9
    fig, ax = plt.subplots(figsize=(11, 7.5))
    scale = 0
    data_dict = {}

    vals = zip(sigfs, backgroundfs)

    for i, f in enumerate(vals):
        data = pd.read_csv(f[0], delimiter=', ', skiprows=2, engine='python')
        bgdata = pd.read_csv(f[1], delimiter=', ', skiprows=2, engine='python')
        y = data['Y'].to_numpy()
        x = np.arange(0, len(y)) * dt
        distance = np.where(x > 130e-9)[0][0]
        ypeaks, _ = find_peaks(y[x < 45e-6], distance=distance)

        bgy = bgdata['Y'].to_numpy()
        bgypeaks, _ = find_peaks(bgy[x < 45e-6], distance=distance)
        bgy = bgy[bgypeaks]
        bgy = np.interp(x[ypeaks], x[bgypeaks], bgy)

        if np.max(y[ypeaks] > scale):
            scale = np.max(y[ypeaks])

        data_dict[f[0].stem] = np.column_stack((x[ypeaks], y[ypeaks], bgy))

    keys = sorted(data_dict.keys())

    for i, key in enumerate(keys):
        if i == 0:
            label = 'Laser off'
        else:
            label = f'{135 + (i-1)*5} mA'
        ax.plot(data_dict[key][:, 0] * 1e6,
                data_dict[key][:, 1] - data_dict[key][:, 2], label=label, lw=2)

    ax.legend()
    ax.set_xlim(left=-10e-6)
    ax.set_ylabel('Signal (mV)')
    ax.set_xlabel(r'Time ($\mu$s)')
    if title:
        ax.set_title(title)
        fig.savefig(sigfs[0].parent.joinpath(
            title + '_figure.png'), dpi=400)
        P(sigfs[0].parent.joinpath(
            title + '_combinedPeaks.dat'
            )).write_text(repr(data_dict))
    else:
        ax.set_title(sigfs[0].stem.replace('_', ' ').title())
        fig.savefig(sigfs[0].parent.joinpath(
            sigfs[0].stem + '_figure.png'), dpi=400)
        P(sigfs[0].parent.joinpath(
            sigfs[0].stem + '_combinedPeaks.dat'
            )).write_text(repr(data_dict))


if __name__ == "__main__":
    folder = '/Volumes/GoogleDrive/My Drive/Research/Data/2023/1/19/20230119_pulseSlicerOnSwitch/'
    signal = 1
    background = 2
    title = 'On switch, final wafer and source angle, comparison sensor angle (bc)'
    main(folder, signal, background, title=title)
    plt.show()
