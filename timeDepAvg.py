import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

from readDataFile import read


def main(filename):
    process(
        filename,
        on=5,
        off=175,
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

    prevlen = 0

    while index < len(sig):
        lo = np.where(t >= index * (on + off))[0][0]
        hi = np.where(t < (index + 1) * (on + off))[0][-1]

        if np.abs(hi - lo) < prevlen * 0.9:
            break

        if window_frac == 0:  # use 0 to not do savgol filtering
            avgsig.append(
                sig[lo:hi])
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
        index += 1

    smallen = np.inf

    for row in avgsig:
        if len(row) < smallen:
            smallen = len(row)

    full = np.zeros(smallen)

    avgsig1 = [np.abs(np.real(ii)) for ii in avgsig]
    avgsig2 = [np.abs(np.imag(ii)) for ii in avgsig]

    plots = {"Ch1 mag": avgsig1, "Ch2 mag":avgsig2, "Ch1 real": avgr, "Ch1 imag":
             avgr, "Ch2 real": avgi, "Ch2 imag": avgi}

    for plot, dat in plots.items():
        plt.figure(plot)

        for row in dat:
            if "real" in plot:
                row = np.real(row)
            elif "imag" in plot:
                row = np.imag(row)

            if np.min(row) < 0:
                row -= np.min(row)
            plt.plot(t[:len(row)], row / np.max(row),
                     alpha=0.3, color='lightgray')
            full += row[:smallen]
            # full += (row[:smallen] / np.max(np.abs(row[:smallen])))
        full = full / np.max(full)
        abovelas = np.where(t > on)[0][0]
        plt.plot(t[:smallen], full, label="Raw data")
        amp_guess = 0.2 # amplitude of exponential decay
        bl_guess = 0.5 # starting point of decay
        tau_guess = 50 # time constant guess 

        if bi:
            popt, pcov = curve_fit(biexponential, t[:smallen], full, maxfev=10000000, p0=[
                                   bl_guess, amp_guess, tau_guess, amp_guess, tau_guess])
            plt.plot(np.linspace(t[abovelas], t[smallen]), biexponential(np.linspace(t[abovelas], t[smallen]), *popt),
                     label=r"Fit: $\tau_1$=" + f"{popt[2]:.2f}" + r" s$^{-1}$;$\tau_2$=" + f"{popt[4]:.2f}" + r" s$^{-1}$")
        else:
            popt, pcov = curve_fit(
                exponential, t[:smallen], full, maxfev=10000000, p0=[bl_guess, amp_guess, tau_guess])
            plt.plot(np.linspace(t[abovelas], t[smallen]), exponential(np.linspace(
                t[abovelas], t[smallen]), *popt), label=r"Fit: $\tau_1$=" + f"{popt[2]:.2f}" + r" s$^{-1}$")

        plt.legend()
        rang = np.max(full) - np.min(full)
        plt.annotate('Laser\npulse', (on / 2, np.max(full)),
                     color='gray', horizontalalignment='center')
        plt.ylim(np.min(full) - rang / 4, np.max(full) + rang / 4)
        plt.axvspan(0, on, facecolor='palegreen')
        plt.title(plot)

        if plot == "Ch2 imag":
            plt.title("Time-resolved EPR absoption vs. time")
        plt.ylabel('Normalized signal')
        plt.xlabel('Time (s)')
        full = np.zeros(smallen)
        plt.savefig(P(filename).parent.joinpath(f"{plot}.png"), dpi=300)

    plt.show()


if __name__ == "__main__":
    f = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/7/M06_537_pulsing_40mA.dat'
    main(f)
