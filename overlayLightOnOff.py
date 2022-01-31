import os
import sys
import PIL
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
from scipy.integrate import cumtrapz, trapz

from baselineSubtract import subtract
from makeAbsDisp import make
from readDataFile import read

plt.style.use('science')
# plt.rcParams.update({'font.family':'sans-serif'})
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'


def main(targ="./", makeAbs=True, keyw='Light'):
    if P(targ).is_file():
        targ = str(P(targ).parent)

    if makeAbs:
        make(
            targ=targ,
            keyw=keyw,
            file_suffix='rephased.dat',
            numerical_keyw=False,
            field=0,
            center=False,
            center_sect=1000
        )
    compare(targ=targ, keyword=keyw)
    # compare(targ=targ, keyword=keyw, normalize=True)
    # compare(targ=targ, keyword=keyw, integral=True)


def compare(targ='./', keyword='Light', normalize=False, integral=False):
    keyword = keyword.lower()

    if P(targ).is_file():
        targ = str(P(targ).parent)

    filelist = [
        ii for ii in P(targ).iterdir()

        if (ii.name.startswith('dispersion') or ii.name.startswith('absorption')) and ii.name.endswith('_exp.txt')
    ]

    disp_add = False
    abs_add = False

    fig, ax = plt.subplots()
   
    filelist.sort()
    for file in filelist:
        legend = ' '.join([
            ii.lower() for ii in P(file).stem.split('_') if
            ('absorption' in ii or 'dispersion' in ii or keyword in ii.lower())
        ]).replace('light','laser ').replace(keyword, '').replace('absorption', r"$\frac{d\chi''}{dB}$"
                ).replace('dispersion', r"$\frac{d\chi'}{dB}$")
        header, data = read(file)

        # legend = legend[:-len('Sweep')]

        # data[:, 1] = subtract(data[:, 1])

        int_add = ""

        if 'on' in legend:
            pc = '#00A7CA'
            sty = '--'
            # sty = '-'
        elif 'off' in legend:
            pc = 'black'
            sty = '-'

        lw = 1.25

        if integral:
            if r"chi''" in legend:
                ax.plot(data[:-1, 0], cumtrapz(data[:, 1]) /
                        np.max(cumtrapz(data[:, 1])), label=legend, c=pc, linestyle=sty, lw=lw)
                int_add += "_int"
        else:
            if normalize:
                data[:, 1] /= np.max(np.abs(data[:, 1]))
            # data[:, 1] /= np.abs(np.min(data[:, 1]))
                # data[:, 1] /= np.max(data[:, 1])

            if r"chi''" in legend:
                ax.plot(data[:, 0], data[:, 1], label=legend, c=pc, linestyle=sty, lw=lw)
                spins = trapz(cumtrapz(data[:, 1]))
                data[:, 1] += 1

                print(f'{file.stem} spins {abs(spins):.2e}')

            if r"\chi'" in legend:
                data[:, 1] -= 1

                # ax.plot(data[:, 0], data[:, 1], label=legend)

    ax.legend()
    title = 'Light-activated spectral narrowing'
    # title = 'Dipolar broadening at 87 K'

    if normalize:
        title += ' (normalized to max)'
    # ax.set_title(title)
    ax.set_xlabel('Field (T)')
    ax.set_ylabel('Signal (arb. u)')
    ax.set_yticklabels([])
    # ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    fig.savefig(P(targ).joinpath('compared' + int_add + '.png'), dpi=200)
    fig.savefig(P(targ).joinpath('compared' + int_add + '.tif'), dpi=200)


if __name__ == "__main__":
    targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/1/27/537/stable temp 293.7'
    main(targ=targ, makeAbs=True, keyw='Light')
    plt.show()
