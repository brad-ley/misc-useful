import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit

from readDataFile import read


def main():
    process(
        '/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/06/03/Concentrated_AsLOV_cwEPR/Try 2/M09/M09_pulsing.dat',
        5,
        25,
        window_frac=100,
        order=2
    )


def biexponential(x, A, a1, t1, a2, t2):
    return A + a1 * np.exp(- x / t1) + a2 * np.exp(-x / t2)


def process(filename, on, off, window_frac=10, order=2):
    """process.

    :param filename: input filename
    :param on: on-time for laser
    :param off: off-time for laser
    :window_frac: reciprocal of data length for window choice
    :order: savgol_filter polyfit order
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

    prevlen = 0

    while index < len(sig):
        lo = np.where(t >= index * (on + off))[0][0]
        hi = np.where(t < (index + 1) * (on + off))[0][-1]

        if np.abs(hi - lo) < prevlen * 0.9:
            break

        if window_frac == 0: # use 0 to not do savgol filtering
            avgsig.append(
                np.abs(sig[lo:hi]))
            avgr.append(
                np.real(r[lo:hi]) + 1j * np.imag(r[lo:hi]))
            avgi.append(
                np.real(i[lo:hi]) + 1j*np.imag(i[lo:hi]))
        else:
            avgsig.append(savgol_filter(
                np.abs(sig[lo:hi]), (2 * (np.abs(hi - lo) // window_frac) + 1), order))
            avgr.append(savgol_filter(
                np.real(r)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order) + 1j * savgol_filter(
                np.imag(r)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order))
            avgi.append(savgol_filter(
                np.real(i)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order) + 1j * savgol_filter(
                np.imag(i)[lo:hi], (2 * (np.abs(hi - lo) // window_frac) + 1), order))
        prevlen = np.abs(hi - lo)
        index += 1

    smallen = np.inf

    for row in avgsig:
        if len(row) < smallen:
            smallen = len(row)

    full = np.zeros(smallen)

    plots = {"Average mag": avgsig, "Ch1 real": avgr, "Ch1 imag":
        avgr, "Ch2 real": avgi, "Ch2 imag": avgi}
        # avgr, "Ch2 real": avgi, "Ch2 imag": avgi}

    for plot, dat in plots.items():
        plt.figure(plot)
        for row in dat:
            if "real" in plot:
                row = np.real(row)
            elif "imag" in plot:
                row = np.imag(row)
            if np.min(row) < 0:
                row -= np.min(row)
            plt.plot(t[:len(row)], row / np.max(row), alpha=0.3, color='lightgray')
            full += row[:smallen] / np.max(row[:smallen])
        full = full / np.max(full)
        popt, pcov = curve_fit(biexponential, t[:smallen], full, maxfev=1000000)
        abovelas = np.where(t > on)[0][0]
        plt.plot(t[:smallen], full, label="Raw data")
        plt.plot(np.linspace(t[abovelas], t[smallen]), biexponential(np.linspace(t[abovelas], t[smallen]), *popt), label=r"Fit: $\tau_1$="+f"{popt[2]:.2f}"+r" $s^{-1}$;$\tau_2$="+f"{popt[4]:.2f}"+r" $s^{-1}$")
        plt.legend()
        rang = np.max(full) - np.min(full)
        plt.annotate('Laser\npulse', (on/2, np.max(full)), color='gray', horizontalalignment='center')
        plt.ylim(np.min(full) - rang/4, np.max(full) + rang/4)
        plt.axvspan(0, on, facecolor='palegreen')
        plt.title(plot)
        if plot == "Ch2 imag":
            plt.title("Time-resolved EPR absoption vs. time")
        plt.ylabel('Normalized signal')
        plt.xlabel('Time (s)')
        full = np.zeros(smallen)
        plt.savefig(P(filename).parent.joinpath(f"{plot}.png"))

    plt.show()


if __name__ == "__main__":
    main()
