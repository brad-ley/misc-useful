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

if __name__ == "__main__":
    plt.style.use(['science'])
    # rc('text.latex', preamble=r'\usepackage{cmbright}')
    # plt.rcParams['font.family'] = 'sans-serif'
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
    # return (3 * np.cos(phi)**2 - 1) * np.sin(phi)

    return (3 * np.cos(phi)**2 - 1)


def gaussian(x, mu, wid):
    return 1 / (wid * np.sqrt(2 * pi)) * np.exp(-1 / 2 * ((x - mu) / wid)**2)


def exp(x, a, c, x0):
    return a + c * np.exp(-x / x0)


def strexp(x, a, c, x0, d):
    return a + c * np.exp(-(x / x0)**d)


n = int(5e3)
t_step = 0.5e-9
t_corr = 19e-9  # start with t_corr measured from experiment Shiny did
lw = 12.6e6  # linewidth of 0.45 mT -> 12 MHz
t_total = 16 / lw
time = np.arange(0, t_total, step=t_step)


def main():
    r = np.abs(np.random.normal(2.6e-9, 0.25e-9, n))
    # tracks if spins are alike or anti-alike
    parity = np.sign(np.random.rand(n) - 0.5)
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

    def to_cartesian(spherical):
        return np.array([
            spherical[0] * np.cos(spherical[1]) * np.sin(spherical[2]),
            spherical[0] * np.sin(spherical[1]) * np.sin(spherical[2]),
            spherical[0] * np.cos(spherical[2])
        ])

    def to_spherical(cartesian):
        r = np.linalg.norm(cartesian)

        return np.array([
            r,
            np.arctan2(cartesian[1], cartesian[0]),
            np.arccos(cartesian[2] / r)
        ])

    cartesian_positions = np.array([to_cartesian(ii) for ii in positions])

    d_ang = np.random.normal(t_step / t_corr, t_step / t_corr / 4,
                             n) * np.sign(np.random.rand(n) - 0.5)
    k = [
        np.array([np.random.rand(),
                  np.random.rand(),
                  np.random.rand()]) for ii in cartesian_positions
    ]
    k = [ii / np.linalg.norm(ii) for ii in k]

    def R(theta, k):
        kx, ky, kz = k[0], k[1], k[2]
        K = np.array([[0, -kz, ky], [kz, 0, -kx], [-ky, kx, 0]])

        return np.identity(3) + np.sin(theta) * K + (
            1 - np.cos(theta)) * np.linalg.matrix_power(K, 2)
    
    def update(frame):
        nonlocal positions, couplings_time, cartesian_positions, k

        # positions = [
        #     [
        #         pos[0] + r[i] * 1 / 100 * np.random.normal(1, 1 / 4), # vibration
        #         pos[1] + d_theta[i] * np.random.normal(1, 1 / 4), # rotation by theta around equator
        #         pos[2] + d_phi[i] * np.random.normal(1, 1 / 4) # rotation by phi around polar angle
        #         # pos[0], pos[1] + d_theta[i],
        #         # pos[2] + d_phi[i],
        #     ] for i, pos in enumerate(positions)
        # ]

        # couplings_time[frame, :] = [
        #     f(pos[0]) * ang(pos[2]) for pos in positions
        # ]

        # dd_ang = 1 / 100 * \
        dd_ang = 1 / 1 * \
            np.random.normal(t_step / t_corr, t_step / t_corr,
                             n) * np.sign(np.random.rand(n) - 0.5)
        k = [
            ii + t_step / t_corr * 
            np.random.rand(3) for ii in k
        ]  # add slight variation to k
        k = [ii / np.linalg.norm(ii) for ii in k]

        cartesian_positions = [
            R(d_ang[ind] + dd_ang[ind], k[ind]).dot(p)
            for ind, p in enumerate(cartesian_positions)
        ]

        couplings_time[frame, :] = [
            parity[i] * f(np.linalg.norm(c)) *
            ang(np.arccos(c[2] / np.linalg.norm(c)))
            for i, c in enumerate(cartesian_positions)
        ]

    for i in trange(len(time)):
        # couplings_time = update(ii)
        update(i)

    np.savetxt(
        '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/couplings.txt',
        couplings_time)


