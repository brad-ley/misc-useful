from pathlib import Path as P

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc
from scipy.optimize import curve_fit as cf
from scipy.signal import savgol_filter

from readDataFile import read

# plt.style.use(['science'])
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


def exp(x, a, b, c):
    return a + b * np.exp(-x / c)


def is_int(num):
    try:
        int(num)

        return True
    except:
        return False


def process(filename, subtract_bkg=False, savgol=False):
    """process.

    :param filename: input .dat filename
    :param subtract_bkg: bool to subtract background
    :param savgol: bool to apply Savitzky-Golay filtering
    """
    files = [ii for ii in P(filename).parent.iterdir()
             if ii.suffix == '.dat' and 'P1' in ii.stem]
    # files = [P(filename)]
    fig, ax = plt.subplots()
    files.sort(key=lambda x: float(''.join([ii.split(
        '-')[-1] for ii in ''.join([ii for ii in x.stem.split('_') if 'P1' in ii]) if (is_int(ii) or ii=='.')])))

    baselineopt = []
    ampopt = []
    tauopt = []
    delayopt = []
    # files = files[:1]

    for i, f in enumerate(files):
        header, data = read(f)

        data_array = np.array(data)

        data_dict = {
            'param': data_array[:, 0],
            'echo': np.abs(data_array[:, 1] + 1j * data_array[:, 2]),
        }

        x = data_dict['param']
        add = ''

        dat = data_dict['echo']

        if savgol:
            dat = savgol_filter(dat, 2 * (len(x) // 20) + 1, 3)
            add += 'savgol_'

        snrpart = x > np.max(x) - (np.max(x) - np.min(x)) / 10
        snrpart += x < np.min(x) + (np.max(x) - np.min(x)) / 10
        RMS = np.sqrt(np.mean(dat[snrpart]))
        peak = np.max(dat)
        # ax.plot([x[np.where(np.diff(snrpart)==True)[0][0]], x[np.where(np.diff(snrpart)==True)[0][0]]])
        # dat /= 5e-11
        # dat *= -1
        # dat -= np.min(dat)
        x *= 1e3
        mx = min(x)
        x -= mx
        c = 1
        popt, pcov = cf(exp, x, dat, p0=[np.max(dat), np.max(dat), 2.5])
        smoothx = np.linspace(np.min(x), np.max(x), 1000)
        line = ax.plot(x + mx, dat + i * c,
                       label=f"{float(''.join([ii for ii in ''.join([ii.split('-')[-1] for ii in f.stem.split('_') if 'P1' in ii]) if (is_int(ii) or ii=='.')]))} ms")
        ax.plot(smoothx + mx, exp(smoothx, *popt) +
                i * c, c=line[0].get_color(), ls='--')
        baselineopt.append(popt[0])
        ampopt.append(popt[1])
        tauopt.append(popt[2])
        delayopt.append(float(''.join([ii for ii in ''.join(
            [ii.split('-')[-1] for ii in f.stem.split('_') if 'P1' in ii]) if (is_int(ii) or ii==".")])))

    savename = P(filename).parent.joinpath(add + 'PP.png')

    handles, labels = plt.gca().get_legend_handles_labels()
    handles.reverse()
    labels.reverse()
    ax.legend([i for i in handles], [i for i in labels], markerfirst=True,
              handlelength=1, handletextpad=0.4, labelspacing=0.2,)
    ax.set_ylabel('P2 intensity (arb. u)')
    # ax.set_yticks([])
    ax.set_xlabel('Time (ms)')
    ax.set_title('Pump-probe')
    
    pfig, pax = plt.subplots(nrows=2, sharex=True)
    # popt, pcov = cf(exp, delayopt, ampopt)
    smoothx = np.linspace(np.min(delayopt), np.max(delayopt), 1000)
    pax[0].scatter(delayopt, tauopt, c='r', label=r'$\tau$')
    pax[0].axhline(np.mean(tauopt), c='r', alpha=0.5, label=f'{np.mean(tauopt):.2f} ms')
    pax[1].scatter(delayopt, ampopt, c='k', label='A')
    pax[1].plot(smoothx, exp(smoothx, *popt), c='k', label=f'{popt[-1]:.2f} ms', alpha=0.5)
    # pax.scatter(delayopt, baselineopt, c='blue', label='C')
    pfig.supxlabel('P2 length (ms)')
    pfig.supylabel('Fit value')
    pfig.suptitle(r'Fits vs. P2 for $f(t)=C + A e^{-t/\tau}$')
    pax[1].legend()
    pax[0].legend()

    # for s in ['top', 'right']:
    #     for a in [ax, pax]:
    #         a.spines[s].set_visible(False)

    plt.tight_layout()
    fig.savefig(savename, dpi=300)
    pfig.savefig(P(savename).parent.joinpath(
        P(savename).stem + '_trackfits.png'), dpi=300)


if __name__ == "__main__":
    f = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/8/23/M07_noSample_PP_P1-10m_000.dat'
    process(f)
    plt.show()
