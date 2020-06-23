import os

import numpy as np

# Not too proud of this guy but whatever gets the job done.. I guess

# def moving_average(a, n=3):
#    ret = np.cumsum(a, dtype=float)
#    ret[n:] = ret[n:] - ret[:-n]
#
#    return ret[n - 1:] / n

files = [ii for ii in os.listdir(os.getcwd()) if ii.endswith('ephased.dat')]
by_temp = sorted(
    files, key=lambda x: float(x.split('_')[1].replace('p', '.').rstrip('K')))
file_length = {}

for file in files:
    open_file = open(file, 'r')
    lines = [ii.rstrip('\n') for ii in open_file.readlines()]
    file_length[file] = len(lines)

files_sort = [
    ii[0]
    for ii in sorted(file_length.items(), key=lambda x: x[1], reverse=True)
]

dispfile = open('combined_disp.txt', 'w')
dispfile.write("Field (T), ")
absfile = open('combined_abs.txt', 'w')
absfile.write("Field (T), ")
ppfile = open('combined_p2p.txt', 'w')
p2p = {}

for file in files_sort:
    open_file = open(file, 'r')
    lines = [ii.rstrip('\n') for ii in open_file.readlines()]
    data_index = lines.index('[Data]') + 2
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

    phased_disp = curr_data[:, disp_idx]
    phased_absorp = curr_data[:, abs_idx]
    print(file)
    print(file, middle_averages, maxes, sorted_average, sep='\n')
    print(disp_idx, abs_idx)

    if np.abs(np.min(phased_disp)) > np.max(phased_disp):
        print('flipped disp')
        phased_disp = -phased_disp

    if np.where(phased_absorp == np.min(phased_absorp))[0] < np.where(
            phased_absorp == np.min(phased_absorp))[0]:
        print('flipped abs')
        phased_absorp = -phased_absorp
        print('---------------------------------------')

    curr_data[:, 2] = phased_disp
    curr_data[:, 4] = phased_absorp

    if file == files_sort[0]:
        curr_data[:, 1] += 8.57
        fulldisp = np.zeros((len(curr_data[:, 1]), len(files_sort) + 1))
        fullabs = np.zeros((len(curr_data[:, 1]), len(files_sort) + 1))
        middle = int(np.where(curr_data[:, 2] == max(curr_data[:, 2]))[0][0])
        fulldisp[:len(curr_data[:, 1]), [0, this_idx]] = curr_data[:, [1, 2]]
        fullabs[:len(curr_data[:, 1]), [0, this_idx]] = curr_data[:, [1, 4]]
    else:
        curr_index = int(
            np.where(curr_data[:, 2] == max(curr_data[:, 2]))[0][0])
        delta_index = curr_index - middle

        length_diff = len(fulldisp[:, 1]) - len(curr_data[:, 1])

        if delta_index > 0:
            fulldisp[:len(curr_data[delta_index:, 2]),
                     by_temp.index(file) + 1] = curr_data[delta_index:, 2]
            fullabs[:len(curr_data[delta_index:, 2]),
                    by_temp.index(file) + 1] = curr_data[delta_index:, 2]
        elif delta_index < 0:
            fulldisp[np.abs(delta_index):np.abs(delta_index) +
                     len(curr_data[:delta_index, 2]),
                     by_temp.index(file) + 1] = curr_data[:delta_index, 2]
            fullabs[np.abs(delta_index):np.abs(delta_index) +
                    len(curr_data[:delta_index, 4]),
                    by_temp.index(file) + 1] = curr_data[:delta_index, 4]
        else:
            fulldisp[:, by_temp.index(file) + 1] = np.hstack(
                (curr_data[:, 2], np.zeros(length_diff)))
            fullabs[:, by_temp.index(file) + 1] = np.hstack(
                (curr_data[:, 4], np.zeros(length_diff)))
    min_idx = int(
        np.where(fullabs[:, by_temp.index(file) +
                         1] == np.min(fullabs[:, by_temp.index(file) +
                                              1]))[0][0])
    max_idx = int(
        np.where(fullabs[:, by_temp.index(file) +
                         1] == np.max(fullabs[:, by_temp.index(file) +
                                              1]))[0][0])
    p2p[file] = (fullabs[min_idx, 0] - fullabs[max_idx, 0]) * 10**4
    open_file.close()

#    if file.startswith('M02'):
#        print(delta_index)
#        print(phased_disp, len(phased_disp))
#        print(fulldisp[:, by_temp.index(file) + 1])

for file in by_temp:
    if file == by_temp[-1]:
        dispfile.write(file.split('_')[1].replace('p', '.'))
        absfile.write(file.split('_')[1].replace('p', '.'))
    else:
        dispfile.write(file.split('_')[1].replace('p', '.') + ", ")
        absfile.write(file.split('_')[1].replace('p', '.') + ", ")

dispfile.write('\n')
absfile.write('\n')

for row in fulldisp:
    dispfile.write(str(list(row)).lstrip('[').rstrip(']'))
    dispfile.write('\n')

dispfile.close()

for row in fullabs:
    absfile.write(str(list(row)).lstrip('[').rstrip(']'))
    absfile.write('\n')

absfile.close()

ppfile.write('Temp (K), Peak-to-peak width (G)\n')

temp_dict = {}

for file in p2p:
    temp = file.split('_')[1].replace('p', '.').rstrip('K')
    temp_dict[temp] = abs(p2p[file])
temp_sorted = [ii for ii in sorted([float(ii) for ii in temp_dict.keys()])]

for temp in temp_sorted:
    if temp == int(temp):
        temp = int(temp)
    ppfile.write(str(temp) + ', ' + str(temp_dict[str(temp)]) + '\n')

ppfile.close()
