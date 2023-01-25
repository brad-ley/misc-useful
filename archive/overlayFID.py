import os
import sys
import ast

import matplotlib.pyplot as plt
import numpy as np

from readDataFile import read


def importData(filename):
    """importData.

    :param filename: file
    """
    file = open(filename, 'r').read()

    if file[0] == '{':
        data = ast.literal_eval(file)
    else:
        data = {}
        header, npdata = read(filename)

        for item in header.strip().split('\n')[-1].split(','):
            itemdata = list(
                npdata[:,
                       header.strip().split('\n')[-1].split(',').index(item)])
            data[item.strip()] = itemdata

    return data


def overlayFFT(dir='./'):
    if dir[-1] != '/':
        dir += '/'
    filelist = [
        ii for ii in os.listdir(dir)
        if ii.endswith('.txt') and ii.startswith('FT')
    ]
    filelist = sorted(
        filelist,
        key=lambda x: [int(ii[:-2]) for ii in x.split('_') if 'ns' in ii])

    fig, ax = plt.subplots()
    step = 0.8 / len(filelist)  # this is in GHz
    shift = -0.4  # also in GHz

    for file in filelist:
        dataset = file.split('_')
        tau = [ii for ii in dataset if 'ns' in ii][0]
        data = importData(file)
        ax.plot(shift + np.array(data['Frequency']),
                np.sqrt(
                    np.array(data['FFT Real'])**2 +
                    np.array(data['FFT Imag'])**2),
                label=tau)
        shift += step
        # want to be using fft imag

    ax.set_xlim([239.5, 240.5])
    ax.legend().set_draggable(True)
    ax.set_yticks([])
    ax.set_ylabel('FFT magnitude (arb. u)')
    ax.set_xticks([])
    ax.set_xlabel('Frequency (centered at ~240)')
    ax.set_title('FFT magnitude for varying pulse separation')
    plt.savefig('shifted-fft.png')
    plt.show()


def overlayMag(type='int', dir='./', start=0, end=-1):
    if dir[-1] != '/':
        dir += '/'
    """
    Available types are 'int' for integral and 'max' for peak amplitude
    """
    filelist = [
        ii for ii in os.listdir(dir)
        if ii.endswith('.txt') and ii.startswith('FT')
    ]

    if not filelist:
        filelist = [
            ii for ii in os.listdir(dir)
            if ii.endswith('.dat') and ii.startswith('M')
        ]

    if not filelist:
        filelist = [
            ii for ii in os.listdir(dir)
            if ii.endswith('.txt') and ii.startswith('cycled')
        ]

    x = []
    y = []
    for file in sorted(filelist):
        dataset = file.split('_')
        tau = [ii for ii in dataset if ('TAU' or 'ns') in ii][0]
        data = importData(dir + file)
        has_ch = sum([key == 'Ch1' or key == 'Ch2' for key in data]) > 0
        taken = False

        if not has_ch:
            data['Ch1'] = []
            data['Ch2'] = []
            data['Limits'] = []

            for key in data:
                if key.startswith('Channel') and not taken:
                    data['Ch1'] = data[key]
                    key1 = key
                    taken = True
                elif key.startswith('Channel') and taken:
                    data['Ch2'] = data[key]
                    data['Limits'] = [start, end]
                    key2 = key

            del data[key1], data[key2]

            if not taken:
                print("WARNING: start and end values unused")
        try:
            os.mkdir(dir + 'processed_data/')
        except OSError:
            pass

        writefile = dir + 'processed_data/' + 'datafile_' + '_'.join(dataset[:-2]) + '.txt'
        with open(writefile, 'w') as f:
            print(data, file=f)

        tau = ''.join([ii for ii in tau if not ii.isalpha()])
        x.append(np.float(tau))
        # plt.figure(1)
        # plt.plot(data['Ch1'])

        if type == 'int':
            y.append(
                np.trapz(
                    np.sqrt(
                        np.array(data['Ch1'][start:end])**2 + np.array(data['Ch2'][start:end])**2)))
            ylabel = 'Integrated FID'
        elif type == 'max':
            y.append(
                np.mean(
                    np.abs(
                        np.sort(
                            np.abs(
                                np.sqrt(
                                    np.array(data['Ch1'][start:end])**2 +
                                    np.array(data['Ch2'][start:end])**2)))[:10])))
            ylabel = 'FID peak magnitude (arb. u)'

    y = y / np.max(y)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Tau ($\mu$s)')
    ax.set_title('FID vs pulse separation ($\mu$s)')
    plt.savefig('magnitude.png')
    plt.show()


if __name__ == "__main__":
    overlayMag(
        type='max',
        start=21500,
        end=22500,
        dir='/Volumes/GoogleDrive/My Drive/Research/Data/2020-08-05_BDPA_Bz_FELEPR/2020-08-05-T1-single-scan/cycled/')
