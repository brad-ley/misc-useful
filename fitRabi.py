import ast
import os
from dataclasses import dataclass
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from matplotlib import rc
from scipy.optimize import curve_fit

from readDataFile import read

if __name__ == "__main__":
    plt.style.use(['science'])
    # rc('text.latex', preamble=r'\usepackage{cmbright}')
    rcParams = [
        # ['font.family', 'sans-serif'],
        ['font.size', 14],
        ['axes.linewidth', 1],
        ['lines.linewidth', 2],
        ['xtick.major.size', 5],
        ['xtick.major.width', 1],
        ['xtick.minor.size', 2],
        ['xtick.minor.width', 1],
        ['ytick.major.size', 5],
        ['ytick.major.width', 1],
        ['ytick.minor.size', 2],
        ['ytick.minor.width', 1],
    ]
    plt.rcParams.update(dict(rcParams))


def func(xdata, freq, a, b, d, phi):
    return a + d * np.exp(-b * xdata) * np.cos(2 * np.pi * freq * xdata + phi)


# def func2(xdata, freq, a, b, d):
#     return a + d * np.exp(-b * xdata) * np.cos(2 * np.pi * freq * xdata + 3.37)


def process(filename, subtract_bkg=False, savgol=False):
    """process.

    :param filename: input .dat filename
    :param subtract_bkg: bool to subtract background
    :param savgol: bool to apply Savitzky-Golay filtering
    """
    header, data = read(filename)

    data_array = np.array(data)
    data_dict = {
        'param': 1E6 * data_array[:, 0],
        'real': data_array[:, 1],
        'imag': data_array[:, 2],
    }

    t_f = 15
    x = data_dict['param'][data_dict['param'] < t_f]
    add = ''

    real = data_dict['real'][data_dict['param'] < t_f]
    imag = data_dict['imag'][data_dict['param'] < t_f]
    # real /= np.max(np.abs(data_dict['real'][data_dict['param'] < t_f]))
    # imag /= np.max(np.abs(data_dict['real'][data_dict['param'] < t_f]))
    dat = real + 1j * imag

    savename = P(filename).parent.joinpath(P(filename).stem + '_fig.png')
    popt, pcov = curve_fit(func, x, np.abs(dat), maxfev=100000)
    # popt, pcov = curve_fit(func2, x, np.abs(dat), maxfev=100000)
    err = np.sqrt(np.diag(pcov))
    fitx = np.linspace(x[0], x[-1], 1000)
    min_time = fitx[np.argmin(func(fitx, *popt))]
    # min_time = x[np.argmax(np.abs(dat))]
    outstr = f"min_time = {min_time:.2f} us\nfreq = {1/(2*min_time):.3f} MHz"
    # min_time = fitx[np.argmin(func2(fitx, *popt))]
    # print(popt)
    fig, ax = plt.subplots()
    # ax.plot(x, real, label='Real', c='blue')
    # ax.plot(x, imag, label='Imag', c='green')
    ax.plot(x, np.abs(dat), label='Echo amp.', c='k')
    ax.plot(
        fitx,
        func(fitx, *popt),
        # func2(fitx, *popt),
        # label=f"Min time: {min_time:.2f} $\mu$s\nFreq: {popt[0]:.2f} MHz",
        label=rf"Fit $\nu={popt[0]:.2f}\pm{err[0]:.2f}\,$MHz",
        c='red',
        ls='--')
    ax.legend()
    ax.set_ylabel('Signal intensity (arb. u)')
    # ax.set_yticks([])
    ax.set_xlabel('$P_1$ length ($\mu$s)')
    # ax.set_title('Rabi echo intensity vs. inversion pulse length')
    # for s in ['top', 'right']:
    #     ax.spines[s].set_visible(False)

    P(filename).parent.joinpath(P(filename).stem +
                                '_fit.txt').write_text(outstr)
    plt.savefig(savename, dpi=300)


if __name__ == "__main__":
    filename = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/6/21/Diamond pulsed/SSH-T/M01_rabiFID_000.dat'
    process(filename, savgol=False)
    # process(f)
    plt.show()
