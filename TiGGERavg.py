import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from scipy.signal import find_peaks as fp
from scipy import signal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from readDataFile import read

targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/09/30/looped'


def main(targ):
    if P(targ).is_file():
        targ = P(targ).parent
    fs = [ii for ii in P(targ).iterdir() if ii.name.startswith('test')]
    fs.sort(key=lambda x: int(x.name.lstrip('test_').rstrip('.dat')))
    tot_phases = []
    fig, ax = plt.subplots(nrows=3,ncols=1)
    figp, axp = plt.subplots()
    for i, f in enumerate(fs): 
        db = pd.read_csv(f)
        data = db.iloc[3:, 1:].to_numpy(dtype=float)
        dt = db[db['waveform'] == 'delta t'].iloc[:, 1:].to_numpy(dtype=float)[
            0][0]
        data = np.insert(data, 0, np.linspace(
            0, (data.shape[0] - 1) * dt, data.shape[0]), axis=1)
        w = signal.blackman(data.shape[0])
        freq = np.fft.fftfreq(data.shape[0], dt)
        cpx = data[:, 1] + 1j * data[:, 2]
        if i == 0:
            ref = np.copy(cpx)
            avg = np.copy(cpx)
        else:
            phi = np.angle(np.dot(ref, np.conjugate(cpx)))
            cpx *= np.exp(1j * phi)
            avg += cpx

        fft = np.fft.fft(cpx*w)
        distance = np.where(freq > 5e6)[0][0] # ~10 MHz spacing between peaks
        h = 0.5 * np.max(np.abs(fft))
        peaks = fp(np.abs(fft), distance=distance, height=h)
        p = peaks[0][0]
        ph = peaks[1]["peak_heights"][0]
        i = 0
        freqs = []

        # want to iteratively demodulate the signal
        # while freq[p] not in freqs:
        while abs(freq[p]) not in freqs:
            freqs.append(abs(freq[p]))
            i += 1
            cpx *= np.exp(-1j * 2 * np.pi * np.abs(freq[p]) * data[:, 0])
            fft = np.fft.fft(cpx*w)
            peaks = fp(np.abs(fft), distance=distance, height=h)
            try:
                p = peaks[0][0]
                ph = peaks[1]["peak_heights"][0]
            except IndexError: # there are no significant peaks
                break
        axp.plot(data[:, 0], np.real(cpx))
        axp.plot(data[:, 0], np.imag(cpx))
        axp.plot(data[:, 0], 1.5*np.abs(cpx))
        tot_phases.append(f"{np.arctan2(np.sum(np.imag(cpx)), np.sum(np.real(cpx))):.3f}")
    
    avg /= len(fs)
    print(tot_phases)
    fft = np.fft.fft(avg*w)
    ff, aax = plt.subplots()
    aax.plot(np.real(avg))
    aax.plot(np.real(avg*w))
    ax[0].plot(data[:, 0], data[:, 1])
    ax[0].plot(data[:, 0], data[:, 2])
    distance = np.where(freq > 5e6)[0][0] # ~10 MHz spacing between peaks
    h = 0.5 * np.max(np.abs(fft))
    peaks = fp(np.abs(fft), distance=distance, height=h)
    p = peaks[0][0]
    ph = peaks[1]["peak_heights"][0]
    i = 0
    ax[2].plot(freq, np.abs(fft), label=f"pass 0")
    freqs = []

    # want to iteratively demodulate the signal
    # while freq[p] not in freqs:
    while abs(freq[p]) not in freqs:
        freqs.append(abs(freq[p]))
        i += 1
        avg *= np.exp(-1j * 2 * np.pi * np.abs(freq[p]) * data[:, 0])
        ax[1].plot(data[:, 0], np.real(avg), label=f"pass {i} r")
        ax[1].plot(data[:, 0], np.imag(avg), label=f"pass {i} i")
        fft = np.fft.fft(avg*w)
        ax[2].plot(freq, np.abs(fft), label=f"pass {i}")
        peaks = fp(np.abs(fft), distance=distance, height=h)
        try:
            p = peaks[0][0]
            ph = peaks[1]["peak_heights"][0]
        except IndexError: # there are no significant peaks
            break

    # for a in ax[:2]:
        # a.set_xlim([0, data[500, 0]])
    ax[1].legend()
    ax[2].legend()
    # ax[2].set_xlim([0, np.max(freq)])

    f, a = plt.subplots()
    a.plot(data[:, 0], np.real(avg))
    a.plot(data[:, 0], np.imag(avg))
    a.plot(data[:, 0], np.abs(avg))
    plt.show()


if __name__ == "__main__":
    main(targ)
