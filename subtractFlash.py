import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import decimate, savgol_filter

sys.path.append('/Users/Brad/Documents/Research/code/python/misc-useful')

from readDataFile import read


def subtract(targ='./', background=0, experiment=1, downsample=10):
    if not targ.endswith('/'):
        targ += '/'

    filelist = [
        targ + ii for ii in os.listdir(targ)
        if ii.endswith('.dat') and ii.startswith('M')
    ]

    background_file = ''
    data_file = ''

    for file in filelist:
        m = re.search('[M][0-9][0-9]', file)
        num = int(m.group(0).lstrip('M'))

        if num == background and 'AverageLog' in file:
            background_file = file

        if num == experiment and 'AverageLog' in file:
            data_file = file

    if not background_file:
        print('No background average found. Attempting to calculate it.')
        background_list = [
            ii for ii in filelist
            if int(re.search('[M][0-9][0-9]', ii).group(0).lstrip('M')) ==
            background
        ]
        first_head, first_data = read(background_list[0])
        background_sum = np.copy(first_data)
        count = 1

        for file in background_list:
            h, d = read(file)
            background_sum += d
            count += 1
        b_data = background_sum / count
    else:
        b_header, b_data = read(background_file)

    if not data_file:
        print('No data average found. Attempting to calculate it.')
        data_list = [
            ii for ii in filelist
            if int(re.search('[M][0-9][0-9]', ii).group(0).lstrip('M')) == data
        ]
        first_head, first_data = read(data_list[0])
        data_sum = np.copy(first_data)
        count = 1

        for file in data_list:
            h, d = read(file)
            data_sum += d
            count += 1
        data = data_sum / count
    else:
        header, data = read(data_file)

    datatypes = header.strip().split(', ')

    title = ' '.join(data_file.split('/')[-1].split('_')[:-1]).title() + \
        ' spectrum w/o background'

    true_data = data[2:, 1] - b_data[2:, 1]
    plt.figure('True data')
    plt.plot(data[2:, 0], true_data, label=f"{targ.split('/')[-2]}nm")
    plt.plot(data[2::downsample, 0],
             decimate(true_data, downsample),
             label=f"{targ.split('/')[-2]}nm {downsample}x downsample")
    yy = savgol_filter(true_data, len(true_data) // downsample, 2)
    plt.plot(data[2:, 0], yy, label='savgol_filter')
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    plt.ylabel(datatypes[1])
    plt.yticks([])
    plt.xlabel(datatypes[0])
    plt.title(title)
    plt.legend()
    plt.savefig(targ + 'subtracted.png')


if __name__ == "__main__":
    subtract(
        targ=
        '/Volumes/GoogleDrive/My Drive/Research/Data/2020/09/2020-09-06_Flash/PRA174_E108Q_E50Q/590'
    )
