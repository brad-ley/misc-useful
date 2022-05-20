import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib import rc

from readDataFile import read

plt.style.use('science')
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'


def plot(folder):
    if P(folder).is_file():
        folder = P(folder).parent
    fs = [ii for ii in P(folder).iterdir() if ii.name.startswith(
        'echo') or ii.name.startswith('fid')]
    fig, ax = plt.subplots(2, sharex=True)

    for i, f in enumerate(fs):
        string = f.read_text()
        data_dict = ast.literal_eval(string)
        sig = np.array(data_dict['Ch1 All']) + 1j * \
            np.array(data_dict['Ch2 All'])
        t = np.array(data_dict['Time']) * 1e6
        r = np.logical_and(t > 0.4, t < 0.9)
        sig = sig[r]
        t = t[r]
        t -= t[0]
        ax[i].plot(t, np.abs(sig))
        ax[i].set_ylim(top=np.max(np.abs(sig))*1.25)
        ax[i].set_yticks([])

        x1 = (0.145,0.175)
        x2 = (0.22, 0.25)
        fid = (0.30, 0.38)
        echo = (0.315, 0.335)
        ax[i].text(x1[0], 1.1*np.max(np.abs(sig)), 'P1',
                   horizontalalignment='left', verticalalignment='center')
        ax[i].axvspan(*x1, color='gray', alpha=0.5)
        ax[i].text(x2[0], 1.1*np.max(np.abs(sig)), 'P2',
                   horizontalalignment='left', verticalalignment='center')
        ax[i].axvspan(*x2, color='gray', alpha=0.5)
        if ax[i] == ax[0]:
            ax[i].text(fid[0], 1.1*np.max(np.abs(sig)), 'FID',
                       horizontalalignment='left', verticalalignment='center')
            ax[i].axvspan(*fid, color='gray', alpha=0.5)
        elif ax[i] == ax[1]:
            ax[i].text(echo[0], 1.1*np.max(np.abs(sig)), 'Echo?',
                       horizontalalignment='left', verticalalignment='center')
            ax[i].axvspan(*echo, color='gray', alpha=0.5)

    ax[1].set_xlabel('Time ($\mu$s)')

    fig.supylabel('Induction mode signal (arb. u)')
    plt.tight_layout()
    plt.savefig(P(folder).joinpath('fig.png'), dpi=300)


if __name__ == "__main__":
    FOLDER = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/06/06/4T'
    plot(FOLDER)
    plt.show()
