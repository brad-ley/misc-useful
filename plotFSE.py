import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit as cf
from scipy.signal import savgol_filter
from pathlib import Path as P
from readDataFile import read


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
        'echo': data_array[:, 1],
    }
    
    x = data_dict['param']
    add = ''

    dat = data_dict['echo']
    if savgol:
        dat = savgol_filter(dat, 2*(len(x)//20)+1, 3)
        add += 'savgol_'


    savename = P(filename).parent.joinpath(add + 'FSE.png')

    fig, ax = plt.subplots()
    ax.plot(x, dat, label='Raw data', c='black')
    ax.legend()
    ax.set_ylabel('Echo intensity (arb. u)')
    ax.set_yticks([])
    ax.set_xlabel('$P_1$ length ($\mu$s)')
    ax.set_title('Field swept echo')
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)

    plt.savefig(savename, dpi=300)


if __name__ == "__main__":
    f = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/11/29/M30_FSE_000.dat'
    process(f)
    plt.show()
