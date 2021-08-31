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
    targ = '/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/07/Gd data for Cocoa/selected for poster'
    if P(targ).is_file():
        targ = str(P(targ).parent)
    makeAbs = True

    keyw = 'keyw'
    if makeAbs:
        make(
            targ=targ,
            keyw=keyw,
            file_suffix='rephased.dat',
            numerical_keyw=False,
            field=8.62,
            center=True
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

    for file in filelist:
        legend = ' '.join([
            ii.title() for ii in P(file).stem.split('_') if
            ('absorption' in ii or 'dispersion' in ii or keyword in ii.lower())
        ]).replace(keyword, '').replace('Absorption', 'Abs').replace('Dispersion', 'Disp')
        header, data = read(file)
        plt.figure('Comparison')

        # data[:, 1] = subtract(data[:, 1])

        if not disp_add:
            if 'Disp' in legend:
                disp_add = np.max(data[:, 1])
        if not abs_add:
            if 'Abs' in legend:
                abs_add = np.min(data[:, 1])

        if 'Disp' in legend:
            data[:, 1] += disp_add
        elif 'Abs' in legend:
            data[:, 1] += abs_add

        plt.plot(data[:, 0], data[:, 1]/np.max(np.abs(data[:, 1])), label=legend)

    plt.legend()
    plt.title('Light on/off comparison')
    plt.xlabel('Field (T)')
    plt.ylabel('Signal (arb. u)')
    plt.yticks([])
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    plt.savefig(P(targ).joinpath('compared.png'), dpi=200)
    plt.show()


if __name__ == "__main__":
    main()
