import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import constants, integrate, optimize
from scipy.stats import cauchy


def lorentzian(x, x0, a, gam):
    return 1 / np.pi * a * 1 / 2 * gam / ((1 / 2 * gam)**2 + (x - x0)**2)


def dlorentzian(x, x0, a, gam):
    return 16 * (x - x0) * a * gam / (np.pi * (4 * (x - x0)**2 + gam**2)**2)


def ising(T, a, m):
    return a * m**2 / (T * np.cosh((m * 8.58) / (constants.Boltzmann * T))**2)


def takahashi(T, a, T0, J, b):
    return b + a * (1 / (np.pi**2 * -1*np.abs(J)) + (1 + 1/2* np.log(T0 / T)))


def gFit(T, T0, a):
    return a * np.sqrt(3) / (4 * np.pi * np.log(T0 / T))


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

    if kind.startswith('abs'):
        fig, axes = plt.subplots(len(files), sharex=True)
        axn = plt.subplot(111)

    temps = []
    gs = []
    widths = []
    basetemps = []
    basegs = []
    fitgs = []
    basewidths = []
    fitwidths = []

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

        if kind.startswith('abs'):
            # print(x[y.argmax()], x[y.argmin()])
            p0 = [
                x[np.where(y[y.argmax():y.argmin()] > 0)[0][-1] + y.argmax()],
                np.max(np.abs(y)),
                np.abs(x[y.argmax()] - x[y.argmin()])
            ]
            dopt, dcov = optimize.curve_fit(dlorentzian,
                                            x,
                                            y,
                                            maxfev=10000,
                                            p0=p0)
            popt, pcov = optimize.curve_fit(lorentzian,
                                            x,
                                            integral_y,
                                            maxfev=10000,
                                            p0=p0)

            center = dopt[0]

            if file == files[0]:
                gHighTFit = center

            fitgs.append((1/center - 1/gHighTFit) / (1/gHighTFit) * 100)
            axn.plot(x, y - 2 * files.index(file), 'k')
            axn.plot(x, dlorentzian(x, *dopt) - 2 * files.index(file), 'r')
            axn.set_yticks([])
            axn.annotate(f"{name}", (x[x.argmin()] *
                                     (1 - 1e-4), -0.5 - 2 * files.index(file)),
                         horizontalalignment='right')
            axn.annotate(f"{dopt[2]*10**(4):.2f} G",
                         (x[x.argmax()] *
                          (1 + 1e-4), -0.5 - 2 * files.index(file)),
                         horizontalalignment='left')
            axn.set_xlabel("Temperature (T)")

            for pos in ['top', 'right', 'left']:
                axn.spines[pos].set_visible(False)

            fitwidths.append(dopt[2] * 1e4)
            # plt.suptitle(
            #     r'$\frac{d \chi '
            #     '}{d B}$ (red: fit, black: experiment) vs\nfield for varying temperature T'
            # )
            plt.savefig(targ + 'fitted_absorptions.png', dpi=200)

            # axes[files.index(file)].plot(x, integral_y, 'k')
            # axes[files.index(file)].plot(
            #     x,
            #     lorentzian(x, *popt),
            #     'r',
            #     label=f"{popt[2]*10**(4):.2f} G @ {name}")
            # axes[files.index(file)].set_yticks([])
            # axes[files.index(file)].legend(loc='center left')

            # if file == files[-1]:
            #     axes[files.index(file)].set_xlabel('Field (T)')

            # if file == files[len(files) // 2]:
            #     axes[files.index(file)].set_ylabel('Absorption (arb. u)')

            fig.suptitle(
                'Absorption (red: fit, black: experiment) vs\nfield for varying temperature T'
            )
            fig.savefig(targ + 'fitted_absorptions.png', dpi=200)

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

            if temperature < 100 and temperature > 6:
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
                poptising, pcovising = optimize.curve_fit(ising,
                                                          basetemps,
                                                          fitwidths,
                                                          maxfev=10000,
                                                          p0=[30e48, 9e-24])
                poptg, pcovg = optimize.curve_fit(
                    takahashi,
                    1/basetemps,
                    fitgs,
                    maxfev=10000,
                    p0=[-0.001, 10, -4.4, 1]
                )

                # plt.figure('g-shift scatter')
                # plt.scatter(basetemps, basegs, c='black', label='Raw data')
                # plt.plot(np.linspace(temps[0], temps[-1], 1000),
                #          expfit(np.linspace(temps[0], temps[-1], 1000),
                #                 *poptg),
                #          label=(r"$exp\left(\frac{-T}{\tau}\right)$; $\tau=$" +
                #                 f"{poptg[1]:.2f}"))
                # plt.legend()
                # plt.ylabel('% shift')
                # plt.xlabel('Temperature (K)')
                # plt.title('$g$-shift vs. temperature in BDPA-Bz')
                # plt.figure('Linewidth')
                # plt.scatter(basetemps[-9:],
                #             1e4 * basewidths[-9:],
                #             c='black',
                #             label='Raw data')
                # plt.legend()
                # plt.ylabel('Linewidth (G)')
                # plt.xlabel('Temperature (K)')
                # plt.title('Linewidth vs. temperature in BDPA-Bz')

                endpts_to_skip = 2
                poptlin, pcovlin = optimize.curve_fit(
                    linfit,
                    fitwidths[:-endpts_to_skip],
                    fitgs[:-endpts_to_skip],
                    maxfev=10000,
                )
                plt.figure('Fit g-shift vs linewidth')
                plt.scatter(fitwidths,
                            fitgs,
                            c=np.log10(basetemps),
                            cmap='plasma',
                            label='Raw data')
                plt.plot(np.linspace(
                    np.sort(fitwidths)[0],
                    np.sort(fitwidths)[-endpts_to_skip], 1000),
                         linfit(
                             np.linspace(
                                 np.sort(fitwidths)[0],
                                 np.sort(fitwidths)[-endpts_to_skip], 1000),
                             *poptlin),
                         color='black',
                         label=f'Fit: y={poptlin[0]:.2}x + {poptlin[1]:.2f}')
                cbar = plt.colorbar(
                    ticks=np.linspace(np.log10(np.min(basetemps)),
                                      np.log10(np.max(basetemps)), 10))
                cbar.ax.set_ylabel('Temperature (K)')
                cbar.set_ticklabels([
                    f"{ii:.1f}"
                    for ii in np.logspace(np.log10(np.min(basetemps)),
                                          np.log10(np.max(basetemps)), 10)
                ])
                plt.ylabel('g-shift %')
                plt.xlabel('Linewidth (G)')
                # plt.zlabel('Temperature (K)')
                plt.title('Fit g-shift vs linewidth')
                # plt.figure('g-shift scatter')
                # plt.savefig(targ + "g vs temp.png", dpi=200)
                # plt.figure('Linewidth')
                # plt.savefig(targ + "linewidth vs T.png", dpi=200)
                plt.figure('Fit g-shift vs linewidth')
                plt.savefig(targ + "gshift vs linewidth.png", dpi=200)
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

    plt.figure("Fitted width vs. temperature")
    
    points = 10
    x = np.array(basetemps)[np.array(basetemps, dtype='int64').argsort()[:points]]
    plt.scatter(x,
                np.array(fitwidths)[np.array(basetemps,
                                             dtype='int64').argsort()[:points]],
                color='k',
                label="Raw data")
    # plt.plot(np.linspace(x[0], x[-1], 1000),
    #          ising(np.linspace(x[0], x[-1], 1000), *poptising),
    #          color='black',
    #          label=(f"Ising fit\nA={poptising[0]:.2e}\nm={poptising[1]:.2e}"))
    plt.legend()
    plt.ylabel("Linewidth (G)")
    plt.xlabel("Temperature (K)")
    plt.title("Fit linewidth vs. temperature")
    plt.savefig(targ + "widthVtemp.png", dpi=200)

    plt.figure("Fitted g shift vs. 1/T")
    # plt.plot(1/np.linspace(basetemps[0], basetemps[-1], 1000),
    #          takahashi(np.linspace(basetemps[0], basetemps[-1], 1000), *poptg),
    #          color='black',
    #          label=(f"J={poptg[2]:.2f}; T0={poptg[1]:.2f}"))
    plt.scatter(1/np.array(basetemps)[np.array(basetemps,
                                             dtype='int64').argsort()[:]],
                np.array(fitgs)[np.array(basetemps,
                                         dtype='int64').argsort()[:]],
                color='r',
                label='Raw data')
    plt.ylabel("$g$-shift (%)")
    plt.xlabel("Inverse temperature ($K^{-1}$)")
    plt.title("Fit g-shift vs. temperature")
    plt.legend()
    plt.savefig(targ + "fitgVtemp.png", dpi=200)

    plt.show()


if __name__ == "__main__":
    make(
        targ=
        '/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2020/10/VT_cw_BDPA',
        kind='abs')
