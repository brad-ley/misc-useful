from pathlib import Path as P

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit as cf
from scipy.signal import savgol_filter

from readDataFile import read

from matplotlib import rc
plt.style.use('science')
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['xtick.major.size'] = 5
plt.rcParams['xtick.major.width'] = 1
plt.rcParams['xtick.minor.size'] = 2
plt.rcParams['xtick.minor.width'] = 1
plt.rcParams['ytick.major.size'] = 5
plt.rcParams['ytick.major.width'] = 1
plt.rcParams['ytick.minor.size'] = 2
plt.rcParams['ytick.minor.width'] = 1
lw=2


def process(filename, subtract_bkg=False, savgol=False):
    """process.

    :param filename: input .dat filename
    :param subtract_bkg: bool to subtract background
    :param savgol: bool to apply Savitzky-Golay filtering
    """
    files = [ii for ii in P(filename).parent.iterdir() if ii.suffix == '.dat']
    fig, ax = plt.subplots()
    files.sort()
    files.insert(0, files.pop(1))
    # files.reverse()

    labels = ['Roof mirror', 'Flat mirror']
    for i, f in enumerate(files):
        header, data = read(f)

        data_array = np.array(data)

        data_dict = {
            'param': data_array[:, 0] - (np.max(data_array[:, 0]) + np.min(data_array[:, 0])) / 2,
            'echo': np.abs(data_array[:, 1] + 1j * data_array[:, 2]),
        }

        x = data_dict['param']
        add = ''

        dat = data_dict['echo']

        if savgol:
            dat = savgol_filter(dat, 2 * (len(x) // 20) + 1, 3)
            add += 'savgol_'

        snrfrac = 1 / 5
        snrpart = x > np.max(x) - (np.max(x) - np.min(x)) * snrfrac
        snrpart += x < np.min(x) + (np.max(x) - np.min(x)) * snrfrac
        RMS = np.sqrt(np.mean(dat[snrpart]**2))
        peak = np.max(dat)
        print(f.stem, RMS, peak)

        a = 0.25
        c = 0.75
        # ax.axvspan(x[0], x[np.where(
        #     np.diff(snrpart) == True)[0][0]], ymin=i * c, ymax=i * c + 1, facecolor='k', alpha=a)
        # ax.axvspan(x[np.where(np.diff(snrpart) == True)[0][1]], x[-1],
        #            ymin=i * c, ymax=i * c + 1, facecolor='k', alpha=a)
        # ax.plot(x, dat / np.max(dat) + i * c, label=" ".join([ii for ii in f.stem.split(
        #     "_") if 'sweep' not in ii][1:-1]) + f": $SNR={int(peak/RMS)}$", lw=2)
        ax.plot(x, dat / np.max(dat) + i * c, label=labels[i] + f": $SNR={int(peak/RMS)}$", lw=2)

    savename = P(filename).parent.joinpath(add + 'FSE.png')

    ax.legend()

    handles, labels = ax.get_legend_handles_labels()
    order = [1, 0]
  
    ax.legend([handles[i] for i in order], [labels[i] for i in order], loc='upper right',markerfirst=True,handlelength=1,handletextpad=0.4,labelspacing=0.2,)
    # ax.legend()
    ax.set_ylabel('Echo intensity (arb. u)')
    # ax.set_yticks([])
    ax.set_xlabel('Field (T)')
    # ax.set_title(r'SNR ($\frac{peak}{RMS_{baseline}}$)')
    ax.set_ylim(top=2.5)

    # for s in ['top', 'right']:
    #     ax.spines[s].set_visible(False)

    plt.savefig(savename, dpi=300)


if __name__ == "__main__":
    f = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/8/17/poster fig/M04_dsweep_FlatMirror_000.dat'
    process(f)
    plt.show()
