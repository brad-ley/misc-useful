import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumtrapz

from readDataFile import read

targ = '/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/08/30/LR/temp comp'


def overlay(targ):
    fs = [ii for ii in P(targ).iterdir() if ii.name.startswith(
        'absorption') and ii.name.endswith('_exp.txt')]
    fig, ax = plt.subplots()
    plotlow = 7.5
    plothigh = 9.5

    for i, f in enumerate(fs):
        h, d = read(str(f))

        d[:, 1] = d[:, 1] - np.average(d[:, 1])
        scale = np.trapz(cumtrapz(d[np.where(plotlow < d[:, 0])[
                         0][0]:np.where(plothigh < d[:, 0])[0][0], 1]))
        ax.plot(d[:, 0], d[:, 1] / scale, label=f"{f.name.split('_')[1]}")

    ax.set_xlim([plotlow, plothigh])
    ax.set_yticks([])
    ax.set_ylabel('Signal (arb. u)')
    ax.set_xlabel('Field (T)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.legend()

    plt.tight_layout()
    plt.savefig(P(targ).joinpath('figure_comp.png'), dpi=300)

    plt.show()


def main():
    overlay(targ)


if __name__ == "__main__":
    main()
