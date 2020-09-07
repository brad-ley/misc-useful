import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.append('/Users/Brad/Documents/Research/code/python/misc-useful')
from makeAbsDisp import makeAbsDisp
from readDataFile import read


def compare(targ='./'):
    if not targ.endswith('/'):
        targ += '/'
    filelist = [
        targ + ii for ii in os.listdir(targ)
        if ii.startswith('dispersion') or ii.startswith('absorption')
    ]

    disp_add = 0
    abs_add = 0

    for file in filelist:
        legend = ' '.join([ch[:-5].split('/')[-1].lower() if 'light' in ch 
            else ch.split('/')[-1] for ch in [
            ii.title() for ii in file.split('_')
            if ('absorption' in ii or 'dispersion' in ii or 'Light' in ii)
        ]])
        header, data = read(file)
        plt.figure('Comparison')
        
        if (disp_add == 0 or abs_add == 0):
            if 'Dispersion' in legend:
                disp_add = np.max(data[:, 1]) / 2
            elif 'Absorption':
                abs_add = np.min(data[:, 1]) / 2
        if 'Dispersion' in legend:
            data[:, 1] += disp_add
        elif 'Absorption':
            data[:, 1] += abs_add
        plt.plot(data[:, 0], data[:, 1], label=legend)

    plt.legend()
    plt.title('Light on/off comparison')
    plt.xlabel('Field (T)')
    plt.ylabel('Signal (arb. u)')
    plt.yticks([])
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    plt.savefig(targ + 'compared.png')
    # plt.show()


if __name__ == "__main__":
    targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2020/09/2020-09-05_E108Q_cwEPR'
    makeAbsDisp(targ=targ,keyw='Light', numerical_keyw=False)
    compare(targ=targ)
