import ast
import os
import sys
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib import rc

from readDataFile import read

sys.path.append('/Users/Brad/Documents/Research/code/python/rapidscan/')
from simulateRapidscan import Bloch

plt.style.use(['science'])
# rc('text.latex', preamble=r'\usepackage{cmbright}')
# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.size'] = 14
plt.rcParams['font.size'] = 20
# plt.rcParams['axes.linewidth'] = 1
plt.rcParams['axes.linewidth'] = 1.5
# plt.rcParams['xtick.major.size'] = 5
plt.rcParams['xtick.major.size'] = 6
# plt.rcParams['xtick.major.width'] = 1
plt.rcParams['xtick.major.width'] = 1.5
# plt.rcParams['xtick.minor.size'] = 2
plt.rcParams['xtick.minor.size'] = 3
plt.rcParams['xtick.minor.width'] = 1
# plt.rcParams['ytick.major.size'] = 5
plt.rcParams['ytick.major.size'] = 6
# plt.rcParams['ytick.major.width'] = 1
plt.rcParams['ytick.major.width'] = 1.5
# plt.rcParams['ytick.minor.size'] = 2
plt.rcParams['ytick.minor.size'] = 3
plt.rcParams['ytick.minor.width'] = 1
# plt.rcParams['lines.linewidth'] = 2
plt.rcParams['lines.linewidth'] = 3


