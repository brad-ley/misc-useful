import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit as cf
from scipy.signal import savgol_filter
from pathlib import Path as P
from readDataFile import read


def func(xdata, freq, a, b, d, phi):
    return a + d * np.exp(-b * xdata) * np.cos(2 * np.pi * freq * xdata + phi)


def process(filename, subtract_bkg=False, savgol=False):
    header, data = read(filename)

    data_array = np.array(data)
    data_dict = {
        'param': 1E6 * data_array[:, 0],
        'echo': data_array[:, 3],
        'bkg': data_array[:, 4],
    }
    
    x = data_dict['param']
    add = ''
    if subtract_bkg:
        dat = data_dict['echo'] - data_dict['bkg']
        add += 'subtract_bkg_'
    else:
        dat = data_dict['echo']

    if savgol:
        dat = savgol_filter(dat, 2*(len(x)//10)+1, 3)
        add += 'savgol_'

    savename = P(filename).parent.joinpath(add + 'Rabi.png')
    popt, pcov = cf(func, x, dat)
    min_time = np.min(func(x, *popt))
    rabi_freq = 1 / (2 * min_time * 1E-6) / 1E6 # convert the us to s then get freq
    # print(popt)
    fig, ax = plt.subplots()
    ax.plot(x, dat, label='Raw data', c='black')
    fitx = np.linspace(x[0], x[-1], 1000)
    ax.plot(
        fitx,
        func(fitx, *popt),
        label=f"Min time: {min_time:.2f} $\mu$s\nFreq: {popt[0]:.2f} MHz", c='red')
    ax.legend()
    ax.set_ylabel('Echo intensity (arb. u)')
    ax.set_yticks([])
    ax.set_xlabel('$P_1$ length ($\mu$s)')
    ax.set_title('Rabi echo intensity vs. inversion pulse length')
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)

    plt.savefig(savename, dpi=300)


if __name__ == "__main__":
    f = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/11/29/M16_RabiE_000.dat'
    process(f, subtract_bkg=True, savgol=True)
    process(f)
    plt.show()
