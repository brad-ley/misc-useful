import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from matplotlib import rc
from scipy import signal

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


def sim(ax, additive=False):
    PULSE_LENGTH = 10e-9  # s
    PULSE_TIME = 325e-9  # s

    SLICER_LENGTH = 100e-9  # s
    SLICER_TIME = 350e-9  # s

    t = np.linspace(0, 1.75e-6, 10000)
    # pulse = np.logical_and(t > PULSE_TIME, t < PULSE_TIME + PULSE_LENGTH) * 1
    # pulse = np.exp(-(t - PULSE_TIME)**2 / (1/16 * PULSE_LENGTH**2))
    pulse = 1 * fermi_pulse(t, PULSE_TIME, PULSE_TIME + PULSE_LENGTH, 5e8)

    profile = np.logical_not(
        np.logical_and(t > SLICER_TIME, t
                       < SLICER_TIME + SLICER_LENGTH)).astype('float64')
    # begin for additive channel #

    if additive:
        profile = np.logical_not(profile).astype('float64')
    # end for additive channel #
    decay = np.concatenate(
        (np.ones(np.where(t < SLICER_LENGTH + SLICER_TIME)[0][-1]),
         np.exp(-(t[np.where(t > SLICER_LENGTH + SLICER_TIME)[0][0] - 1:] -
                  t[np.where(t > SLICER_LENGTH + SLICER_TIME)[0][0] - 1]) /
                (1 / 3 * np.max(t))))).astype('float64')
    body = fermi_pulse(t, 0.1e-6, 1e-6, 5e7)

    profile *= decay * body

    profile_pad = np.hstack(
        (np.zeros(len(profile)), profile, np.zeros(len(profile))))
    pulse_pad = np.hstack((np.zeros(len(pulse)), pulse, np.zeros(len(pulse))))

    # choose pulse for convolving to avoid artifacts
    conv_pulse = pulse[pulse > 0.05 * np.max(pulse)]

    # zero-pad end of signal function to reduce waste region
    # profile = np.concatenate((profile, np.zeros(len(conv_pulse))))

    out = signal.convolve(conv_pulse, profile_pad, 'valid')
    # out = np.convolve(pulse, profile, 'same')
    out /= np.max(out)

    early = fermi_pulse(t, 150e-9, 150e-9 + PULSE_LENGTH, 5e8) * np.max(pulse)
    early = np.hstack((np.zeros(len(early)), early, np.zeros(len(early))))
    late = fermi_pulse(t, 550e-9, 550e-9 + PULSE_LENGTH, 5e8) * np.max(pulse)
    late = np.hstack((np.zeros(len(late)), late, np.zeros(len(late))))

    showpulse = early + late + pulse_pad

    t = np.arange(t[0] - 1e-6, 3 * t[-1], (t[1] - t[0])) * \
        1e6  # make a new linspace

    ax.plot(t[:len(profile_pad)], profile_pad, label='subtractive')
    line = ax.plot(t[:len(showpulse)], showpulse, label='pulses')
    ax.fill_between(t[:len(showpulse)],
                    showpulse,
                    0,
                    where=showpulse > 0.05 * np.max(showpulse),
                    facecolor=line[0].get_color(),
                    alpha=0.25,
                    label='int. power')
    ax.fill_between(
        t[:len(showpulse)],
        showpulse,
        profile_pad,
        where=showpulse > 0.05 * np.max(showpulse),
        facecolor='white',
    )
    # ax.plot(t[:len(early)], early, c=line[0].get_color())
    # ax.plot(t[:len(late)], late, c=line[0].get_color())
    ax.plot(t[:len(out)], out - 1.5, label='convolution')

    return out, pulse_pad, t


def deconvolve(trace, pulse, t, ax):
    # impulse = signal.wiener(pulse[pulse > 0.05 * np.max(pulse)])
    impulse = pulse[pulse > 0.05 * np.max(pulse)]

    trace_fft = np.fft.fftshift(np.fft.fft(trace, len(trace)))
    fftfreq = np.fft.fftshift(np.fft.fftfreq(len(trace), (t[1] - t[0]) * 1e-6))

    pulse_fft = np.fft.fftshift(np.fft.fft(impulse, len(trace)))

    # can add a small nonzero baseline to the denominator to not get weird 0/0 behaviour
    sliced_fft = trace_fft / (pulse_fft + np.max(pulse_fft) * 1e-6)

    # sliced = np.fft.ifft(np.fft.ifftshift(sliced_fft), len(t))
    sliced = np.fft.ifft(sliced_fft, len(trace))
    # sliced -= np.min(sliced)
    sliced /= np.max(sliced)

    ax.plot(t[:len(sliced)], np.abs(sliced) - 3, label='deconvolved')
    # ax.plot(t, np.imag(sliced), label='decon')


if __name__ == "__main__":
    fig, ax = plt.subplots(layout='constrained', figsize=(6, 4))
    additive = False
    trace, pulse, t = sim(ax, additive=additive)
    deconvolve(trace, pulse, t, ax)
    ax.set_xlim([0.7, 1.8])
    ax.set_xlabel('Time ($\mu$s)')
    ax.set_ylabel('Signal (arb. u.)')
    ax.legend(loc=(1, 0.5))

    if additive:
        plt.savefig('/Users/Brad/Desktop/additive_slicer_sim.png', dpi=500)
    else:
        plt.savefig('/Users/Brad/Desktop/subtractive_slicer_sim.png', dpi=500)
    plt.show()
