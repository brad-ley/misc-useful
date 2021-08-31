import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np

from readDataFile import read

plt.rcParams.update({'font.size': 20})

targ = '/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/07/26'
fs = [ii for ii in P(targ).iterdir() if ii.stem.startswith('absorption')]

fig, ax = plt.subplots()

for f in fs:
    header, data = read(f)

    if 'Off' in f.stem:
        ax.plot(data[:, 0] + 8.57, data[:, 1], label='Dark', c='k', linewidth=2)

    if 'On' in f.stem:
        ax.plot(data[:, 0] + 8.57, data[:, 1],
                label='Lit', c='dodgerblue', linewidth=2)

ax.set_yticks([])
ax.set_ylabel('Signal (arb. u)')
ax.set_xlabel('Field (T)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.legend()

plt.tight_layout()
plt.savefig(P(targ).joinpath('dark-lit.png'), dpi=300)
