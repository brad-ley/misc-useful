import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumtrapz
from scipy.optimize import curve_fit as cf

from readDataFile import read


def lorentzianabs(x, x0, a):
    return a / ((x - x0)**2 + a**2)


def lorentziandisp(x, x0, a):
    return (x - x0) / ((x - x0)**2 + a**2)


def magnitude(x, x0, a, A):
    return A * np.abs(lorentzianabs(x, x0, a) + 1j * lorentziandisp(x, x0, a))


def fwhm(f, y):
    r = np.where(y > 1 / 2 * np.max(y))[0]

    return f[r[-1]] - f[r[0]]


def main(filename):
    _, dab = read(filename)
    _, ddisp = read(filename.replace('absorption', 'dispersion'))

    ab = dab[:, 1]
    disp = ddisp[:, 1]
    f = dab[:, 0] - 8.62

    mag = np.abs(ab + 1j * disp)
    mag /= np.max(mag)
    lw = fwhm(f, cumtrapz(ab))
    print(f"fwhm is {lw*1e4:.2f} G")
    popt, _ = cf(magnitude, f, mag, p0=[1.7e-3, 5e-4, 1], maxfev=10000)

    fig, ax = plt.subplots()
    # ax.plot(f, ab/np.max(ab))
    # ax.plot(f[1:], cumtrapz(ab)/np.max(cumtrapz(ab)))
    ax.plot(f, mag)
    ax.plot(f, magnitude(f, *popt))
    ax.plot(f, lorentzianabs(f, *popt[:-1]) /
            np.max(lorentzianabs(f, *popt[:-1])))
    ax.plot(f, lorentziandisp(f, *popt[:-1]) /
            np.max(lorentziandisp(f, *popt[:-1])))

    print(f"Linewidth: {popt[1]*1e4*2:.2f} G")

    plt.show()


if __name__ == "__main__":
    main('/Volumes/GoogleDrive/My Drive/Research/Data/2021/09/15/RT 537-406 AsLOV/RT/absorption_OffLight_exp.txt')
