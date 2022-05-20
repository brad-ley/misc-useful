import ast
import os
import PIL
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

from readDataFile import read

# plt.rcParams.update({'font.size': 20})
plt.style.use('science')
# plt.rcParams.update({'font.family':'sans-serif'})
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'


def main(targ):
    fs = [ii for ii in P(targ).iterdir() if 'usweep' in ii.stem and ii.stem.endswith('rephased')]

    fig, ax = plt.subplots()
    d = 4
    lw = 1.25

    for f in fs:
        header, data = read(f)
        if 'Off' in f.stem:
            ax.plot(data[:, 1] + 8.62, -data[:, d], label=r"Laser off", c='k', linewidth=lw)

        if 'On' in f.stem:
            pc = '#00A7CA'
            sty = '--'
            ax.plot(data[:, 1] + 8.62, data[:, d],
                    label=r"Laser on", c=pc, linestyle=sty, linewidth=lw)

    ax.set_yticklabels([])
    ax.set_ylabel('cwEPR signal (arb. u)')
    ax.set_xlabel('Field (T)')
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    ax.text(0.05, 0.11, '$T=294$ K',
            horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(P(targ).joinpath('dark-lit.png'), dpi=300)
    plt.savefig(P(targ).joinpath('dark-lit.tif'), dpi=300)


if __name__ == "__main__":
    FOLDER = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/2/7'
    main(FOLDER)
    plt.show()
