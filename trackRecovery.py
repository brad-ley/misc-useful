import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from matplotlib import rc

from readDataFile import read

plt.style.use(['science', 'ieee'])
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'


def main(filename):
    process(
        filename,
        5,
        175,
        window_frac=0,
        order=3,
        bi=False
    )


def biexponential(x, A, a1, t1, a2, t2):
    return A + a1 * np.exp(- x / t1) + a2 * np.exp(-x / t2)


def exponential(x, A, a1, t1):
    return A + a1 * np.exp(- x / t1)


def process(filename, on, off, window_frac=10, order=2, bi=True):
    """process.

    :param filename: input filename
    :param on: on-time for laser
    :param off: off-time for laser
    :window_frac: reciprocal of data length for window choice
    :order: savgol_filter polyfit order
    :bi: biexponential fit
    """
    header, data = read(filename)
    t = data[:, 0]
    r = data[:, 2] + 1j * data[:, 3]
    i = data[:, 4] + 1j * data[:, 5]
    sig = np.abs(r) + 1j * np.abs(i)

    index = 0
    avgsig = []
    avgr = []
    avgi = []
    times = []

    prevlen = 0

    while index < len(sig):
        lo = np.where(t >= index * (on + off))[0][0]
        hi = np.where(t < (index + 1) * (on + off))[0][-1]

        if np.abs(hi - lo) < prevlen * 0.9:
            break

        if window_frac == 0:  # use 0 to not do savgol filtering
            avgsig.append(sig[lo:hi])
            avgr.append(
                np.real(r[lo:hi]) + 1j * np.imag(r[lo:hi]))
            avgi.append(
                np.real(i[lo:hi]) + 1j * np.imag(i[lo:hi]))
        else:
            avgsig.append(savgol_filter(
                sig[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order))
            avgr.append(savgol_filter(
                np.real(r)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order) + 1j * savgol_filter(
                np.imag(r)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order))
            avgi.append(savgol_filter(
                np.real(i)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order) + 1j * savgol_filter(
                np.imag(i)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order))
        prevlen = np.abs(hi - lo)
        times.append(t[:prevlen])
        index += 1

    amp_guess = 0.2  # amplitude of exponential decay
    bl_guess = 0.5  # starting point of decay
    tau_guess = 50  # time constant guess

    avgsig1 = [np.abs(np.real(ii)) for ii in avgsig]
    avgsig2 = [np.abs(np.imag(ii)) for ii in avgsig]

    plots = {"Ch1 mag": avgsig1, "Ch2 mag": avgsig2, "Ch1 real": avgr, "Ch1 imag":
             avgr, "Ch2 real": avgi, "Ch2 imag": avgi}

    amp_guess = 0.2  # amplitude of exponential decay
    bl_guess = 0.5  # starting point of decay
    tau_guess = 50  # time constant guess

    for plot, dat in plots.items():
        xmax = 0
        xmin = np.inf
        plt.figure(plot)
        outy = []
        outx = []

        for i, row in enumerate(dat):
            abovelas = np.where(times[i] > on)[0][0]

            if "real" in plot:
                row = np.real(row)
            elif "imag" in plot:
                row = np.imag(row)

            if np.min(row) < 0:
                row -= np.min(row)

            popt, pcov = curve_fit(
                exponential, times[i][abovelas:], row[abovelas:], maxfev=10000000, p0=[bl_guess, amp_guess, tau_guess])
            
            ### for showing tracking ###
            if outx:
                if not popt[2] > 10*np.mean(outx):
                    outy.append(abs(popt[1])/y0)
                    outx.append(popt[2])
                    plt.scatter(popt[2], abs(popt[1])/y0, c='black', alpha=(
                        1 - i / len(dat)), )

                    if popt[2] > xmax:
                        xmax = popt[2]

                    if popt[1] < xmin:
                        xmin = popt[1]
            else:
                y0 = abs(popt[1])
                outy.append(abs(popt[1])/y0)
                outx.append(popt[2])
                plt.scatter(popt[2], abs(popt[1])/y0, c='black', alpha=(
                    1 - i / len(dat)), label=f"Single run")
                if popt[2] > xmax:
                    xmax = popt[2]

                if popt[1] < xmin:
                    xmin = popt[1]
            ### for showing tracking ###

            ### for showing fits ###
            # x = np.linspace(times[i][abovelas], times[i][-1], 1000)
            # p = plt.plot(x, exponential(x, *popt))
            # plt.plot(times[i], row, c=p[0].get_color())
            # plt.annotate('Laser\npulse', (on / 2, 0.5),
            #              color='gray', horizontalalignment='center')
            # plt.axvspan(0, on, facecolor='palegreen')
            ### for showing fits ###
        
        ### for showing tracking ###
        plt.errorbar(np.mean(outx), np.mean(outy), yerr=np.std(
            outy), xerr=np.std(outx), c='red', label=f"Average")
        plt.legend(frameon=True)
        plt.xlim([xmin / 1.5, xmax * 1.5])
        plt.ylim([np.min(outy)/1.5, np.max(outy)*1.25])
        ### for showing tracking ###
        plt.ylabel('Fit amplitude (arb. u)')
        plt.xlabel(r'Fit $\tau$ (s)')
        plt.savefig(P(filename).parent.joinpath(
            f"{plot}_tracking.png"), dpi=300)
        plt.savefig(P(filename).parent.joinpath(
            f"{plot}_tracking.tif"), dpi=300)


if __name__ == "__main__":
    f = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/20/7.0 mT/M06_pulsing_rephased.dat'
    main(f)
    plt.show()

