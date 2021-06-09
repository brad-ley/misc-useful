import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit as cf
from pathlib import Path as P
from readDataFile import read


def func(xdata, freq, a, b, d, phi):
    return a + d * np.exp(-b * xdata) * np.cos(2 * np.pi * freq * xdata + phi)


def process(filename):
    header, data = read(filename)

    data_array = np.array(data)
    data_dict = {
        'param': 1E6 * data_array[:, 0],
        'echo': data_array[:, 3],
    }

    popt, pcov = cf(func, data_dict['param'], data_dict['echo'])
    min_idx = np.argmin(func(data_dict['param'], *popt))
    min_time = data_dict['param'][min_idx]
    rabi_freq = 1 / (2 * min_time * 1E-6) / 1E6 # convert the us to s then get freq
    # print(popt)
    fig, ax = plt.subplots()
    ax.plot(data_dict['param'], data_dict['echo'], label='Raw data', c='black')
    ax.plot(
        data_dict['param'],
        func(data_dict['param'], *popt),
        label=f"Min time: {min_time:.2f} $\mu$s\nFreq: {popt[0]:.2f} MHz", c='red')
    ax.legend()
    ax.set_ylabel('Echo intensity (arb. u)')
    ax.set_yticks([])
    ax.set_xlabel('$P_1$ length ($\mu$s)')
    ax.set_title('Rabi echo intensity vs. inversion pulse length')
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    plt.savefig(P(filename).parent.joinpath('fixedSourceRabi.png'), dpi=300)
    plt.show()


if __name__ == "__main__":
    process('/Users/Brad/Downloads/M15_rabi_000.dat')
