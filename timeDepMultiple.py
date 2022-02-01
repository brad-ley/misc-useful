import ast
import os
import PIL
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL

from scipy.optimize import curve_fit
from readDataFile import read

plt.style.use(['science'])
ontime = 5
colors = [['black', 'red'], ['gray', 'blue']]
styles = [['-', '--'], ['-', ':']]
delimiter = ', '
skiprows = 0


def exp(x, c, A, tau):
    return c + A*np.exp(-x / tau)


def show(folder):
    if P(folder).is_file():
        folder = P(folder).parent
    files = [ii for ii in P(folder).iterdir() if ii.suffix == '.txt']
    fig, ax = plt.subplots()

    for i, f in enumerate(files):
        data = np.loadtxt(f, delimiter=delimiter, skiprows=skiprows)
        t = np.array(data[:, 0])
        dat = np.array(data[:, 1])
        ax.plot(t, dat / dat[0] - 1, label=f.stem,
                lw=1.25, color=colors[i][0], linestyle=styles[i][0])
        popt, pcov = curve_fit(exp, t[t > ontime], dat[t > ontime])
        perr = np.sqrt(np.diag(pcov))
        sd2 = 2*perr[2]
        ax.plot(t[t > ontime], exp(t[t > ontime],*popt) / dat[0] - 1,
                label=r"$\tau=$" + f"{popt[2]:.1f}$\pm${sd2:.1f} s", lw=1.25, color=colors[i][1], linestyle=styles[i][1])

    ax.set_ylabel('Signal (arb. u)')
    ax.set_xlabel('Time (s)')
    plt.legend()
    plt.savefig(P(folder).joinpath('compared.tif'),dpi=300)
    plt.savefig(P(folder).joinpath('compared.png'),dpi=300)


if __name__ == "__main__":
    folder = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/compare single double'
    show(folder)
    plt.show()
