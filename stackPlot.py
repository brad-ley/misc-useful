import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize
from scipy.stats import cauchy


def lorentzian(x, x0, a, gam):
    return 1 / np.pi * a * 1 / 2 * gam / ((1 / 2 * gam)**2 + (x - x0)**2)


def make(targ='./', kind='disp'):
    """
    Plots the absorption or dispersion lineshapes from makeAbsDisp.py depending
    on :kind: param, 'disp' or 'abs'
    :param targ: input target directory
    """

    if not targ.endswith('/'):
        targ += '/'

    if kind.startswith('disp'):
        title = 'Dispersion'
        start = 'dispersion_'
        shift = 1
        chi = "$\chi'$"
    elif kind.startswith('abs'):
        title = 'Absorption'
        start = 'absorption_'
        shift = 1.5
        chi = "$\chi''$"
    else:
        start = 'error_'
        shift = 0
        chi = ''

    files = sorted([ii for ii in os.listdir(targ) if ii.startswith(start)],
                   key=lambda x: float("".join(
                       [ii.strip('K') for ii in x.split('_') if 'K' in ii])),
                   reverse=True)

    count = 0
    fig, axes = plt.subplots(len(files), sharex=True)

    for file in files:
        temperature = float("".join(
            [ii.strip('K') for ii in file.split('_') if 'K' in ii]))
        name = str(temperature) + ' K'

        data = np.loadtxt(targ + file, skiprows=1, delimiter=', ')
        x = data[:, 0]
        y = data[:, 1]
        y = y / np.max(np.abs(y))

        integral_data = integrate.cumtrapz(y, x, initial=0)
        integral_y = integral_data / np.max(np.abs(integral_data))
        max_idx = np.where(integral_y == np.max(integral_y))[0]
        # max_idx = max_idx[len(max_idx)//2]
        max_idx = max_idx[0]

        if kind == 'abs':
            p0 = [8.583, 1, 5e-4]
            popt, pcov = optimize.curve_fit(lorentzian,
                                            x,
                                            integral_y,
                                            maxfev=10000,
                                            p0=p0)
            axes[files.index(file)].plot(x, integral_y, 'k')
            axes[files.index(file)].plot(
                x,
                lorentzian(x, *popt),
                'r',
                label=f"{popt[2]*10**(4):.2f} G @ {name}")
            axes[files.index(file)].set_yticks([])
            axes[files.index(file)].legend(loc='center left')

            if file == files[-1]:
                axes[files.index(file)].set_xlabel('Field (T)')

            if file == files[len(files) // 2]:
                axes[files.index(file)].set_ylabel('Absorption (arb. u)')

            fig.suptitle(
                'Absorption (red: fit, black: experiment) vs\nfield for varying temperature T'
            )
            fig.savefig(targ + 'fitted_absorptions.png')

            max_idx = np.where(y == np.max(y))
            min_idx = np.where(y == np.min(y))

            linewidth = float(x[min_idx] - x[max_idx])

            plt.figure('Stacked ' + title.lower())
            plt.annotate(f"{linewidth*1e4:.1f} G", (x[min_idx] + 15e-4, shift * count))
            plt.annotate(f"{name}", (x[max_idx] - 35e-4, shift * count))

        plt.figure('Stacked ' + title.lower())
        plt.plot(x, y / np.max(np.abs(y)) + shift * count, label=name)
        count -= 1

        if file == files[-3]:
            x_min = data[0, 0] * (1 - 1e-4)
            x_max = data[-1, 0] * (1 + 1e-4)
    plt.xlim([x_min, x_max])

    plt.ylabel('Signal (shifted vertically for clarity)')
    plt.tick_params(
        axis='y',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        left=False,
        labelleft=False)  # ticks along the bottom edge are off

    plt.xlabel('Field (T)')
    # plt.legend().set_draggable(True)
    plt.title(f"cwEPR, {chi} of BDPA-Bz")
    plt.savefig(targ + f"shifted_{start}fig.png")
    plt.show()


if __name__ == "__main__":
    make(targ='/Users/Brad/Downloads/VT_cw_BDPA', kind='abs')
