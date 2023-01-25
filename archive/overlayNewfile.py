import os
import re

import numpy as np

target_directory = '/Volumes/GoogleDrive/My Drive/Research/Data/2020-08-26_Gd-DOTA_cwEPR/'

if not target_directory:
    target_directory = os.getcwd()

files = [
    target_directory + ii for ii in os.listdir(target_directory) if ii.endswith('ephased.dat')
]

by_temp = sorted(
    files, key=lambda x: float(x.split('_')[-2].replace('p', '.').rstrip('K')))
file_length = {}

for file in files:
    open_file = open(file, 'r')
    lines = [ii.rstrip('\n') for ii in open_file.readlines()]

    if file == by_temp[0]:
        data_index = lines.index('[Data]') + 2
    file_length[file] = len(lines) + lines.index('[Data]') + 2
    open_file.close()

files_sort = [
    ii[0]
    for ii in sorted(file_length.items(), key=lambda x: x[1], reverse=True)
]

longest = files_sort[0]
longest_data = np.loadtxt(file, skiprows=data_index, delimiter=', ')
longest_data[:, 1] += 8.57
middle_B = longest_data[int(
    np.where(longest_data[:, 2] == max(longest_data[:, 2]))[0][0]), 1]
p2p = {}

for file in files:
    data_start = lines.index('[Data]') + 2
    curr_data = np.loadtxt(file, skiprows=data_index, delimiter=', ')

    middle_averages = {}
    maxes = {}

    this_idx = by_temp.index(file)

    for ll in range(2, np.shape(curr_data)[1]):
        middle_averages[ll] = np.abs(
            np.average(curr_data[np.where(
                np.abs(curr_data[:, ll]) ==
                np.max(np.abs(curr_data[:, ll])))[0][0] -
                                 int(np.shape(curr_data)[0] / 10):np.where(
                                     np.abs(curr_data[:, ll]) ==
                                     np.max(np.abs(curr_data[:, ll])))[0][0] +
                                 int(np.shape(curr_data)[0] / 10), ll]))
        maxes[ll] = np.max(np.abs(curr_data[:, ll]))
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
    print(file.split('/')[-1], middle_averages, maxes, sorted_average, sep='\n')
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

    print('---------------------------------------')
    curr_B = curr_data[int(
        np.where(curr_data[:, 2] == np.max(curr_data[:, 2]))[0][0]), 1]
    diff_B = curr_B - middle_B
    curr_data[:, 1] -= diff_B

    disp_name = target_directory + 'dispersion_' + \
        file.split('_')[-2].replace('p', '.') + '_exp.txt'
    abs_name = target_directory + 'absorption_' + \
        file.split('_')[-2].replace('p', '.') + '_exp.txt'

    disp_file = open(disp_name, 'w')
    abs_file = open(abs_name, 'w')

    disp_file.write(
        f"Field (T), {file.split('_')[-2].replace('p', '.')} (deriv)\n")
    abs_file.write(
        f"Field (T), {file.split('_')[-2].replace('p', '.')} (deriv)\n")
    min_idx = int(np.where(curr_data[:, 4] == np.min(curr_data[:, 4]))[0][0])
    max_idx = int(np.where(curr_data[:, 4] == np.max(curr_data[:, 4]))[0][0])
    p2p[file] = (curr_data[min_idx, 1] - curr_data[max_idx, 1]) * 10**4

    for row in curr_data:
        disp_file.write(f"{row[1]}, {row[2]}\n")
        abs_file.write(f"{row[1]}, {row[4]}\n")

    disp_file.close()
    abs_file.close()

ppfile = open(target_directory + 'peak-to-peak.txt', 'w')
ppfile.write('Temp (K), Peak-to-peak width (G)\n')

temp_dict = {}

for file in p2p:
    temp = f"{float(file.split('_')[-2].replace('p', '.').rstrip('K')):.1f}" 
    temp_dict[temp] = abs(p2p[file])

temp_sorted = [ii for ii in sorted([float(ii) for ii in temp_dict.keys()])]

for temp in temp_sorted:
    # if temp == int(temp):
    #     temp = int(temp)
    ppfile.write(str(temp) + ', ' + str(temp_dict[str(temp)]) + '\n')

ppfile.close()
