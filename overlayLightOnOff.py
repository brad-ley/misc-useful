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
    targ = '/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/06/09/check movement'
    makeAbs = True

    if makeAbs:
        make(
            targ=targ,
            keyw='Light',
            file_suffix='rephased.dat',
            numerical_keyw=False,
            field=8.62
        )
    compare(targ=targ)


def compare(targ='./'):
    if not targ.endswith('/'):
        targ += '/'

    filelist = [
        targ + ii for ii in os.listdir(targ)
        if ii.startswith('dispersion') or ii.startswith('absorption')
    ]

    disp_add = False
    abs_add = False

    for file in filelist:
        legend = ' '.join([
            ii.title() for ii in P(file).stem.split('_') if
            ('absorption' in ii or 'dispersion' in ii or 'light' in ii.lower())
        ]).replace('light', '').replace('Absorption', 'Abs').replace('Dispersion', 'Disp')
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

        plt.plot(data[:, 0], data[:, 1], label=legend)

    plt.legend()
    plt.title('Light on/off comparison')
    plt.xlabel('Field (T)')
    plt.ylabel('Signal (arb. u)')
    plt.yticks([])
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    plt.savefig(targ + 'compared.png', dpi=200)
    plt.show()


if __name__ == "__main__":
    main()
