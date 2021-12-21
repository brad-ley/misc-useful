import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumtrapz

from readDataFile import read
from makeAbsDisp import make


def overlay(targ, low=-1, high=-1):
    """overlay.
    :param targ: directory with 'absorption' files
    :param low: low field for plotting
    :param high: high field for plotting
    """
    if P(targ).is_file():
        targ = str(P(targ).parent)
    fs = [ii for ii in P(targ).iterdir() if ii.name.startswith(
        'absorption') and ii.name.endswith('_exp.txt')]
        # 'dispersion') and ii.name.endswith('_exp.txt')]
    fig, ax = plt.subplots()
    figtrapz, axtrapz = plt.subplots()
    
    for i, f in enumerate(sorted(fs)):
        h, d = read(str(f))
        d[:, 1] = d[:, 1] - np.average(d[:, 1]) # remove baseline
        if low == -1:
            if 'plotlow' in locals():
                if d[0, 0] < plotlow:
                    plotlow = d[0, 0]
            else:
                plotlow = d[0, 0]
        else:
            plotlow = low
        if high == -1:
            if 'plothigh' in locals():
                if d[-1, 0] > plothigh:
                    plothigh = d[-1, 0]
            else:
                plothigh = d[-1, 0]
        else:
            plothigh = high
        
        try:
            scale = np.trapz(cumtrapz(d[np.where(plotlow < d[:, 0])[
                             0][0]:np.where(plothigh < d[:, 0])[0][0], 1]))
            ax.plot(d[:, 0], d[:, 1] / scale, label=f"{f.name.split('_')[1]}")
            axtrapz.plot(d[1:, 0], cumtrapz(d[:, 1]) / scale, label=f"{f.name.split('_')[1]}")
        except (IndexError, UnboundLocalError):
            ax.plot(d[:, 0], d[:, 1] / np.max(d[:, 1]), label=f"{f.name.split('_')[1]}")
            axtrapz.plot(d[1:, 0], cumtrapz(d[:, 1]) / np.max(cumtrapz(d[:, 1])), label=f"{f.name.split('_')[1]}")

    try:
        for a in [ax, axtrapz]:
            a.set_xlim([plotlow, plothigh])
            a.set_yticks([])
            a.set_ylabel('Signal (arb. u)')
            a.set_xlabel('Field (T)')
            a.spines['right'].set_visible(False)
            a.spines['top'].set_visible(False)
            a.legend()

        plt.tight_layout()
        fig.savefig(P(targ).joinpath('figure_comp.png'), dpi=300)

        plt.show()
    except UnboundLocalError:
        print("Need to create absorption files with makeAbsDisp.py first!")


def main():
    make(targ, keyw='%', center=True, rollmid=50)
    overlay(targ)


if __name__ == "__main__":
    targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/12/7/combined'
    main()
