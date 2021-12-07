import os
import sys
from pathlib import Path as P
from pathlib import PurePath as PP
from scipy.integrate import trapz, cumtrapz

import matplotlib.pyplot as plt
import numpy as np

from baselineSubtract import subtract
from makeAbsDisp import make
from readDataFile import read


def main(targ="./", makeAbs=True):
    if P(targ).is_file():
        targ = str(P(targ).parent)
    makeAbs = True

    keyw = 'Light'

    if makeAbs:
        make(
            targ=targ,
            keyw=keyw,
            file_suffix='rephased.dat',
            numerical_keyw=False,
            field=0,
            center=False,
            center_sect=20
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

    for file in filelist:
        legend = ' '.join([
            ii.title() for ii in P(file).stem.split('_') if
            ('absorption' in ii or 'dispersion' in ii or keyword in ii.lower())
        ]).replace(keyword, '').replace('Absorption', r"$\chi''$").replace('Dispersion', r"$\chi'$")
        header, data = read(file)

        # data[:, 1] = subtract(data[:, 1])

        int_add = ""
        if integral:
            if r"$\chi''$" in legend:
                ax.plot(data[:-1, 0], cumtrapz(data[:, 1]) / np.max(cumtrapz(data[:, 1])), label=legend)
                int_add += "_int" 
        else:
            if normalize:
                data[:, 1] /= np.max(np.abs(data[:, 1]))
            # data[:, 1] /= np.abs(np.min(data[:, 1]))
                # data[:, 1] /= np.max(data[:, 1])

            if r"$\chi''$" in legend:
                ax.plot(data[:, 0], data[:, 1], label=legend)
                spins = trapz(cumtrapz(data[:, 1]))
                data[:, 1] += 1

                print(f'{file.stem} spins {abs(spins):.2e}')

            if r"$\chi'$" in legend:
                data[:, 1] -= 1

            # ax.plot(data[:, 0], data[:, 1], label=legend)

    ax.legend()
    title = 'Light on/off comparison'
    if normalize:
        title += ' (normalized to max)'
    ax.set_title(title)
    ax.set_xlabel('Field (T)')
    ax.set_ylabel('Signal (arb. u)')
    ax.set_yticks([])
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.savefig(P(targ).joinpath('compared' + int_add + '.png'), dpi=200)
    plt.show()


if __name__ == "__main__":
    targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/12/7/30%'
    main(targ=targ)
