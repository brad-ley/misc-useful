from pathlib import Path as P

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit as cf
from scipy.signal import savgol_filter

from readDataFile import read


def exp(x, a, b, c):
   return a + b*np.exp(-x/c) 


def process(filename, subtract_bkg=False, savgol=False):
    """process.

    :param filename: input .dat filename
    :param subtract_bkg: bool to subtract background
    :param savgol: bool to apply Savitzky-Golay filtering
    """
    files = [P(filename)]
    fig, ax = plt.subplots()
    files.sort()

    for i, f in enumerate(files):
        header, data = read(f)

        data_array = np.array(data)

        data_dict = {
            'param': data_array[:, 0],
            'echo': np.abs(data_array[:, 1] + 1j * data_array[:, 2]),
        }

        x = data_dict['param']
        add = ''

        dat = data_dict['echo']

        if savgol:
            dat = savgol_filter(dat, 2 * (len(x) // 20) + 1, 3)
            add += 'savgol_'

        c = 1
        xx = np.min(x)
        x -= xx
        popt, pcov = cf(exp, x, dat, p0=[np.max(dat), np.max(dat), 2e-3])
        smoothx = np.linspace(np.min(x), np.max(x), 1000)

        # ax.plot((x+xx)*1e3, dat / np.max(dat) + i * c, lw=2, label='raw')
        ax.plot((x+xx)*1e3, dat, lw=2, label='raw')
        ax.plot((x+xx)*1e3, exp(x,*popt) + i * c, c='k', ls='--', lw=2, label=fr'fit: $\tau=${popt[-1]:.1e} s')

    # savename = P(filename).parent.joinpath(add + 'Saturation.png')
    savename = P(filename).parent.joinpath(add + 'Recovery.png')

    ax.legend()
    ax.set_ylabel('Echo intensity (arb. u)')
    # ax.set_yticks([])
    # ax.set_xlabel('P1 length (ms)')
    ax.set_xlabel('Delay length (ms)')
    # ax.set_title(r'Low power saturation')

    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)

    plt.savefig(savename, dpi=300)


if __name__ == "__main__":
    f = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/8/22/M17_invRecovery_000.dat'
    process(f)
    plt.show()
