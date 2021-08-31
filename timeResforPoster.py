import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

from readDataFile import read


def exp(x, a, b, c):
    return a + b * np.exp(-x / c)


plt.rcParams.update({'font.size': 20})

f = '/Users/Brad/Downloads/dark light dark 3480_G 2-1.asc'
header, data = read(
    f, delimiter='\t', flipX=False)

t = data[:, 0]
signal = data[:, 1] / np.max(data)
filtered = savgol_filter(signal, 21, 2)

lightoff = 240

popt, pcov = curve_fit(exp, t[np.where(t > lightoff)[0][0]:], filtered[np.where(t > lightoff)[0][0]:], p0=[-0.5,1,40])

fig, ax = plt.subplots()

# ax.plot(t, signal, c='r')
ax.plot(t, filtered, c='b', linewidth=3, label='Data')
ax.plot(np.linspace(lightoff, np.max(t), 1000), exp(
    np.linspace(lightoff, np.max(t), 1000), *popt), c='r', linewidth=3, label='Fit')
ax.set_ylabel('Signal (arb. u)')
# ax.set_yticks([])
ax.set_xlabel('Time (s)')
ax.axvspan(90, lightoff, color='dodgerblue', alpha=0.2)
ax.text(150, -0.4, 'Light on', alpha=0.4, rotation=90)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.legend()
plt.tight_layout()
plt.savefig(P(f).parent.joinpath('timeDep.png'), dpi=300)
plt.show()
