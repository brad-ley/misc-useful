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

from readDataFile import read
from statusBar import statusBar

targ = '/Volumes/GoogleDrive/My Drive/Research/Data/2021/09/30/later/normal_acq_3200/'
frac = 0.05  # min height to appear in COM calculation
delta = 5e6
n = 9  # 1/2**n*1/(max time) for finding min usable frequency
rd = -1
Q = 0.0045


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
    if not np.trapz(b) == 0:
        try:
            out = np.trapz(t) / np.trapz(b)
        except TypeError:
            out = -1
    else:
        out = -1

    if out != -1 and np.abs(out) < min_freq:
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
    figp, axp = plt.subplots(nrows=2, ncols=1, sharex=True)
    figg, axg = plt.subplots()

    axgscaty = []
    axgscatxr = []
    axgscatxi = []
    axgscatxm = []
    axgrey = []
    axgrexr = []
    axgrexi = []
    axgrexm = []
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
        cpx_og = np.copy(cpx)
        ref = False
        mf = 1 / (2**n * (data[-1, 0] - data[0, 0]))

        ### demodulate at COM peak ###
        final = False
        fft = np.fft.fft(cpx * w)
        # fftax.plot(freq, np.abs(fft), label='start')
        com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)

        freqs = []
        ii = 1
    
        # print(f"MF: {mf:.1f}")
        while not found and round(com_pk, rd) not in freqs:
            freqs.append(round(com_pk, rd))
            cpx *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])
            fft = np.fft.fft(cpx * w)
            # fftax.plot(freq, np.abs(fft), label=f'loop {ii}')
            ii += 1
            com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)
            # print(f"COM: {com_pk:.1f}, True: {found}")
            if np.isnan(com_pk):
                raise "Error"

        if found:
            cpx *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])

        fft = np.fft.fft(cpx * w)
        # fftax.plot(freq, np.abs(fft), label='end')
        # fftax.legend()
        if np.std(np.real(cpx)) < Q and np.std(np.imag(cpx)) < Q:
            if not ref:
                ref = cpx_og
                avg = np.zeros_like(cpx_og)
            phi = np.angle(np.dot(np.conjugate(cpx_og), ref))
            cpx_og *= np.exp(1j * phi)
            avg += cpx_og
            reject = 1
            axgscaty.append(np.mean(cpx))
            axgscatxr.append(np.std(np.real(cpx)))
            axgscatxi.append(np.std(np.imag(cpx)))
            axgscatxm.append(np.std(np.abs(cpx)))
        else:
            reject = 0
            axgrey.append(np.mean(cpx))
            axgrexr.append(np.std(np.real(cpx)))
            axgrexi.append(np.std(np.imag(cpx)))
            axgrexm.append(np.std(np.abs(cpx)))

        add = i * np.mean(np.abs(cpx)) * 1.1

        l = 0.75
        axp[reject].plot(data[:, 0], np.real(cpx), alpha=l)
        axp[reject].plot(data[:, 0], np.imag(cpx), alpha=l)
        axp[reject].plot(data[:, 0], np.abs(cpx), alpha=l)
        tot_phases.append(
            f"{np.arctan2(np.sum(np.imag(cpx)), np.sum(np.real(cpx))):.3f}")

    axg.scatter(np.abs(np.real(axgscaty)), axgscatxr
        , c='blue', alpha=1, label='real')
    axg.scatter(np.abs(np.imag(axgscaty)), axgscatxi
        , c='red', alpha=1, label='imag')
    axg.scatter(np.abs(axgscaty), axgscatxm
        , c='black', alpha=1, label='mag')
    axg.scatter(np.abs(np.real(axgrey)), axgrexr
        , c='blue', alpha=0.25)
    axg.scatter(np.abs(np.imag(axgrey)), axgrexi
        , c='red', alpha=0.25)
    axg.scatter(np.abs(axgrey), axgrexm
        , c='black', alpha=0.25)
    axp[0].set_title("Each scan demodulated (tossed)")
    axp[0].set_ylabel("Signal (arb. u)")
    axp[1].set_ylabel("Signal (arb. u)")
    axp[1].set_xlabel("Time (s)")
    axp[1].set_title(f"Each scan demodulated (kept {len(axgscaty) / (len(axgrey) + len(axgscaty)) * 100:.1f}%)")
    axg.set_title("Channel st dev vs. mean")
    axg.set_xlabel("Channel mean")
    axg.set_ylabel("Channel standard dev")
    axg.legend()
    axg.axhline(Q, c='gray', alpha=0.5, ls="--")

    avg /= len(fs)
    fft = np.fft.fft(avg * w)
    ff, aax = plt.subplots()
    aax.plot(data[:, 0], np.real(avg))
    aax.plot(data[:, 0], np.real(avg * w))
    aax.set_title("Average before demodulation")
    aax.set_xlabel("Time (s)")
    aax.set_ylabel("Signal (arb. u)")
    ax[0].plot(data[:, 0], data[:, 1])
    ax[0].plot(data[:, 0], data[:, 2])
    ax[0].set_ylabel("Signal (arb. u)")
    ax[0].set_xlabel("Time (s)")

    ax[1].plot(np.fft.fftshift(freq), np.fft.fftshift(
        np.abs(fft)), label=f"avg before demod")
    ax[1].set_ylabel("Signal (arb. u)")
    ax[1].set_xlabel("Freq (Hz)")

    final = False
    com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)

    freqs = []

    while not found and round(com_pk, rd) not in freqs:
        freqs.append(round(com_pk, rd))
        avg *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])
        fft = np.fft.fft(avg * w)
        com_pk, found = COM(freq, fft, frac=frac, delta=delta, min_freq=mf)

    if found:
        avg *= np.exp(-1j * 2 * np.pi * com_pk * data[:, 0])

    ax[1].plot(freq, np.abs(np.fft.fft(avg * w)), label="avg after demod")

    ax[1].legend()

    f, a = plt.subplots()
    a.set_title("Averaged demodulated")
    a.set_xlabel("Time (s)")
    a.set_ylabel("Signal (arb. u)")
    a.plot(data[:, 0], np.real(avg))
    a.plot(data[:, 0], np.imag(avg))
    a.plot(data[:, 0], np.abs(avg))
    # a.set_ylim([0, np.max(np.abs(avg))*1.05])
    for fg in [fig, figp, figg, f, ff]:
        fg.tight_layout()
    plt.show()


if __name__ == "__main__":
    main(targ)