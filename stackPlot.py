import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize
from scipy.stats import cauchy


def lorentzian(x, x0, a, gam):
    return 1 / np.pi * a * 1 / 2 * gam / ((1 / 2 * gam)**2 + (x - x0)**2)


def expfit(x, a, b):
    return np.array(a * np.exp(-x / b))


def altfit(x, a, b):
    return np.array(a * x**(-1 / 4) + b)


def linfit(x, m, b):
    return np.array(m * x + b)


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
    temps = []
    gs = []
    widths = []
    basetemps = []
    basegs = []
    basewidths = []

    for file in files:
        temperature = float("".join(
            [ii.strip('K') for ii in file.split('_') if 'K' in ii]))
        name = str(temperature) + ' K'

        data = np.loadtxt(targ + file, skiprows=1, delimiter=', ')
        x = data[:, 0] + 8.57
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

            max_idx = np.where(y == np.max(y))[0][0]
            min_idx = np.where(y == np.min(y))[0][0]

            linewidth = float(x[min_idx] - x[max_idx])

            # zero crossing to find g-shift
            crossing_idx = max_idx + \
                np.where(np.diff(np.sign(y))[max_idx:min_idx] == -2)[0]
            crossing = x[crossing_idx[0]]

            if file == files[0]:
                g_center = crossing

            g_shift = (crossing - g_center) / g_center * 100

            # if not file == files[0]:
            #     temps.append(temperature)
            #     gs.append(g_shift)
            basetemps.append(temperature)
            basegs.append(g_shift)
            basewidths.append(x[min_idx] - x[max_idx])

            if temperature < 100:
                temps.append(temperature)
                gs.append(g_shift)
                widths.append(x[min_idx] - x[max_idx])

            if file == files[-1]:
                temps = np.array(temps)
                gs = np.array(gs)
                widths = np.array(widths)
                basetemps = np.array(basetemps)
                basegs = np.array(basegs)
                basewidths = np.array(basewidths)
                popt, pcov = optimize.curve_fit(
                    expfit,
                    temps,
                    widths,
                    maxfev=10000,
                )
                poptalt, pcovalt = optimize.curve_fit(
                    altfit,
                    temps,
                    widths,
                    maxfev=10000,
                )
                poptg, pcovg = optimize.curve_fit(
                    expfit,
                    temps,
                    gs,
                    maxfev=10000,
                )

                plt.figure('g-shift scatter')
                plt.scatter(basetemps, basegs, c='black', label='Raw data')
                plt.plot(np.linspace(temps[0], temps[-1], 1000),
                         expfit(np.linspace(temps[0], temps[-1], 1000),
                                *poptg),
                         label=(r"$exp\left(\frac{-T}{\tau}\right)$; $\tau=$" +
                                f"{poptg[1]:.2f}"))
                plt.legend()
                plt.ylabel('% shift')
                plt.xlabel('Temperature (K)')
                plt.title('$g$-shift vs. temperature in BDPA-Bz')
                plt.figure('Linewidth')
                plt.scatter(basetemps,
                            1e4 * basewidths,
                            c='black',
                            label='Raw data')
                plt.plot(np.linspace(temps[0], temps[-1], 1000),
                         1e4 *
                         expfit(np.linspace(temps[0], temps[-1], 1000), *popt),
                         label=(r"$exp\left(\frac{-T}{\tau}\right)$; $\tau=$" +
                                f"{popt[1]:.2f}"))
                plt.plot(
                    np.linspace(temps[0], temps[-1], 1000),
                    1e4 *
                    altfit(np.linspace(temps[0], temps[-1], 1000), *poptalt),
                    label=r"$A T^{-1/4}$")
                plt.legend()
                plt.ylabel('Linewidth (G)')
                plt.xlabel('Temperature (K)')
                plt.title('Linewidth vs. temperature in BDPA-Bz')

                poptlin, pcovlin = optimize.curve_fit(
                    linfit,
                    1e4 * basewidths,
                    basegs,
                    maxfev=10000,
                )
                plt.figure('g-shift vs linewidth')
                plt.scatter(1e4 * basewidths, basegs,
                            c=np.log(basetemps), cmap='plasma', label='Raw data')
                plt.plot(1e4 * np.linspace(basewidths[0], basewidths[-1], 1000),
                         linfit(
                             1e4 *
                    np.linspace(basewidths[0], basewidths[-1], 1000),
                             *poptlin),
                         color='black',
                         label=f'Fit: y={poptlin[0]:.2}x + {poptlin[1]:.2f}')
                cbar = plt.colorbar(ticks=np.log(basetemps))
                cbar.ax.set_ylabel('Temperature (K)')
                cbar.set_ticklabels(basetemps)
                plt.ylabel('g-shift %')
                plt.xlabel('Linewidth (G)')
                # plt.zlabel('Temperature (K)')
                plt.title('g-shift vs linewidth')
                plt.legend()

            plt.figure('Stacked ' + title.lower())
            plt.annotate(f"{linewidth*1e4:.1f} G",
                         (x[min_idx] + 15e-4, shift * count))
            plt.annotate(f"{name}", (x[max_idx] - 35e-4, shift * count))

        plt.figure('Stacked ' + title.lower())
        plt.plot(x, y / np.max(np.abs(y)) + shift * count, label=name)
        count -= 1

        if file == files[-3]:
            x_min = x[0] * (1 - 1e-4)
            x_max = x[-1] * (1 + 1e-4)
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
    plt.savefig(targ + f"shifted_{start}fig.png", dpi=200)

    plt.figure('g-shift scatter')
    plt.savefig(targ + "g vs temp.png", dpi=200)

    plt.figure('Linewidth')
    plt.savefig(targ + "linewidth vs T.png", dpi=200)
    plt.figure('g-shift vs linewidth')
    plt.savefig(targ + "gshift vs linewidth.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    make(targ='/Users/Brad/odrive/Google Drive/Research/Data/2020/10/VT_cw_BDPA', kind='abs')