def makegif(filename, runcalc=False, ani=True):
    if runcalc:
        main()
    else:
        if not P(filename).is_file():
            main()

    couplings_time = np.loadtxt(filename)

    # fig3, ax3 = plt.subplots(figsize=(8, 6))
    fig3, ax3 = plt.subplots(layout='constrained')
    # ax3[0].hist(couplings_time[:, 0]/1e6, bins=bins, label=f"{time[1]*1e9:.2f} ns")
    # t_ind = np.where(time >= t_corr)[0][0]
    # ax3[1].hist(np.mean(couplings_time[:, :t_ind], axis=1)/1e6, bins=bins, label=f"{t_corr:.2f} ns")
    # ax3[2].hist(np.mean(couplings_time[:, :], axis=1)/1e6, bins=bins, label=f"{time[-1]*1e9:.2f} ns")
    bins = np.linspace(-1 / 2 * np.max(np.abs(couplings_time[0, :] / 1e6)),
                       np.max(1 / 2 * np.abs(couplings_time[0, :] / 1e6)), 250)
    couplings_avg = [
        np.mean(couplings_time[:idx + 1, :], axis=0) / 1e6
        for idx, ii in enumerate(couplings_time)
    ]

    def plot(frame):
        ax3.clear()
        ax3.text(0.7,
                 0.85,
                 f"{time[frame]*1e9:.1f} ns",
                 transform=ax3.transAxes)
        ax3.set_xlabel('Coupling (MHz)')
        ax3.set_ylabel('Intensity (arb. u)')
        ax3.hist(couplings_avg[frame], bins=bins)

    if ani:
        ani = animation.FuncAnimation(
            fig=fig3,
            func=plot,
            frames=range(0, len(time),
                         int(len(time) / 250)),
            interval=100,
            repeat=True,
            repeat_delay=1000,
        )
    else:
        ani = None

    # fig, ax = plt.subplots(figsize=(8, 6), layout='constrained')
    fig, ax = plt.subplots(layout='constrained')
    com = np.zeros(len(time))
    c1 = np.zeros(len(time))

    # okay so I want to take the mean along the time axis and then rms then the mean along the particle number axis

    for frame, t in enumerate(time):
        c = couplings_time[:frame + 1, :] / 1e6
        com[frame] = np.sqrt(np.mean(np.mean(c, axis=0)**2))
        c1[frame] = np.mean(c[:, 0], axis=0)

    # ax.plot(time * 1e9, c1, label='averaged')
    # ax.plot(time * 1e9, couplings_time[:, 0] / 1e6, label='raw coupling')
    popt, pcov = curve_fit(exp, time * 1e9, com)

    ax.plot(time * 1e9, com, label='RMS value', c='k')
    ax.plot(time * 1e9,
            exp(time * 1e9, *popt),
            label=rf'Fit: $\tau={popt[-1]:.1f}\,$ns',
            ls='--',
            c='r')

    T2 = 7e-9
    ax.axvline(T2 * 1e9,
               label=rf'$T_2\approx {T2 * 1e9}\,$ns',
               color='k',
               alpha=0.3)
    print(f'Observing at {com[time >= T2][0] / np.max(com) * 100:.1f}% of max')

    # popt, pcov = curve_fit(exp, time, com, p0=[0, 1, 3e-9])
    # ax.plot(time * 1e9, exp(time, *popt), label=fr'Fit ($\tau={popt[-1]*1e9:.1f}$ ns)')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Coupling (MHz)')
    ax.legend()
    fig.savefig(
        '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/coupling_RMS.png',
        dpi=400)

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
    cbar.set_label('Coupling (MHz)')
    ax.set_ylabel(r'$\theta_d$')
    ax.set_xlabel('r (nm)')
    plt.savefig(P(
        '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/'
    ).joinpath('coupling_strength.png'),)
                # dpi=400)


if __name__ == "__main__":
    ani = makegif(
        '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/couplings.txt',
        runcalc=True,
        # runcalc=False,
        ani=True)
    # ani=False)

    try:
        ani.save(
            '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Code/dipolar averaging/pake_in_time.mp4',
            dpi=300,
            progress_callback=lambda i, n: print(f'Saving frame {i}/{n}',
                                                 end='\r'))
    except AttributeError:
        pass
    # plt.show()
