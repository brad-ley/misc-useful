import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.append('/Users/Brad/Documents/Research/code/python/misc-useful')
from makeAbsDisp import makeAbsDisp
from readDataFile import read


def compare(targ='./'):
    filelist = [
        ii for ii in os.listdir(targ)
        if ii.startswith('dispersion') or ii.startswith('absorption')
    ]

    for file in filelist:
        legend = ' '.join([ch[:-5].lower() if 'light' in ch else ch for ch in [
            ii.title() for ii in file.split('_')
            if ii == 'absorption' or ii == 'dispersion' or 'Light' in ii
        ]])
        header, data = read(file)
        plt.figure('Comparison')
        plt.plot(data[:, 0], data[:, 1], label=legend)

    plt.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    plt.savefig('compared.png')
    plt.show()


if __name__ == "__main__":
    # makeAbsDisp(keyw='Light', numerical_keyw=False)
    compare()
