import os
import sys
from pathlib import Path as P
from pathlib import PurePath as PP

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
            field=8.62,
            center=True,
            center_sect=20
        )
    compare(targ=targ, keyword=keyw)


def compare(targ='./',keyword='Light',normalize=False):
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

        data[:, 1] /= np.max(np.abs(data[:, 1]))

        if r"$\chi''$" in legend:
            data[:, 1] += 1
        if r"$\chi'$" in legend:
            data[:, 1] -= 1

        print(disp_add, abs_add)

        ax.plot(data[:, 0], data[:, 1], label=legend)

    ax.legend()
    ax.set_title('Light on/off comparison')
    ax.set_xlabel('Field (T)')
    ax.set_ylabel('Signal (arb. u)')
    ax.set_yticks([])
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.savefig(P(targ).joinpath('compared.png'), dpi=200)
    plt.show()


if __name__ == "__main__":
    targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/09/23/537_old/compare single and double'
    main(targ=targ)
