import os

import numpy as np

# Not too proud of this guy but whatever gets the job done.. I guess

files = [ii for ii in os.listdir(os.getcwd()) if ii.endswith('ephased.dat')]
file_length = {}

for file in files:
    open_file = open(file, 'r')
    lines = [ii.rstrip('\n') for ii in open_file.readlines()]
    file_length[file] = len(lines)

files = [
    ii[0]
    for ii in sorted(file_length.items(), key=lambda x: x[1], reverse=True)
]

dispfile = open('combined_disp.txt', 'w')
dispfile.write("Field (T), ")
absfile = open('combined_abs.txt', 'w')
absfile.write("Field (T), ")
ppfile = open('combined_p2p.txt', 'w')
p2p = []

for file in files:
    open_file = open(file, 'r')
    lines = [ii.rstrip('\n') for ii in open_file.readlines()]
    data_index = lines.index('[Data]') + 2
    curr_data = np.loadtxt(file, skiprows=data_index, delimiter=', ')

    if file == files[0]:
        curr_data[:, 1] += 8.57
        fulldisp = np.zeros((len(curr_data[:, 1]), len(files) + 1))
        fullabs = np.zeros((len(curr_data[:, 1]), len(files) + 1))
        middle = int(np.where(curr_data[:, 2] == max(curr_data[:, 2]))[0])
        fulldisp[:len(curr_data[:, 1]), [0, 1]] = curr_data[:, [1, 2]]
        fullabs[:len(curr_data[:, 1]), [0, 1]] = curr_data[:, [1, 4]]
    else:
        curr_index = int(np.where(curr_data[:, 2] == max(curr_data[:, 2]))[0])
        delta_index = curr_index - middle

        length_diff = len(fulldisp[:, 1]) - len(curr_data[:, 1])

        if delta_index > 0:
            fulldisp[:len(curr_data[delta_index:, 2]),
                     files.index(file) + 1] = curr_data[delta_index:, 2]
            fullabs[:len(curr_data[delta_index:, 2]),
                    files.index(file) + 1] = curr_data[delta_index:, 2]
        elif delta_index < 0:
            fulldisp[np.abs(delta_index):np.abs(delta_index) +
                     len(curr_data[:-delta_index + length_diff, 2]),
                     files.index(file) + 1] = curr_data[:-delta_index +
                                                        length_diff, 2]
            fullabs[np.abs(delta_index):np.abs(delta_index) +
                    len(curr_data[:-delta_index + length_diff, 4]),
                    files.index(file) + 1] = curr_data[:-delta_index +
                                                       length_diff, 4]
        else:
            fulldisp[:, files.index(file) + 1] = np.hstack(
                (curr_data[:, 2], np.zeros(length_diff)))
            fullabs[:, files.index(file) + 1] = np.hstack(
                (curr_data[:, 4], np.zeros(length_diff)))
#    print(
#        np.shape(fullabs),
#        np.where(fullabs[:, files.index(file) +
#                         1] == np.min(fullabs[:, files.index(file) + 1])))
#    p2p.append(
#        (fullabs[int(
#            np.where(fullabs[:, files.index(file) + 1] ==
#                     np.min(fullabs[:, files.index(file) + 1]))[0]), 0] -
#         fullabs[int(
#             np.where(fullabs[:, files.index(file) + 1] ==
#                      np.max(fullabs[:, files.index(file) + 1]))[0]), 0]) *
#        10**4)
    open_file.close()

    if file == files[-1]:
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

for dist in p2p:
    file = files[p2p.index(dist)]
    ppfile.write(
        file.split('_')[1].replace('p', '.').rstrip('K') + ', ' +
        str(float(dist)))
    ppfile.write('\n')

ppfile.close()
