import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize, signal
import sys

sys.path.append('/Users/Brad/Documents/Research/code/python/misc-useful')
from makeAbsDisp import makeAbsDisp

def calibrate(targ='./', keyw="uM"):
    """
    This makes a calibration curve of baseline-subtracted doubly-integrated
    absorption lineshape as a function of concentration
    """
    x = []
    y = []
    e = []
    unknown = []
    samples = []

    filelist = sorted(
        [
            targ + ii for ii in os.listdir(targ)
            if ii.startswith('dispersion') and ii.endswith('.txt')
        ],
        key=lambda f: float(''.join(ch for ch in str(
            [ii for ii in f.split('/')[-1].split('_') if keyw in ii][0])
                                    if ch.isdigit())),
        reverse=True)

    base_DA = -1

    for file in filelist:
        # because the dispersive lineshape is nicer, use that and Hilbert
        # transform it

        name = ''.join(
            ch for ch in str([ii for ii in file.split('_') if keyw in ii])
            if ch.isdigit())

        DA = float(''.join(
            ch for ch in str([ii for ii in file.split('_') if 'DA' in ii])
            if ch.isdigit() or ch == '.'))

        samp = ''.join(
            ch for ch in str([ii for ii in file.split('_') if 'sample' in ii])
            if ch.isdigit())

        if samp:
            samp = float(samp)

        if base_DA == -1 and DA:
            base_DA = DA

        if DA:
            scaling = 10**(float(DA) / 10) / 10**(base_DA / 10)
            leg_name = name + keyw
        else:
            scaling = 1
            leg_name = name + keyw + " " + DA + "DA"
            
        if samp:
            leg_name = f"Samp {int(samp)}"

        print(f'DA is {DA}, base DA is {base_DA}, scaling is {scaling}')

        dat = np.loadtxt(file, skiprows=1, delimiter=',')
        dispersive = dat[:, 1] * scaling
        absorptive = -1 * np.imag(signal.hilbert(dispersive))
        absorption = integrate.cumtrapz(absorptive)
        absorp_err = np.sqrt(len(absorption)) * np.std(absorption)
        integrate_abs = integrate.trapz(absorption)

        plt.figure('Absorption')
        plt.plot(dat[:len(absorption), 0], absorption, label=leg_name)
        plt.legend()
        plt.figure('Dispersion')
        plt.plot(dat[:len(absorptive), 0], absorptive, label=leg_name)
        plt.legend()

        if 'sample' not in file:
            x.append(float(name))
            y.append(integrate_abs)
            e.append(absorp_err)
        else:
            unknown.append(integrate_abs)
            samples.append(samp)

    plt.figure('Absorption')
    plt.yticks([0])
    plt.ylabel('Integrated absorption (arb. u)')
    plt.xlabel('Field (T)')
    plt.savefig(targ + 'absorption.png')

    plt.figure('Dispersion')
    plt.yticks([0])
    plt.ylabel('Integrated dispersion (arb. u)')
    plt.xlabel('Field (T)')
    plt.savefig(targ + 'dispersion.png')

    plt.figure('Calibration')
    popt, pcov = optimize.curve_fit(func, x, y)
    conc = unknown / popt[0]
    end = np.max(np.hstack((x, conc)))
    plt.plot(np.linspace(0, end, 1000), func(np.linspace(0, end, 1000), *popt),
             'k--')
    plt.text(10, 0.7, f"Fit: y={popt[0]:.2E}x")
    plt.scatter(conc, unknown, c='red')

    for ii, txt in enumerate(samples):
        plt.annotate(f"Samp {int(txt)}: {conc[ii]:.2f} $\mu M$",
                     (conc[ii], unknown[ii]),
                     (conc[ii] + 5, unknown[ii] - 0.025),
                     c='red')
    plt.errorbar(x, y, yerr=e, capsize=3, fmt='ko')
    plt.grid()
    # plt.yticks(np.linspace(0, 0.8, 9))
    plt.xlabel('Concentration ($\mu M$)')
    plt.ylabel('Double integral of absorption')
    plt.title('Gd-DOTA calibration curve')
    plt.tight_layout()
    plt.savefig(targ + 'calibration.png')
    # plt.show()


def func(x, m):
    return m * np.array(x)


if __name__ == "__main__":
    makeAbsDisp(
        targ=
        '/Volumes/GoogleDrive/My Drive/Research/Data/2020-08-26_Gd-DOTA_cwEPR/',
    )
    calibrate(
        targ=
        '/Volumes/GoogleDrive/My Drive/Research/Data/2020-08-26_Gd-DOTA_cwEPR/'
    )
