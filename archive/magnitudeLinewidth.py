import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit as cf
from scipy.signal import find_peaks, hilbert

from readDataFile import read


def lorentzianabs(x, x0, T2):
    return 1 / T2 / ((x - x0)**2 + 1 / T2**2)


def lorentziandisp(x, x0, T2):
    return (x - x0) / ((x - x0)**2 + 1 / T2**2)


def magnitude(x, x0, T2, A):
    return A * np.abs(lorentzianabs(x, x0, T2) + 1j * lorentziandisp(x, x0, T2))


def fwhm(f, y):
    r = np.where(y > 1/2 * np.max(y))[0]
    return f[r[-1]] - f[r[0]] 


def main():
    for T in [1/10, 3/10, 1, 3, 10]:
        l = 3000
        f = np.linspace(0, l, 10000000)
        ab = lorentzianabs(f, l // 2, T)
        # disp = np.imag(hilbert(ab))
        disp = lorentziandisp(f, l//2, T)
        mag = np.abs(ab + 1j * disp) / np.max(np.abs(ab + 1j * disp))
        plotall = False
        if plotall:
            fig, ax = plt.subplots(nrows=2, ncols=1)
        else:
            fig, ax = plt.subplots()
        ### find linewidth of absorption and magnitude ###
        Dab = np.diff(ab)
        Dmag = np.diff(mag)
        popt, pcov = cf(magnitude, f, mag, p0=[l // 2, T, 1], maxfev=10000)
        out = np.zeros(2)

        for i, z in enumerate(zip([Dab, Dmag], ['abs', 'mag'])):
            d = np.array(z[0]) / np.max(np.array(z[0]))
            peaks = find_peaks(np.abs(d))
            out[i] = (f[peaks[0][1]] - f[peaks[0][0]])

        lw = fwhm(f, ab)
        # ax[0].plot(f, ab / np.max(ab), label='abs')
        # ax[0].plot(f, disp / np.max(disp), label='disp')
        print(f"Fitted linewidth is {1/np.abs(popt[1]):.2f}")
        print(f"Extracted 1/2*FWHM from abs is {lw:.2f}")
        print(f"Fit:p2p is {np.abs(popt[1])/2*lw:.2f}")
        print("=============")
        if plotall:
            ax[0].plot(f, mag, label='mag')
            ax[0].plot(f, magnitude(f, *popt), label='fiit')
            l = ax[0].legend()
            ax[1].plot(f[1:], np.abs(Dab / np.max(Dab)))
            ax[1].plot(f[1:], np.abs(Dmag / np.max(Dmag)))
        else:
            ax.plot(f, mag, label='mag')
            ax.plot(f, magnitude(f, *popt), label='fit')
            l = ax.legend()
        l.set_draggable(True)
    plt.show()


if __name__ == "__main__":
    main()