def main():
    sig_x = np.array([[0, 1], [1, 0]])
    sig_y = np.array([[0, -1j], [1j, 0]])
    sig_z = np.array([[1, 0], [0, -1]])

    up = np.array([1, 0]).transpose()
    down = np.array([0, 1]).transpose()

    def length(vec):
        return np.sqrt(np.dot(vec, np.conjugate(vec)))

    def normalize(vec):
        return vec / length(vec)

    def H_zee(state, B):
        x = 1 / 2 * B * sig_z @ state

        if all(x == 0):
            return x

        if any(abs(normalize(x)) != abs(normalize(state))):
            print('Not an eigenstate.')

            return

        return x

    l = 1000
    sweepfield = np.linspace(0, 9, l)
    su = np.zeros(len(sweepfield))
    sd = np.zeros(len(sweepfield))

    for i, B in enumerate(sweepfield):
        retu = H_zee(up, B)
        retd = H_zee(down, B)

        if any(np.isnan(retu)):
            su[i] = 0
        else:
            su[i] += np.dot(retu, normalize(up))

        if any(np.isnan(retd)):
            sd[i] = 0
        else:
            sd[i] += np.dot(retd, normalize(down))
    fig, ax = plt.subplots(ncols=1, nrows=3, figsize=(
        # 6, 4), gridspec_kw={'height_ratios': [1, 1, 1]})
        6, 4), gridspec_kw={'height_ratios': [1, 1, 1]}, layout='constrained')

    # a0 = ax[0]
    a1 = ax[0]
    a2 = ax[1]
    a3 = ax[2]
    a2.sharex(a3)

    # a0.sharex(a1)
    # a2.sharex(a3)

    # ax.set_yticks([])

    for a in ax:
        a.set_yticklabels([])
    # a0.set_ylabel("Energy")
    # a0.set_xticklabels([])
    # a1.set_ylabel("Signal")
    # a0.set_xlabel("$B_0$")
    sep = 4

    ### cw EPR ###
    diff = su - sd
    pos = np.where(su - sd > sep)[0][0]
    gamma = 0.5
    stime = np.linspace(2.9, 3.4, 100)
    sin = 0.5 + 0.1 * np.sin(2 * np.pi * 4 * stime + 0.75)
    absorption = 1 / (2 * np.pi) * gamma / \
        ((sweepfield - sweepfield[pos])**2 + (1 / 2 * gamma)**2)
    a1.plot(sweepfield, absorption / np.max(absorption), label=r"$\chi''$")
    a1.plot(sweepfield[:-1], np.diff(absorption) /
            np.max(np.diff(absorption) * 2), label=r"$\frac{d\chi''}{dB}$")
    a1.plot(stime - 0.25, sin + 0.3, c='k', alpha=0.5)
    a1.annotate('$\Delta V_{mod}$', (1.3, 0.8), alpha=0.5)
    a1.plot(2.25 + sin, stime - np.min(stime), c='k')
    a1.annotate('$\Delta B_{mod}$', (1.2, 0.2))
    a1.text(0.05, 0.7, 'A)', transform=a1.transAxes)
    a1.set_xticks([0, sweepfield[pos]])
    a1.set_xticklabels(["$B_0$", r"$B_{res}$"])
    # a1.set_xticklabels([])
    a1.set_xlim()
    a1.set_xlabel('Magnetic field ($B_{ext}$)')
    a1.set_ylim(top=1.75)
    # a0.set_xticks([0, sweepfield[pos]])
    # a0.set_xticklabels([0, r"$B_{res}$"])
    c = 'k'
    head = 0.1
    # a0.plot([sweepfield[pos], sweepfield[pos]], [su[pos], sd[pos]],
            # c=c, label='$\hbar \omega$', ls='--')
    # a0.arrow(sweepfield[pos], sd[pos] + head, 0, -head / 30, shape='full',
            #  length_includes_head=True, head_width=0.1, ec=c, fc=c)
    # a0.arrow(sweepfield[pos], su[pos] - head, 0, head / 30, shape='full',
            #  length_includes_head=True, head_width=0.1, ec=c, fc=c)
    # a0.plot(sweepfield, su, label=r'$m_s=+\frac12$',)
    # a0.plot(sweepfield, sd, label=r'$m_s=-\frac12$',)
    # a0.set_xlim(right=10.5)
    ### cw EPR ###

    ### pulsed EPR ###
    time = np.linspace(0, 6, 1000)
    pulses = np.logical_and(time >= 1, time < 1.5)
    pulses += np.logical_and(time >= 2.5, time < 3.5)
    signal = 0.8*np.exp(-(time - 4.75)**2 / (2 * gamma / 6 ** 2))
    fidpts = np.where(np.diff(pulses.astype(float)) < 0)[0]
    signal += (time > time[fidpts[0]]) * np.exp(-(time - time[fidpts[0]])/0.05)
    signal += (time > time[fidpts[1]]) * np.exp(-(time - time[fidpts[1]])/0.05)
    a2.plot(time, pulses, zorder=2)
    a2.plot(time, signal, zorder=1)
    a2.fill_between(time, pulses, label='Pulses', zorder=3)
    a2.fill_between(time, signal, label='Signal', zorder=3)
    a2.plot(time, [0] * len(time), c='k', zorder=3)
    a2.set_ylim(top=2.25)
    # a2.set_xlabel(r'Time ($\mu$s)')
    # a2.set_ylabel(r'Signal')
    a2.text(0.05, 0.7, 'B)', transform=a2.transAxes)
    a2.set_xticklabels([])
    ### pulsed EPR ###

    ### rapidscan EPR ###
    f = 200e3
    RStimes = np.linspace(np.min(time), 6, int(10 * f * np.max(time))) * 1e-6
    t, rapid, w = Bloch(1e-6, 300e-9, 0, f, 25, t=RStimes)
    a3.plot(RStimes * 1e6, w / np.max(w) *
            np.max(rapid.y[0]), label='$B_{mod}$', c='k', alpha=0.5, ls='--')
    a3.plot(RStimes * 1e6, np.real(rapid.y[0] + 1j*rapid.y[1]), label='$M_\perp$')
    # a3.plot(RStimes * 1e6, rapid.y[1], label='$M_y$')
    # a3.set_ylabel('Signal')
    a3.set_xlabel('Time ($\mu$s)')
    a3.set_ylim(top=0.6)
    a3.text(0.05, 0.7, 'C)', transform=a3.transAxes)
    ### rapidscan EPR ###
    fig.supylabel('Amplitude (arb. u)', fontsize=20)

    # reordering the labels
    # handles, labels = a0.get_legend_handles_labels()
    # order = [1, 2, 0]
    # a0.legend([handles[i] for i in order], [labels[i] for i in order],
    #           loc='center right', markerfirst=False, handlelength=1, handletextpad=0.4, labelspacing=0.2,)
    a1.legend(
        loc='upper right', handlelength=1, handletextpad=0.4, labelspacing=0.0, ncol=3
    )
    a2.legend(
        loc='upper right', handlelength=1, handletextpad=0.4, labelspacing=0.0, ncol=3
    )
    a3.legend(
        loc='upper right', handlelength=1, handletextpad=0.4, labelspacing=0.0, ncol=3
    )
    plt.savefig('/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/Shared drives/Brad-Tonda UCSB/2022-Quasi-optical Sample Holder Solution for sub-THz Electron Spin Resonance Spectrometers/Figures/EPRtechniques.png', dpi=600)


if __name__ == "__main__":
    main()
    plt.show()
