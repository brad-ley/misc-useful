import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from matplotlib import rc
from scipy.signal import fftconvolve

from readDataFile import read

if __name__ == "__main__":
    plt.style.use(['science'])
    rc('text.latex', preamble=r'\usepackage{cmbright}')
    rcParams = [
        ['font.family', 'sans-serif'],
        ['font.size', 14],
        ['axes.linewidth', 1],
        ['lines.linewidth', 2],
        ['xtick.major.size', 5],
        ['xtick.major.width', 1],
        ['xtick.minor.size', 2],
        ['xtick.minor.width', 1],
        ['ytick.major.size', 5],
        ['ytick.major.width', 1],
        ['ytick.minor.size', 2],
        ['ytick.minor.width', 1],
    ]
    plt.rcParams.update(dict(rcParams))


def fermi_pulse(t, start, stop, sharpness):

    def fermi(x, u, kT):
        return 1 / (np.exp((x - u) / kT) + 1)

    kT = 1 / sharpness
    fel = -fermi(t, start, kT) + fermi(t, stop, kT)

    return fel


def sim():
    PULSE_LENGTH = 50e-9  # s
    PULSE_TIME = 0.250e-6  # s

    SLICER_LENGTH = 50e-9  # s
    SLICER_LENGTH = 250e-9  # s

    t = np.linspace(0, 1.5e-6, 1000)
    # pulse = np.logical_and(t > PULSE_TIME, t < PULSE_TIME + PULSE_LENGTH) * 1
    # pulse = np.exp(-(t - PULSE_TIME)**2 / (1/16 * PULSE_LENGTH**2))
    pulse = fermi_pulse(t, PULSE_TIME, PULSE_TIME + PULSE_LENGTH, 2e8)

    profile = np.logical_not(
        np.logical_and(t > SLICER_TIME, t
                       < SLICER_TIME + SLICER_LENGTH)).astype('float64')
    decay = np.concatenate(
        (np.ones(np.where(t < SLICER_LENGTH + SLICER_TIME)[0][-1]),
         np.exp(-(t[np.where(t > SLICER_LENGTH + SLICER_TIME)[0][0] - 1:] -
                  t[np.where(t > SLICER_LENGTH + SLICER_TIME)[0][0] - 1]) /
                np.max(t)))).astype('float64')

    profile *= decay

    # choose pulse for convolving to avoid artifacts
    conv_pulse = pulse[pulse > 0.05 * np.max(pulse)]

    out = np.convolve(conv_pulse, profile, 'valid')
    # out = np.convolve(pulse, profile, 'same')
    out /= np.max(out)
    out += 1

    fig, ax = plt.subplots(layout='constrained', figsize=(6,4))
    t *= 1e6
    ax.plot(t[:len(out)], out, label='conv')
    ax.plot(t, profile, label='subtractive')
    ax.plot(t, pulse, label='pulse')
    ax.set_xlabel('Time ($\mu$s)')
    ax.set_ylabel('Signal (arb. u.)')
    ax.legend(loc=(1, 0.7))


if __name__ == "__main__":
    sim()
    plt.show()
