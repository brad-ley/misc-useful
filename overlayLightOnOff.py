import os
import sys
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL
from scipy.integrate import cumtrapz, trapz

# from baselineSubtract import subtract
from makeAbsDisp import make
from readDataFile import read

from matplotlib import rc
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


def main(targ="./", makeAbs=True, keyw='Light', field=0):
    if P(targ).is_file():
        targ = str(P(targ).parent)

    # field = 8.62

    if makeAbs:
        make(
            targ=targ,
            keyw=keyw,
            file_suffix='rephased.dat',
            numerical_keyw=False,
            field=field,
            center=False,
            center_sect=10
        )
    # compare(targ=targ, keyword=keyw, field=field, B_0=-1)
    compare(targ=targ, keyword=keyw, field=field, B_0=-1, normalize=False,)


def compare(targ='./', keyword='Light', field=0, normalize=False, integral=False, B_0=-1):
    keyword = keyword.lower()

    if P(targ).is_file():
        targ = str(P(targ).parent)

    filelist = [
        ii for ii in P(targ).iterdir()

        if (ii.name.startswith('dispersion') or ii.name.startswith('absorption')) and ii.name.endswith('_exp.txt')
    ]
    filelist.sort()
    # filelist.reverse()

    disp_add = False
    abs_add = False

    # fig, ax = plt.subplots(figsize=(8,6))
    fig, ax = plt.subplots()

    scale = 0
    lines = {}
    outlist = []
    
    for i, f in enumerate(filelist):
        legend = ' '.join([
            ii.lower() for ii in P(f).stem.split('_') if
            ('absorption' in ii or 'dispersion' in ii or keyword in ii.lower())
        ]).replace('light', 'Laser ').replace(keyword, '').replace('absorption', r"$\frac{d\chi''}{dB}$"
                                                                   ).replace('dispersion', r"$\frac{d\chi'}{dB}$")
        header, data = read(f)

        # legend = legend[:-len('Sweep')]

        # data[:, 1] = subtract(data[:, 1])

        int_add = ""

        if 'off' in legend:
            pc = 'black'
            sty = '-'
        elif 'on' in legend:
            pc = '#00A7CA'
            sty = '--'
            # sty = '-'

        lw = 2

        if integral:
            d = cumtrapz(data[:, 1], x=data[:, 0])

            if r"chi''" in legend:

                legend = " ".join(legend.split(" ")[1:])
                lines[f.stem + ' data'] = [data[:-1, 0], d]
                try:
                    lines[f.stem + ' color'] = pc
                    lines[f.stem + ' style'] = sty
                    lines[f.stem + ' name'] = legend
                except:
                    pass
                outlist.append(f.stem)

                if np.max(d) > scale:
                    scale = np.max(d)

                # legend = " ".join(legend.split(" ")[1:])
                # ax.plot(data[:-1, 0], d,
                #         label=legend, c=pc, linestyle=sty, lw=lw)
                # ax.plot(data[:-1, 0], d / np.max(d),
                #         c=pc, linestyle=sty, lw=lw)
                int_add += "_int"
        else:
            if normalize:
                """
                For normalizing by double integral
                """
                # data[:, 1] -= trapz(data[:,1], x=data[:,0])
                # d = trapz(cumtrapz(data[:, 1], x=data[:, 0]), x=data[1:, 0])
                # data[:, 1] /= d
                """
                For normalizing to max
                """
                data[:, 1] -= trapz(data[:, 1], x=data[:, 0])
                data[:, 1] /= np.max(data[:, 1])

            if r"chi''" in legend:
                legend = " ".join(legend.split(" ")[1:])
                lines[f.stem + ' data'] = [data[:, 0], data[:, 1]]
                try:
                    lines[f.stem + ' color'] = pc
                    lines[f.stem + ' style'] = sty
                    lines[f.stem + ' name'] = legend
                except:
                    pass
                outlist.append(f.stem)

                if np.max(data[:, 1]) > scale:
                    scale = np.max(data[:, 1])
                    # scale = 0.0001604264455812626

                # ax.plot(data[:, 0], -1 * data[:, 1] / scale,
                #         label=legend, c=pc, linestyle=sty, lw=lw)
                spins = trapz(cumtrapz(data[:, 1]))

                print(f'{f.stem} spins {abs(spins):.2e}')

            if r"\chi'" in legend:
                data[:, 1] -= 1

                # ax.plot(data[:, 0], data[:, 1], label=legend)

    outlist.reverse()
    for i, f in enumerate(outlist):
        try:
            ax.plot(lines[f + ' data'][0], lines[f + ' data'][1] / scale, label=lines[f +
                                                                                          ' name'], c=lines[f + ' color'], linestyle=lines[f + ' style'], lw=lw)
        except:
            ax.plot(lines[f + ' data'][0], lines[f + ' data']
                    [1] / scale, label="".join([ii.strip('sweep') for ii in f.split("_") if ii != 'absorption' and ii != 'exp']), lw=lw)

    if B_0 != -1:
        ax.axvline(x=field + B_0, c='gray',
                   alpha=0.5, lw=lw, label=r'$B_0$')
    # T406C, E537C are mutations
    T = 294
    mutant = 'DL T406C-E537C'
    # ax.legend(loc=(.55,.8),markerfirst=True,handlelength=1,handletextpad=0.4,labelspacing=0.2,)
    ax.legend(loc='upper right',markerfirst=False,handlelength=1,handletextpad=0.4,labelspacing=0.2,)
    ax.text(0.05, 0.11, f'$T={T}$ K\n{mutant}',
            horizontalalignment='left', verticalalignment='center', transform=ax.transAxes)
    title = 'Light-activated spectral narrowing'
    # title = 'Dipolar broadening at 87 K'

    if normalize:
        title += ' (normalized to max)'
    # ax.set_title(title)
    ax.set_xlabel('Field (T)')
    ax.set_ylabel('cwEPR signal (arb. u)')
    ax.set_yticks([-1, 0, 1])
    ax.set_ylim([-1.1, 1.1])
    # ax.set_yticklabels([])
    # ax.set_xticks([8.620,8.622, 8.624, 8.626, 8.628])
    # ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    fig.savefig(P(targ).joinpath('compared' + int_add + '.png'), transparent=True, dpi=500)
    # fig.savefig(P(targ).joinpath('compared' + int_add + '.tif'), dpi=300)


if __name__ == "__main__":
    targ = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2022/1/20'
    main(targ=targ, makeAbs=True, keyw='Light', field=8.62)
    # main(targ=targ, makeAbs=True, keyw='sweep', field=8.62)
    plt.show()
