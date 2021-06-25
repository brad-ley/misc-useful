#!python3
import os
import re
from pathlib import Path as P

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter


def main():
    ########### CHANGE FOLDER HERE #############
    process(
        folder=r"/Users/Brad/Downloads/For Max"
    )
    ############################################


def statusBar(percent):
    ps = '|' + '=' * (int(percent) // 2) + '-' * \
        (50 - (int(percent) // 2)) + '|'

    if int(percent) == 100:
        print(f"{ps} {percent:.1f}% complete")
    else:
        print(f"{ps} {percent:.1f}% complete", end='\r')


def process(folder=".",
            keyword="wvlth",
            windowing=20,
            show=False):
    """process.

    :param folder: target folder of UV Vis data
    :param keyword: sweep keyword
    :param windowing: number of points in Savitzky-Golay window
    :param show: show matplotlib plot
    """

    if P(folder).is_file():
        folder = str(P(folder).parent)
    filelist = list(P(folder).glob("*" + keyword + "*.dat"))

    if not len(filelist):
        raise ValueError(
            "The folder or keyword is wrong -- no files were found with the parameters given.")

    p = re.compile("(wvlth)([0-9]{3})")
    experiments = list(set([p.findall(str(ii))[0] for ii in filelist]))
    fig, ax = plt.subplots()
    filterfig, filterax = plt.subplots()

    for idx, exp in enumerate(sorted(experiments)):
        avglist = list(P(folder).glob("*" + "".join(exp) + "*.dat"))
        outstr = ""
        avgdata = False
        try:
            os.mkdir(folder + '/processed_data/')
        except FileExistsError:
            pass

        for idxx, file in enumerate(avglist):
            header, data = read(file)
            data = data[data[:, 0] > 0]

            if type(avgdata) == bool:
                avgdata = data
                avgdata[:, -1] -= np.average(avgdata[-30:, -1])
            else:
                avgdata[:, -1] += data[:, -1] - np.average(data[-30:, -1])
            statusBar((idx * len(avglist) + idxx + 1) / len(experiments) /
                      len(avglist) * 100)
        avgdata[:, -1] /= len(avglist)

        filteravg = np.copy(avgdata)

        filteravg[:, -1] = savgol_filter(
            avgdata[:, -1], 2 * (len(avgdata[:, -1]) // windowing) + 1, 2)
        pw = re.compile("(Wavelength: )([0-9]{3}\.[0-9]{3})")
        wv = pw.findall(header)[0]
        ax.plot(avgdata[:, 0], avgdata[:, -1], label=f"{float(wv[-1]):.1f} nm")
        filterax.plot(filteravg[:, 0], filteravg[:, -1],
                      label=f"{float(wv[-1]):.1f} nm")
        outfile = P(folder).joinpath('processed_data').joinpath(
            "_".join(str(avglist[0].name).split("_")[:-1]) + f"_{int(float(wv[-1]))}.csv")

        for row in avgdata:
            outstr += f"{row[0]}, {row[1]}\n"
        outfile.write_text(outstr)

    for AX in [ax, filterax]:
        AX.spines['top'].set_visible(False)
        AX.spines['right'].set_visible(False)
        AX.set_xlabel("Time (s)")
        AX.set_ylabel("Signal (V)")
        AX.set_xscale("log")
        AX.legend(loc='right')

        if AX == ax:
            AX.set_title("Flash photolysis signal vs. log time")
            fig.savefig(P.joinpath(P(folder), "processed_data",
                                   "averagedUVVisData.png"),
                        dpi=300)
        elif AX == filterax:
            AX.set_title("Filtered flash photolysis signal vs. log time")
            filterfig.savefig(P.joinpath(P(folder), "processed_data",
                                         "FILTEREDaveragedUVVisData.png"),
                              dpi=300)

    if show:
        plt.show()


def isNumber(num):
    """
    :param s:
    :return:
    stackexchange function to check if user input is a feasible number
    """
    try:
        float(num)

        return True
    except ValueError:
        return False


def read(filename, delimiter=','):
    """
    Takes file from EPR computer, removes header, returns header, numpy array
    :args: filename
    :kwargs: delimiter
    :return: header, data
    """
    file = P(filename).read_text().split("\n")

    header = ''
    found = False

    for line in file:
        if line.startswith('[Data]'):
            data_idx = file.index(line)
            header += line + "\n"
            header += file[file.index(line) + 1] + "\n"
            skiprows = data_idx + 2
            found = True
        elif all([isNumber(ii) for ii in line.split(delimiter)]):
            data_idx = file.index(line)
            skiprows = data_idx
            found = True

        if found:
            break
        header += line + "\n"

    idx_list = []
    datatypes = []
    data = np.loadtxt(filename, delimiter=delimiter, skiprows=skiprows)

    for line in header.split('\n')[::-1]:
        if line != '':
            datatypes = line

            break

    if datatypes:
        idx_dict = {'field': ['field' in ii.strip().lower()
                              for ii in datatypes.split(delimiter)],
                    'time': ['time' in ii.strip().lower()
                             for ii in datatypes.split(delimiter)]}

    if True in idx_dict['field']:
        idx = idx_dict['field'].index(1)
    elif True in idx_dict['time']:
        idx = idx_dict['time'].index(1)
    else:
        idx = 0

    if data[idx, 0] > data[idx, -1]:
        data = np.flipud(data)

    return header, data


if __name__ == "__main__":
    main()
