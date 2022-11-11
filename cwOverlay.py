import ast
import os
import PIL
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
from scipy.integrate import cumtrapz

from readDataFile import read
from makeAbsDisp import make

plt.style.use(['science'])
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


def overlay(targ, low=-1, high=-1):
    """overlay.
    :param targ: directory with 'absorption' files
    :param low: low field for plotting
    :param high: high field for plotting
    """
    if P(targ).is_file():
        targ = str(P(targ).parent)
    fs = [ii for ii in P(targ).iterdir() if ii.name.startswith(
        'absorption') and ii.name.endswith('_exp.txt')]
        # 'dispersion') and ii.name.endswith('_exp.txt')]
    fig, ax = plt.subplots()
    figtrapz, axtrapz = plt.subplots()
    fs.sort()
    # fs.reverse()
    # fs.insert(2, fs.pop(1))
    for i, f in enumerate(fs):
        h, d = read(str(f))
        d[:, 1] = d[:, 1] - np.average(d[:, 1]) # remove baseline
        if low == -1:
            if 'plotlow' in locals():
                if d[0, 0] < plotlow:
                    plotlow = d[0, 0]
            else:
                plotlow = d[0, 0]
        else:
            plotlow = low
        if high == -1:
            if 'plothigh' in locals():
                if d[-1, 0] > plothigh:
                    plothigh = d[-1, 0]
            else:
                plothigh = d[-1, 0]
        else:
            plothigh = high

        ### for generic plotting ###
        # legend = f"{f.name.split('_')[1]}"
        ############################
        ### for manuscript plotting ###
        print(f.name)
        if "513" in f.name.split('_')[1]:
            legend = 'Q513A DL'
            color = 'green'
            style = '-'
        elif "537" in f.name.split('_')[1] and "406" in f.name.split('_')[1]:
            legend = 'T406C-E537C'
            color = 'black'
            style = '--'
        elif "450" in f.name.split('_')[1]:
            legend = 'C450A DL'
            color ='red'
            style = ':'
        elif "528" in f.name.split('_')[1]:
            legend = '528'
            color ='green'
            style = '-'
        elif "537" in f.name.split('_')[1]:
            legend = '537'
            color ='red'
            style = ':'
        elif "LiqCrys" in f.name:
            legend='LiqCrys'
            color = 'red'
            style = ':'
        elif "OLD" in f.name:
            legend='Old'
            color='red'
            style='-'
        # else:
        #     legend = 'DL'
        #     color ='black'
        #     style = '--'
        # if False:
        #     pass
        elif 'NEW' in f.name:
            # legend = f"{f.name.split('_')[1]}"
            legend = 'New'
            color='black'
            style = '-'
        ############################
       
        lw=2
        # try:
        # # if True:
        #     scale = np.trapz(cumtrapz(d[np.where(plotlow < d[:, 0])[
        #                      0][0]:np.where(plothigh < d[:, 0])[0][0], 1]))
        #     ax.plot(d[:, 0], d[:, 1] / scale, label=legend, lw=lw, color=color, linestyle=style)
        #     axtrapz.plot(d[1:, 0], cumtrapz(d[:, 1]) / scale, label=legend)
        # except IndexError:
        if True:
            ax.plot(d[:, 0], d[:, 1] / np.max(d[:, 1]), label=legend, lw=lw, color=color, linestyle=style)
            low = d[np.argmax(d[:, 1]), 0]
            high = d[np.argmin(d[:, 1]), 0]
            p2p = np.abs(high - low)
            print(f"peak to peak of {p2p:.2e}")
            # ax.plot([low, high], [0, 0], color='black', alpha=0.5, ls='--')
            axtrapz.plot(d[1:, 0], cumtrapz(d[:, 1]) / np.max(cumtrapz(d[: 1])), label=legend)
        # except (UnboundLocalError, NameError):
        # if True:
        #     ax.plot(d[:, 0], d[:, 1] / np.max(d[:, 1]), label=legend, lw=lw)
        #     axtrapz.plot(d[1:, 0], cumtrapz(d[:, 1]) / np.max(cumtrapz(d[:, 1])), label=legend)
    

    ax.text(0.05, 0.11, '$T=$294 K\nSL T406C',
            horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    try:
        for a in [ax, axtrapz]:
            # a.set_xlim(right=8.6325)
            # a.set_yticklabels([])
            # a.set_yticks([-1,0,1])
            pf = 1.5e-3
            a.set_xlim([(high+low)/2-pf,(high+low)/2+pf])
            a.set_ylabel('cwEPR signal (arb. u)')
            a.set_xlabel('Field (T)')
            # a.spines['right'].set_visible(False)
            # a.spines['top'].set_visible(False)
            a.legend(markerfirst=True,handlelength=0.85,handletextpad=0.25,labelspacing=0.2)

        plt.tight_layout()
        fig.savefig(P(targ).joinpath('figure_comp.png'), dpi=300, transparent=True)
        fig.savefig(P(targ).joinpath('figure_comp.tif'), dpi=300)

    except UnboundLocalError:
        print("Need to create absorption files with makeAbsDisp.py first!")


def main():
    make(targ, keyw='sweep', field=8.62, numerical_keyw=False)
    overlay(targ)


if __name__ == "__main__":
    targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/10/27/comparing to old'
    main()
    # plt.show()
