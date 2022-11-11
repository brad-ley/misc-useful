import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import PIL
from matplotlib import rc
from readDataFile import read

plt.style.use('science')
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
lw=2


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
        x = 1/2 * B * sig_z @ state

        if all(x == 0):
            return x

        if any(abs(normalize(x)) != abs(normalize(state))):
            print('Not an eigenstate.')

            return

        return x

    l = 1000
    sweepfield = np.linspace(0, 10, l)
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
    fig, ax = plt.subplots()

    # ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_ylabel("Energy")
    ax.set_xlabel("$B_0$")
    sep = 4
    diff = su - sd
    pos = np.where(su - sd > sep)[0][0]
    ax.set_xticks([0, sweepfield[pos]])
    ax.set_xticklabels([0, r"$B_{res}$"])
    c = 'red'
    head = 0.1
    ax.plot([sweepfield[pos], sweepfield[pos]], [su[pos], sd[pos]], c=c, label='$\hbar \omega$', ls='--',lw=lw)
    ax.arrow(sweepfield[pos], sd[pos]+head, 0, -head/30, shape='full', lw=2,
             length_includes_head=True, head_width=0.1, ec=c, fc=c)
    ax.arrow(sweepfield[pos], su[pos]-head, 0, head/30, shape='full', lw=2,
             length_includes_head=True, head_width=0.1, ec=c, fc=c)
    ax.plot(sweepfield, su, label=r'$m_s=+\frac12$',lw=lw)
    ax.plot(sweepfield, sd, label=r'$m_s=-\frac12$',lw=lw)

    # reordering the labels
    handles, labels = plt.gca().get_legend_handles_labels()
    order = [1, 2, 0]
    ax.legend([handles[i] for i in order], [labels[i] for i in order], markerfirst=False,handlelength=1,handletextpad=0.4,labelspacing=0.2,)

    plt.savefig('/Users/Brad/Desktop/EPR.png', dpi=500, transparent=True)


if __name__ == "__main__":
    main()
    plt.show()
