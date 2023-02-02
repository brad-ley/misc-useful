import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib import rc

from readDataFile import read

plt.style.use(['science'])
rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['xtick.major.size'] = 5
plt.rcParams['xtick.major.width'] = 1
plt.rcParams['xtick.minor.size'] = 2
plt.rcParams['xtick.minor.width'] = 1
plt.rcParams['ytick.major.size'] = 5
plt.rcParams['ytick.major.width'] = 1
plt.rcParams['ytick.minor.size'] = 2
plt.rcParams['ytick.minor.width'] = 1
plt.rcParams['lines.linewidth'] = 2


def main(filename):
    header, data = read(filename, delimiter='\t')
    fig, ax = plt.subplots()
    ax.plot(data[:, 1] * 1e-3, data[:, 0] * 1e3)
    ax.set_ylabel('mJ')
    ax.set_xlabel('Time (s)')
    # ax.text(0.1, 0.6, '$I_{d}=135$ mA', transform=ax.transAxes)
    # ax.text(0.55, 0.25, '$I_{d}=140$ mA', transform=ax.transAxes)
    fig.savefig(P(filename).parent.joinpath(
        P(filename).stem + '_fig.png'), dpi=400)


def extractAvgs(filename):
    header, data = read(filename, delimiter='\t')
    x = data[:, 1] * 1e-3
    y = data[:, 0] * 1e3
    z = zip(x, y)
    z = sorted(z, key=lambda x: x[0])
    x, y = zip(*z)
    x = np.array(x)
    y = np.array(y)
    fig, ax = plt.subplots()
    steps = np.where(np.diff(y) > 0.25 * np.mean(y[:20]))
    start = steps[0][0]
    tenSpoints = np.argmin(np.abs(x - 10.3))
    tenS = x[tenSpoints]
    avgs = [0] * (int(np.max(x) / tenS))
    currents = np.linspace(135, 135 + (len(avgs) - 1) * 5, len(avgs))
    outstr = f'{"Dcurr (mA)":<10}|{"Power (mJ)":<10}\n'
    outstr += '-' * (len(outstr) - 1) + '\n'

    for i, _ in enumerate(avgs):
        if start + tenSpoints * i > len(y):
            avgs[i] = np.mean(y[start + tenSpoints * (i - 1):])
        else:
            avgs[i] = np.mean(
                y[start + tenSpoints * (i - 1):start + tenSpoints * i])
        ax.axvline(x[start + tenSpoints * (i - 1)], c='k', ls='--', alpha=0.2)
        outstr += f'{int(currents[i]):>10}|{avgs[i]:>10.3f}\n'
    ax.plot(x, y)
    ax.plot(x[:-1], np.diff(y))
    ax.set_ylabel('Power (mJ)')
    ax.set_xlabel('Time (s)')
    fig.savefig(P(filename).parent.joinpath(
        P(filename).stem + '_fig.png'), dpi=400)
    f, a = plt.subplots()
    a.scatter(currents, avgs)
    a.set_ylabel('Power (mJ)')
    a.set_xlabel('Current (mA)')
    f.savefig(P(filename).parent.joinpath(
        P(filename).stem + '_mJvmA_fig.png'), dpi=400)
    P(filename).parent.joinpath(
        P(filename).stem + '_processed.txt').write_text(outstr)


def rescale(direct, slide):
    directd = np.loadtxt(direct, delimiter='|', skiprows=2)
    slided = np.loadtxt(slide, delimiter='|', skiprows=2)
    dy = directd[:, 1]
    sy = slided[:, 1]
    scale = dy / sy[:len(dy)]
    scale = dy[-1] / sy[len(dy)-1]
    # print(dy, sy[:len(dy)], scale, sep='\n')
    truepower = sy * np.mean(scale)
    fig, ax = plt.subplots()
    ax.scatter(slided[:, 0], truepower)
    ax.set_ylabel('Power (mJ)')
    ax.set_xlabel('Current (mA)')
    fig.savefig(P(slide).parent.joinpath(
        P(slide).stem + '_rescaled.png'), dpi=600)
    outstr = f'{"Dcurr (mA)":<10}|{"Power (mJ)":<10}\n'
    outstr += '-' * (len(outstr) - 1) + '\n'

    for i, _ in enumerate(truepower):
        outstr += f'{slided[i, 0]:>10}|{truepower[i]:>10.3f}\n'
    P(slide).parent.joinpath(P(slide).stem + '_rescaled.txt').write_text(outstr)


if __name__ == "__main__":
    filename = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/2/Viron laser power/DATA05.CSV'
    # main(filename)
    # files = [ii for ii in P(filename).parent.iterdir() if ii.name.endswith('.CSV')]
    # for f in files:
    #     extractAvgs(f)
    rescale('/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/2/Viron laser power/DATA04_processed.txt',
            '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/2/Viron laser power/DATA05_processed.txt')
    # plt.show()
