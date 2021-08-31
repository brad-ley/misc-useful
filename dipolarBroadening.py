import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumtrapz

from readDataFile import read


def main(targ='./'):
    if P(targ).is_file():
        targ = str(P(targ).parent)

    fig, ax = plt.subplots()

    for idx, f in enumerate([ii for ii in P(targ).iterdir() if ii.name.endswith('_exp.txt') and ii.name.startswith('absorption')]):
        header, data = read(str(f))

        # datout = cumtrapz(data[:, 1])
        # datout /= np.max(datout)

        # ax.plot(data[:-1, 0], datout, label=f.name)
        data[:, 1] -= data[0, 1]
        data[:, 1] /= np.abs(np.min(data[:, 1]))
        data[:, 1] /= np.max(data[:, 1])
        ax.plot(data[:, 0], data[: ,1], label=''.join([ii for ii in str(f).split('_') if 'sample' in ii]))
    plt.legend()

    plt.savefig(P(targ).joinpath('dipolar_compare.png'), dpi=300)

if __name__ == "__main__":
    main(targ='/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/07/06')
    plt.show()
