import ast
import os
import re
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize, signal

targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/06/11/new coil calib/selected amp'


def calibrate(targ, fit_Hpp_0=True):
    """calibrate.

    :param targ:
    """
    # choice = 'absorption'
    choice = 'dispersion'
    try:
        regex = re.compile(r"_(\d+\.*\d*)mA_")
        # files = [ii for ii in P(targ).iterdir() if ii.name.startswith('dispersion') and ii.name.endswith('exp.txt')]
        # for f in files:
        #     print(f.name)
        #     print(regex.findall(f.name))
        files = sorted([
            ii for ii in P(targ).iterdir()
            if ii.name.startswith(choice) and ii.name.endswith('exp.txt')
        ],
                       key=lambda x: float(regex.findall(x.name)[0]))
    except IndexError:
        regex = re.compile(r"_mA(\d+\.*\d*)_")
        files = sorted([
            ii for ii in P(targ).iterdir()
            if ii.name.startswith(choice) and ii.name.endswith('exp.txt')
        ],
                       key=lambda x: float(regex.findall(x.name)[0]))

    lw = []
    mod = []

    allfig, allax = plt.subplots()

    for i, f in enumerate(files):
        dat = np.loadtxt(f, delimiter=', ')

        if choice == 'absorption':
            absorptive = dat[:, 1]
            dispersive = -1 * np.imag(signal.hilbert(absorptive))
        elif choice == 'dispersion':
            dispersive = dat[:, 1]
            absorptive = -1 * np.imag(signal.hilbert(dispersive))
        else:
            raise ('Spelling error')
        field = dat[:, 0] * 1e4
        lw.append(
            np.abs(field[np.argmax(absorptive)] -
                   field[np.argmin(absorptive)]))
        mod.append(float(regex.findall(f.name)[0]))

        if i == 0:
            Hpp = np.abs(field[np.argmax(absorptive)] -
                         field[np.argmin(absorptive)])

        allax.plot(field,
                   absorptive / np.max(np.abs(absorptive)),
                   label=f'{float(regex.findall(f.name)[0])} mA')

    def forced_fit(x, scale):
        return fit(x, scale, Hpp)

    fig, ax = plt.subplots()
    ax.plot(mod, lw)
    smoothmod = np.linspace(mod[0], mod[-1], 1000)

    if fit_Hpp_0:
        popt, pcov = optimize.curve_fit(fit, mod, lw)
        ax.plot(smoothmod,
                fit(smoothmod, *popt),
                label=r"cal$=$" + f"{popt[0]:.2f} G/mA\n" + "$H_{pp}=$" +
                f"{popt[1]:.2f} G")
    else:
        popt, pcov = optimize.curve_fit(forced_fit, mod, lw)
        ax.plot(smoothmod,
                forced_fit(smoothmod, *popt),
                label=r"cal$=$" + f"{popt[0]:.2f} G/mA\n" + "$H_{pp}=$" +
                f"{Hpp:.2f} G")
    allax.legend()
    ax.legend()


def fit(mod, a, Hpp):
    return Hpp * ((a * mod / Hpp)**2 + 5 - 2 *
                  (4 + (a * mod / Hpp)**2)**(1 / 2))**(1 / 2)


def main():
    calibrate(targ, fit_Hpp_0=False)


if __name__ == "__main__":
    main()
    plt.show()
