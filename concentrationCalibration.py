import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize, signal


def makeAbsDisp(targ='./', keyw='uM'):
    """
    This finds the absorption and dispersion lines from the input 4-line
    rephased cwEPR spectra and makes new files for the absorption and
    dispersion spectra of each
    :param targ: directory of choice
    :param keyw: varied parameter
    """

    files = [
        targ + ii for ii in os.listdir(targ) if ii.endswith('ephased.dat')
    ]
    file_length = {}

    for file in files:
        open_file = open(file, 'r')
        lines = [ii.rstrip('\n') for ii in open_file.readlines()]

        file_length[file] = len(lines) + lines.index('[Data]') + 2
        open_file.close()

    files_sort = [
        ii[0]
        for ii in sorted(file_length.items(), key=lambda x: x[1], reverse=True)
    ]

    for file in files:
        lines = [ii.strip() for ii in open(file, 'r').readlines()]

        for line in lines:
            data_start = lines.index('[Data]') + 2

        if file == files_sort[0]:
            longest_data = np.loadtxt(file, skiprows=data_start, delimiter=',')
            longest_data[:, 1] += 8.57
            middle_B = longest_data[int(
                np.where(longest_data[:, 2] ==
                         np.max(longest_data[:, 2]))[0][0]), 1]

        curr_data = np.loadtxt(file, skiprows=data_start, delimiter=',')

        middle_averages = {}
        maxes = {}

        for ll in range(2, np.shape(curr_data)[1]):
            dat = signal.detrend(curr_data[:, ll])
            middle_averages[ll] = np.abs(
                np.average(
                    dat[np.where(np.abs(dat) == np.max(np.abs(dat)))[0][0] -
                        int(np.shape(dat)[0] / 10):np.where(
                            np.abs(dat) == np.max(np.abs(dat)))[0][0] +
                        int(np.shape(dat)[0] / 10)]))
            maxes[ll] = np.max(np.abs(dat))

            dat -= np.average(
                np.hstack((dat[:len(dat) // 4], dat[3 * len(dat) // 4:])))

            curr_data[:, ll] = np.copy(dat)
        sorted_average = [
            ii[1] for ii in sorted(
                middle_averages.items(), key=lambda x: x[1], reverse=True)
        ]

        for key in middle_averages:
            if middle_averages[key] == sorted_average[0]:
                disp_idx = key

        del maxes[disp_idx]  # remove used line

        abs_idx = sorted(maxes.items(), key=lambda x: x[1], reverse=True)[0][0]

        phased_disp = np.copy(curr_data[:, disp_idx])
        phased_absorp = np.copy(curr_data[:, abs_idx])
        print(file.split('/')[-1],
              middle_averages,
              maxes,
              sorted_average,
              sep='\n')
        print(disp_idx, abs_idx)

        if np.abs(np.min(phased_disp)) > np.max(phased_disp):
            print('flipped disp')
            phased_disp = -1 * phased_disp

        max_idx = np.where(phased_absorp == np.max(phased_absorp))[0][0]
        min_idx = np.where(phased_absorp == np.min(phased_absorp))[0][0]

        if curr_data[min_idx, 1] < curr_data[max_idx, 1]:
            print('flipped abs')
            phased_absorp = -1 * phased_absorp

        print('---------------------------------------')
        curr_data[:, 2] = phased_disp[:]
        curr_data[:, 4] = phased_absorp[:]

        curr_B = curr_data[int(
            np.where(curr_data[:, 2] == np.max(curr_data[:, 2]))[0][0]), 1]
        diff_B = curr_B - middle_B
        curr_data[:, 1] -= diff_B

        # print([ii for ii in file.split('_') if keyw in ii])
        name_keyw = ''.join(
            ch for ch in str([ii for ii in file.split('_') if keyw in ii])
            if ch.isdigit())

        if name_keyw == '':
            name_keyw = '0'

        disp_name = targ + 'dispersion_' + \
            name_keyw + keyw + '_exp.txt'
        abs_name = targ + 'absorption_' + \
            name_keyw + keyw + '_exp.txt'

        disp_file = open(disp_name, 'w')
        abs_file = open(abs_name, 'w')

        disp_file.write(f"Field (T), {name_keyw + keyw} (deriv)\n")
        abs_file.write(f"Field (T), {name_keyw + keyw} (deriv)\n")
        min_idx = int(
            np.where(curr_data[:, 4] == np.min(curr_data[:, 4]))[0][0])
        max_idx = int(
            np.where(curr_data[:, 4] == np.max(curr_data[:, 4]))[0][0])

        for row in curr_data:
            disp_file.write(f"{row[1]}, {row[2]}\n")
            abs_file.write(f"{row[1]}, {row[4]}\n")

        disp_file.close()
        abs_file.close()


def calibrate(targ='./', keyw="uM"):
    """
    This makes a calibration curve of baseline-subtracted doubly-integrated
    absorption lineshape as a function of concentration
    """
    x = []
    y = []
    e = []

    for file in sorted(
        [
            targ + ii for ii in os.listdir(targ)
            if ii.startswith('dispersion') and ii.endswith('.txt')
        ],
            key=lambda f: float(''.join(ch for ch in str(
                [ii for ii in f.split('/')[-1].split('_') if keyw in ii][0])
                                        if ch.isdigit())),
            reverse=True):
        # because the dispersive lineshape is nicer, use that and Hilbert
        # transform it

        name = ''.join(
            ch for ch in str([ii for ii in file.split('_') if keyw in ii])
            if ch.isdigit())

        if name == '0':
            DA = '27'

        if name == '50':
            DA = '34.25'
        elif name == '100':
            DA = '38'
        elif name == '150':
            DA = '36'
        elif name == '200':
            DA = '31.5'

        if DA:
            scaling = 10**(float(DA) / 10) / 10**(31.5 / 10)
            leg_name = name + keyw
        else:
            scaling = 1
            leg_name = name + keyw + " " + DA + "DA"

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

        if name != '0':
            x.append(float(name))
            y.append(integrate_abs)
            e.append(absorp_err)
        else:
            unknown = integrate_abs

    plt.figure('Absorption')
    plt.yticks([0])
    plt.ylabel('Signal (arb. u)')
    plt.xlabel('Field (T)')
    plt.savefig(targ + 'absorption.png')

    plt.figure('Dispersion')
    plt.yticks([0])
    plt.ylabel('Signal (arb. u)')
    plt.xlabel('Field (T)')
    plt.savefig(targ + 'dispersion.png')

    plt.figure('Calibration')
    popt, pcov = optimize.curve_fit(func, x, y)
    plt.plot(np.linspace(0, 200, 1000), func(np.linspace(0, 200, 1000), *popt),
             'k--')
    plt.text(10, 0.7, f"Fit: y={popt[0]:.2E}x")
    conc = unknown / popt[0]
    plt.scatter(conc, unknown, c='red')
    plt.annotate(f"Gd-LOV: {conc:.2f} $\mu M$", (conc, unknown),
                 (conc + 5, unknown - 0.025),
                 c='red')
    plt.errorbar(x, y, yerr=e, capsize=3, fmt='ko')
    plt.grid()
    plt.yticks(np.linspace(0, 0.8, 9))
    plt.xlabel('Concentration ($\mu M$)')
    plt.ylabel('Double integral of absorption')
    plt.title('Gd-DOTA calibration curve')
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
