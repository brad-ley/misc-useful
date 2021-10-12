import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from scipy.signal import find_peaks as fp
from scipy.signal import welch
from statusBar import statusBar

from readDataFile import read

targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/09/30/smaller/'
frac = 0.05  # min height to appear in COM calculation
delta = 10e6
n = 8 # 1/2**n*1/(max time) for finding min usable frequency


def COM(x, y, frac=0.1, delta=10e6, min_freq=5e3):
    x, y = list(zip(*sorted(zip(x, y), key=lambda z: z[0])))
    x = np.array(list(x))
    y = np.array(list(y))
    xx = np.copy(x[np.logical_and(x > x[np.argmax(np.abs(y))] - delta,
                                  x < x[np.argmax(np.abs(y))] + delta)])
    yy = np.copy(y[np.logical_and(x > x[np.argmax(np.abs(y))] - delta,
                                  x < x[np.argmax(np.abs(y))] + delta)])
    t = np.abs(yy[yy > frac * np.max(yy)]) * xx[yy > frac * np.max(yy)]
    b = np.abs(yy[yy > frac * np.max(yy)])
    # print(f"{delta:.2f}, {np.trapz(t)/np.trapz(b):.2f}")
    try:
        out = np.trapz(t) / np.trapz(b)
    except ValueError:
        out = -1

    if np.abs(out) < min_freq:
        return out, True

    return out, False


def main(targ):
    if P(targ).is_file():
        targ = P(targ).parent
    fs = [ii for ii in P(targ).iterdir() if ii.name.startswith('test')]
    fs.sort(key=lambda x: int(x.name.lstrip('test_').rstrip('.dat')))
    tot_phases = []
    fig, ax = plt.subplots(nrows=2, ncols=1)
    plt.suptitle("Single scan data")
    figp, axp = plt.subplots()

    for i, f in enumerate(fs):
        # fftfig, fftax = plt.subplots()
        statusBar(i * 100 / len(fs))
        db = pd.read_csv(f, low_memory=False)
        data = db.iloc[3:, 1:].to_numpy(dtype=float)
        dt = db[db['waveform'] == 'delta t'].iloc[:, 1:].to_numpy(dtype=float)[
            0][0]
        data = np.insert(data, 0, np.linspace(
            0, (data.shape[0] - 1) * dt, data.shape[0]), axis=1)
        w = signal.blackman(data.shape[0])
        freq = np.fft.fftfreq(data.shape[0], dt)
        cpx = data[:, 1] + 1j * data[:, 2]
        mf = 1/(2**n*(data[-1, 0] - data[0, 0]))

        if i == 0:
            ref = np.copy(cpx)
            avg = np.copy(cpx)
        else:
            phi = np.angle(np.dot(np.conjugate(cpx), ref))
            cpx *= np.exp(1j * phi)
            avg += cpx

        ### demodulate at COM peak ###
        final = False
        fft = np.fft.fft(cpx * w)
        # fftax.plot(freq, np.abs(fft), label='start')
        com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)
   
        freqs = []
        i = 1
        while not found and round(com_pk, -2) not in freqs:
            freqs.append(round(com_pk, -2))
            cpx *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])
            fft = np.fft.fft(cpx * w)
            # fftax.plot(freq, np.abs(fft), label=f'loop {i}')
            i += 1
            com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)
    
        if found:
            cpx *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])

        fft = np.fft.fft(cpx * w)
        # fftax.plot(freq, np.abs(fft), label='end')
        # fftax.legend()

        add = i * 0.20
        axp.plot(data[:, 0], np.real(cpx) + add)
        axp.plot(data[:, 0], np.imag(cpx) + add)
        axp.plot(data[:, 0], np.abs(cpx) + add)
        axp.set_title("Each scan demodulated")
        tot_phases.append(
            f"{np.arctan2(np.sum(np.imag(cpx)), np.sum(np.real(cpx))):.3f}")

    avg /= len(fs)
    fft = np.fft.fft(avg * w)
    ff, aax = plt.subplots()
    aax.plot(data[:, 0], np.real(avg))
    aax.plot(data[:, 0], np.real(avg * w))
    aax.set_title("Average before demodulation")
    ax[0].plot(data[:, 0], data[:, 1])
    ax[0].plot(data[:, 0], data[:, 2])

    ax[1].plot(np.fft.fftshift(freq), np.fft.fftshift(
        np.abs(fft)), label=f"avg before demod")

    final = False
    com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)
    
    freqs = []
    while not found and round(com_pk, -2) not in freqs:
        freqs.append(round(com_pk, -2))
        avg *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])
        fft = np.fft.fft(avg * w)
        com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)

    if found:
        avg *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])

    ax[1].plot(freq, np.abs(np.fft.fft(avg * w)), label="avg after demod")

    ax[1].legend()

    f, a = plt.subplots()
    a.set_title("Averaged demodulated")
    a.plot(data[:, 0], np.real(avg))
    a.plot(data[:, 0], np.imag(avg))
    a.plot(data[:, 0], np.abs(avg))
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main(targ)
