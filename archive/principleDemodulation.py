import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np

from readDataFile import read


def demodulate(time, signal):
    """demodulate.
    Used to demodulate frequency modulated source. 
    FFT of signal determines principle frequency and applies it with a negative
    phase to the input signal vector.

    :param time: x-axis for data
    :param signal: complex-value data array
    :return: demodulated signal
    """
    fft = np.fft.fft(signal)
    freq = np.fft.fftfreq(len(signal), time[1])
    peakfreq = freq[np.argmax(np.abs(fft))]
    out = np.exp(-1j * 2 * np.pi * peakfreq * time) * signal
    return out


if __name__ == "__main__":
    header, data = read(
        "/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/03/02/M30_30ms.dat"
    )
    maxidx = np.argmax(np.amax(data, axis=0)[2:]) + 2
    out = demodulate(data[:, 0], data[:, 2] + 1j * data[:, 3])
    # out = demodulate(data[:,0],np.exp(1j * 11 * data[:,0]))
    fig, ax = plt.subplots()
    # plt.plot(data[:, 0], np.imag(out), data[:, 0], np.imag(out))
    ax.plot(data[:, 1] * 1e3, np.abs(out))
    ax.set_yticks([])
    ax.set_xlabel('Field (mT)')
    # ax.set_ylabel('Signal (arb. u)')
    for spine in ['right', 'left', 'top']:
        ax.spines[spine].set_visible(False)
    plt.show()
