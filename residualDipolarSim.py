import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from random import choices

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from matplotlib import cm, rc, ticker
from scipy.optimize import curve_fit
from tqdm import tqdm, trange

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

mu0 = 1.257e-6
muB = 9.27e-24
h = 6.63e-34
pi = np.pi


def f(r):
    # want frequency not angular frequency units

    return mu0 / (4 * pi) * muB**2 * 2**2 / h * 1 / r**3


def ang(phi):
    return (3 * np.cos(phi)**2 - 1) * np.sin(phi)
    # return (3 * np.cos(phi)**2 - 1)


def gaussian(x, mu, wid):
    return 1 / (wid * np.sqrt(2 * pi)) * np.exp(-1 / 2 * ((x - mu) / wid)**2)


def exp(x, a, c, x0):
    return a + c * np.exp(-x / x0)


n = int(1e4)
t_step = 1e-9  # start with 1 ns
t_corr = 19e-9  # start with t_corr measured from experiment Shiny did
t_total = 5 / 12.6e6  # linewidth of 0.45 mT -> 12 MHz
time = np.arange(0, t_total, step=t_step)


def main():
    r = np.sign(np.random.rand(n) - 0.5) * \
        np.abs(np.random.normal(2.e-9, 0.25e-9, n))
    # anywhere on equator with equal probability
    theta = np.random.rand(n) * 2 * pi
    pop = np.linspace(0, pi, 100)  # options along phi axis
    weights = np.sin(pop)  # probability of a given phi
    phi = choices(pop, weights, k=n)  # distribution of polar angles

    ff = f(r)
    """
    Time step simulation
    """

    couplings_time = np.zeros((len(time), n))

    positions = [[rr, theta[i], phi[i]] for i, rr in enumerate(r)]
    cartesian_positions = [[
        rr * np.cos(phi[i]), rr * np.sin(phi[i]) * np.cos(theta[i]),
        rr * np.sin(theta[i]) * np.sin(phi[i])
    ] for i, rr in enumerate(r)]

    d_phi = np.random.normal(t_step / t_corr, t_step / t_corr / 4,
                             n) * np.sign(np.random.rand(n) - 0.5)
    d_theta = np.random.normal(t_step / t_corr, t_step / t_corr / 4,
                             n) * np.sign(np.random.rand(n) - 0.5)
    # proportion_to_z = np.array(choices(pop, weights, k=n))  # distribution of polar angles
    # d_phi = np.cos(proportion_to_z) * d_ang

    def update(frame):
        nonlocal positions, couplings_time

        positions = [[
            pos[0], pos[1] + 
            d_theta[i] * np.random.normal(1, 1 / 4),
            pos[2] + d_phi[i] * np.random.normal(1, 1 / 4)
            # pos[0], pos[1] + d_theta[i],
            # pos[2] + d_phi[i],
        ] for i, pos in enumerate(positions)]

        couplings_time[frame, :] = [
            f(pos[0]) * ang(pos[2]) for pos in positions
        ]

        return couplings_time

    for ii in range(len(time)):
        couplings_time = update(ii)

    np.savetxt('/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/couplings.txt', couplings_time)


def makegif(filename, runcalc=False, ani=True):
    if runcalc:
        main()
    couplings_time = np.loadtxt(filename)

    fig3, ax3 = plt.subplots(figsize=(8, 6))
    # ax3[0].hist(couplings_time[:, 0]/1e6, bins=bins, label=f"{time[1]*1e9:.2f} ns")
    # t_ind = np.where(time >= t_corr)[0][0]
    # ax3[1].hist(np.mean(couplings_time[:, :t_ind], axis=1)/1e6, bins=bins, label=f"{t_corr:.2f} ns")
    # ax3[2].hist(np.mean(couplings_time[:, :], axis=1)/1e6, bins=bins, label=f"{time[-1]*1e9:.2f} ns")
    bins = np.linspace(-1 / 2 * np.max(np.abs(couplings_time[0, :] / 1e6)), np.max(
        1 / 2 * np.abs(couplings_time[0, :] / 1e6)), 250)

    def plot(frame):
        ax3.clear()
        ax3.hist(
            np.mean(couplings_time[:frame + 1, :], axis=0) / 1e6, bins=bins)
        ax3.text(0.85, 0.9, f"{time[frame]*1e9:.1f} ns",
                 transform=ax3.transAxes)
        ax3.set_xlabel('Coupling strength (MHz)')
        ax3.set_ylabel('Intensity (arb. u)')
        # 7193317444
        # 6147384954

    if ani:
        ani = animation.FuncAnimation(
            fig=fig3, func=plot, frames=len(time), interval=2.5, repeat=False)
    else:
        ani = None

    fig, ax = plt.subplots(figsize=(8, 6))
    com = np.zeros(len(time))
    c1 = np.zeros(len(time))

    # okay so I want to take the mean along the time axis and then rms then the mean along the particle number axis

    for frame, t in enumerate(time):
        c = couplings_time[:frame + 1, :] / 1e6
        com[frame] = np.sqrt(np.mean(np.mean(c, axis=0)**2))
        c1[frame] = np.mean(c[:, 0], axis=0)

    # ax.plot(time * 1e9, c1, label='averaged')
    # ax.plot(time * 1e9, couplings_time[:, 0] / 1e6, label='raw coupling')
    popt, pcov = curve_fit(exp, time*1e9, com)

    ax.plot(time * 1e9, com, label='COM')
    ax.plot(time*1e9, exp(time*1e9, *popt), label=r'Fit: $\tau=$' + f'{popt[-1]:.1f} ns')

    # popt, pcov = curve_fit(exp, time, com, p0=[0, 1, 3e-9])
    # ax.plot(time * 1e9, exp(time, *popt), label=fr'Fit ($\tau={popt[-1]*1e9:.1f}$ ns)')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('RMS Coupling strength (MHz)')
    ax.legend()
    fig.savefig('/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/coupling_RMS.png', dpi=400)

    return ani


def coupling_plot(ax=None):
    c_array = np.zeros((100, 100))
    x = np.linspace(2e-9, 6e-9, 100)
    y = np.linspace(0, pi, 100)

    for i, ii in enumerate(x):
        for k, kk in enumerate(y):
            c_array[k, i] = np.abs(f(ii) * ang(kk)) / 1e6

    x, y = np.meshgrid(x * 1e9, y)
    c = ax.contourf(x, y, c_array, locator=ticker.LogLocator())
    cbar = fig.colorbar(c)
    cbar.set_label('Coupling strength (MHz)')
    ax.set_ylabel(r'$\theta_d$')
    ax.set_xlabel('r (nm)')
    plt.savefig(P(
        '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/'
    ).joinpath('coupling_strength.png'),
        dpi=400)


if __name__ == "__main__":
    ani = makegif(
        '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/couplings.txt',
        runcalc=True,
        ani=True)
    try:
        ani.save('/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/pake_in_time.gif',
                 writer='imagemagick', fps=30)
    except AttributeError:
        pass
    # plt.show()
