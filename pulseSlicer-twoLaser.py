import ast
import os
from dataclasses import dataclass
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
import skimage
from matplotlib import rc
from scipy import optimize, signal

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


@dataclass
class Data:
    """
    Data.

    ---attributes---
    t: profile time (optional)
    y: profile signal (optional)
    tpulse: pulse time (optional)
    pulse: pulse signal (optional)
    """

    # experiment: str
    # t: np.ndarray = np.array([])
    # y: np.ndarray = np.array([])
    # tpulse: np.ndarray = np.array([])
    # pulse: np.ndarray = np.array([])

    def load(self, files: list):
        """load.

        :param files:
        :type files: list
        :rtype: Data
        """

        for f in files:
            d = np.loadtxt(f, delimiter=',')

            if 'time-trace' in f.name:
                self.tpulse = d[:, 0] * 1e6
                self.pulse = d[:, 1]
            else:
                self.t = d[:, 0] * 1e6
                self.y = d[:, 1]

            self.file = files[0]
            self.experiment = files[0].stem.replace('time-trace',
                                                    '').replace('_', ' ')

        return self

    def channel(self):
        """channel. -> str returns 'additive' or 'subtractive' for experiment"""

        if hasattr(self, 'experiment'):
            if 'additive' in self.experiment:
                return 'additive'
            elif 'subtractive' in self.experiment:
                return 'subtractive'

            return ''

    def plot(self, plots, ax, savefig=False):
        """plot. generates plot of attributes 

        :param plots: list -> ['raw', 'pulse', 'deconvolved']
        :param ax: axes -> axes used for plotting
        """

        if hasattr(self, 'tpulse') and 'pulse' in plots:
            # pass
            ax.plot(self.tpulse[:len(self.impulse)],
                    self.impulse,
                    label=self.channel() + ' impulse')
            ax.plot(self.tpulse, self.pulse, label=self.channel() + ' pulse')

        if hasattr(self, 't') and 'raw' in plots:
            # pass
            ax.plot(self.t, self.y, label=self.channel() + ' slice')

        if hasattr(self, 'deconvolve') and 'deconvolved' in plots:
            # pass

            if len(self.t) == len(self.deconvolved):
                t = self.t
            else:
                t = np.linspace(
                    np.min(self.t) - 3 * (np.max(self.t) - np.min(self.t)),
                    np.max(self.t) + 3 * (np.max(self.t) - np.min(self.t)),
                    (1 + 6) * len(self.t))
            ax.plot(t,
                    np.abs(self.deconvolved),
                    label=self.channel() + ' deconvolved')
            ax.set_xlim([4, 5])

        ax.set_ylabel('Signal (mV)')
        ax.set_xlabel('Time ($\mu$s)')
        ax.legend(loc=(1, 0.6))

        if savefig:
            plt.savefig(
                self.file.parent.joinpath(f"plot_{'_'.join(plots)}.png"),
                dpi=500)

    def deconvolve(self):

        # def gaussian(x, x0, c, a, w):
        #     return c + a * np.exp(-(x - x0)**2 / (2 * w**2))

        # popt, pcov = optimize.curve_fit(gaussian, self.tpulse, self.pulse)
        # self.pulse = gaussian(self.tpulse, *popt)
        self.impulse = self.pulse[self.pulse > 0.05 * np.max(self.pulse)][::-1]

        padded = np.concatenate(
            (np.zeros(3 * len(self.y)), self.y, np.zeros(3 * len(self.y))))
        # padded = self.y
        trace_fft = np.fft.fftshift(np.fft.fft(padded, len(padded)))
        fftfreq = np.fft.fftshift(
            np.fft.fftfreq(len(padded), (self.t[1] - self.t[0]) * 1e-6))

        # pulse_fft = np.fft.fftshift(np.fft.fft(self.impulse, len(padded)))
        pulse_fft = np.fft.fftshift(np.fft.fft(self.impulse, len(padded)))

        # can add a small nonzero baseline to the denominator to not get weird 0/0 behaviour
        decon_fft = trace_fft / (pulse_fft + np.max(pulse_fft) * 1e-6)

        fig, a = plt.subplots(figsize=(8, 6))
        a.plot(fftfreq,
               np.abs(pulse_fft) / np.max(np.abs(pulse_fft)),
               label='pulse')
        a.plot(fftfreq,
               np.abs(trace_fft) / np.max(np.abs(trace_fft)),
               label='trace')
        a.plot(fftfreq,
               np.abs(decon_fft) / np.max(np.abs(decon_fft)),
               label='decon')
        a.legend()

        # self.deconvolved = np.fft.ifft(
        #     decon_fft * signal.blackman(len(decon_fft)), len(self.y))
        self.deconvolved = np.fft.ifft(decon_fft, len(self.y))
        self.deconvolved /= np.max(self.deconvolved)

        self.deconvolved = skimage.restoration.deconvolution.richardson_lucy(
            padded, self.impulse, num_iter=90, clip=False)

        return self


def main(folder):
    fig, ax = plt.subplots(layout='constrained', figsize=(7, 4))

    files = {}
    files['+'] = sorted(
        [ii for ii in P(folder).iterdir() if 'additive' in ii.stem])
    files['-'] = sorted(
        [ii for ii in P(folder).iterdir() if 'subtractive' in ii.stem])

    for exp in files:
        dat = Data()
        dat.load(files[exp]).deconvolve().plot(['deconvolved'],
                                               ax,
                                               savefig=False)

    plt.show()


if __name__ == "__main__":
    folder = '/Users/Brad/Library/CloudStorage/GoogleDrive-bdprice@ucsb.edu/My Drive/Research/Data/2023/5/24/20230524/second set'
    main(folder)
