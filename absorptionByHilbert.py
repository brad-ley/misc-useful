import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize, signal

from readDataFile import read

targ = '/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/06/03/Concentrated_AsLOV_cwEPR/Try 2'


def create(targ):
    files = [ii for ii in P(targ).iterdir() if ii.name.endswith(
        '_exp.txt') and ii.name.startswith('dispersion')]

    for f in files:
        outstr = ""
        header, data = read(f)
        data[:,1] = -1 * np.imag(signal.hilbert(data[:,1]))
        
        frac = 100
        deltaB = (data[-1, 0] - data[0, 0]) / len(data[:, 0])
        leftB = np.linspace(data[0,0] - (data[-1, 0] - data[0, 0])/frac, data[0,0], int(((data[-1, 0] - data[0, 0])/frac)//deltaB))
        rightB = np.linspace(data[-1,0] + (data[-1, 0] - data[0, 0])/frac, data[-1,0], int(((data[-1, 0] - data[0, 0])/frac)//deltaB))
        
        left_zeros = np.zeros_like(leftB)
        right_zeros = np.zeros_like(rightB)

        B = np.zeros(len(data[:, 0]) + len(leftB) + len(rightB))
        Data = np.zeros_like(B)

        B[:len(leftB)] = leftB
        B[len(leftB):len(leftB) + len(data[:,0])] = data[:,0]
        B[len(leftB) + len(data[:,0]):len(leftB) + len(data[:,0]) + len(rightB)] = rightB
        Data[:len(leftB)] = left_zeros
        Data[len(leftB):len(leftB) + len(data[:,1])] = data[:,1]
        Data[len(leftB) + len(data[:,1]):len(leftB) + len(data[:,1]) + len(rightB)] = right_zeros

        outdat = np.transpose(np.array([B,Data]))
        for index, row in enumerate(outdat):
            outstr += f"{row[0]}, {row[1]}\n"
        P(targ).joinpath(f.name.replace('dispersion', 'hilbert_abs')).write_text(outstr)


if __name__ == "__main__":
    create(targ)
