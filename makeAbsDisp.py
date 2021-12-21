""" Written by Brad Price """
import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import numpy as np
from scipy import signal


def rolling_average(array, n=3):
    return [np.sum(array[ii: ii + n]) / n for ii, val in enumerate(array)]


def make(targ='./',
         keyw='uM',
         numerical_keyw=True,
         file_suffix='rephased.dat',
         field=8.57,
         center_sect=10,
         center=True,
         rollmid=50,
         hyster=0):
    """
    This finds the absorption and dispersion lines from the input 4-line
    rephased cwEPR spectra and makes new files for the absorption and
    dispersion spectra of each
    :param targ: directory of choice
    :param keyw: varied parameter
    :param numerical_keyw: return numeric output by default, string if false
    :param file_suffix: select the files that end in this string 
    :param field: B0 field value to add to field sweep
    :param center_sect: take the middle 1/nth when n is the argument
    :param center: adjusts for hysteresis to align resonances
    :param rollmid: len//param for rolling average to find max area of dispersive line
    :param hyster: (mT) adjusts B-field by hyster value if filename includes 'hyster'
    """

    if P(targ).is_file():
        targ = str(P(targ).parent)

    files = [
        str(ii) for ii in P(targ).iterdir()

        if ii.name.endswith(file_suffix) and not ii.name.startswith(".")
    ]

    file_length = {}

    for file in files:
        lines = [ii.rstrip('\n') for ii in P(file).read_text().split("\n")]

        file_length[file] = len(lines) + lines.index('[Data]') + 2

    files_sort = [
        ii[0]

        for ii in sorted(file_length.items(), key=lambda x: x[1], reverse=True)
    ]

    count = 0

    for file in files_sort:
        lines = [ii.strip() for ii in P(file).read_text().strip().split("\n")]

        for line in lines:
            data_start = lines.index('[Data]') + 2

        if file == files_sort[0]:
            longest_data = np.loadtxt(file, skiprows=data_start, delimiter=',')
            longest_data[:, 1] += field
            middle_B = longest_data[np.argmax(
                rolling_average(longest_data[:, 2], len(longest_data[:, 1])//rollmid)), 1]
            # middle_B = longest_data[np.argmax(longest_data[:, 2]), 1]

        curr_data = np.loadtxt(file, skiprows=data_start, delimiter=',')

        middle_averages = {}
        maxes = {}

        for ll in range(2, np.shape(curr_data)[1]):
            dat = signal.detrend(curr_data[:, ll])
            middle_averages[ll] = np.abs(
                np.average(
                    dat[np.where(np.abs(dat) == np.max(np.abs(dat)))[0][0] -
                        int(np.shape(dat)[0] / center_sect):np.where(
                            np.abs(dat) == np.max(np.abs(dat)))[0][0] +
                        int(np.shape(dat)[0] / center_sect)]))
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
        print(
            file.split('/')[-1],
            # middle_averages,
            # maxes,
            # sorted_average,
            sep='\n',
        )
        print(disp_idx, abs_idx)

        if np.abs(np.min(phased_disp)) > np.max(phased_disp):
            print('flipped disp')
            phased_disp = -1 * phased_disp

        max_idx = np.where(phased_absorp == np.max(phased_absorp))[0][0]
        min_idx = np.where(phased_absorp == np.min(phased_absorp))[0][0]

        if curr_data[min_idx, 1] < curr_data[max_idx, 1]:
            print('flipped abs')
            phased_absorp = -1 * phased_absorp

        curr_data[:, 2] = phased_disp[:]
        curr_data[:, 4] = phased_absorp[:]

        # curr_B = curr_data[np.argmax(curr_data[:, 2]), 1]
        curr_B = curr_data[np.argmax(
            rolling_average(curr_data[:, 2], len(curr_data)//rollmid)), 1]

        if center:
            diff_B = curr_B - middle_B
        else:
            diff_B = 0
        curr_data[:, 1] -= diff_B

        if 'hyster' in file:
            curr_data[:, 1] -= hyster * 1e-3
        print('---------------------------------------')

        # print([ii for ii in file.split('_') if keyw in ii])

        if numerical_keyw:
            name_keyw = ''.join(
                ch

                for ch in ''.join([ii for ii in file.split('_') if keyw in ii])

                if ch.isdigit() or ch == 'p' or ch == '.').replace('p', '.')

            if name_keyw == '':
                name_keyw = '0'
        else:
            name_keyw = "".join([ii for ii in P(file).name.split(
                '_') if keyw in ii]).replace(keyw, "")

            if name_keyw == '':
                name_keyw = f"{keyw}{count}"
                count += 1

        additional = ''

        if 'samp' not in keyw:
            if 'sample' in file.lower():
                samp = ''.join([
                    ch for ch in str(
                        [ii for ii in file.split('_') if 'sample' in ii.lower()])

                    if ch.isdigit()
                ])
                additional = f'_sample{samp}'

        fname = P(file).stem

        if 'DA' in fname:
            DA = ''.join([
                ch for ch in str([
                    fname.split('_')[fname.split('_').index(ii)]

                    for ii in fname.split('_') if 'DA' in ii
                ])
            ]).replace('p', '.')
            DA = float(''.join([ii for ii in DA if ii.isdigit() or ii == '.']))
            DAadd = f'_DA{DA}'
        else:
            DAadd = ''

        disp_name = P(targ).joinpath('dispersion_' +
                                     name_keyw + keyw + additional + DAadd + '_exp.txt')
        abs_name = P(targ).joinpath('absorption_' +
                                    name_keyw + keyw + additional + DAadd + '_exp.txt')

        P(disp_name).write_text(f"Field (T), {name_keyw + keyw} (deriv)\n")
        P(abs_name).write_text(f"Field (T), {name_keyw + keyw} (deriv)\n")
        min_idx = int(
            np.where(curr_data[:, 4] == np.min(curr_data[:, 4]))[0][0])
        max_idx = int(
            np.where(curr_data[:, 4] == np.max(curr_data[:, 4]))[0][0])

        disp_str = ""
        abs_str = ""

        for index, row in enumerate(curr_data):
            if curr_data[index][1] != curr_data[(index + 1) % len(curr_data)][1]:
                disp_str += f"{row[1] + field}, {row[2]}\n"
                abs_str += f"{row[1] + field}, {row[4]}\n"
        P(disp_name).write_text(disp_str)
        P(abs_name).write_text(abs_str)


if __name__ == "__main__":
    make(
        targ='/Volumes/GoogleDrive/My Drive/Research/Data/2021/11/15/BSA',
        keyw='M',
        file_suffix='rephased.dat',
        numerical_keyw=False,
        center=False,
        field=0,
        hyster=0)
