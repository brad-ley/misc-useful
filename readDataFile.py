import numpy as np


def read(filename, delimiter=','):
    """
    Takes file from EPR computer, removes header, returns numpy array
    """
    file = open(filename, 'r').readlines()

    for line in file:
        if line.startswith('[Data]'):
            data_idx = file.index(line)
            skiprows = data_idx + 2
            break

    data = np.loadtxt(filename, delimiter=delimiter, skiprows=skiprows)
    if data[0, 1] > data[-1, 1]:
        data = np.flipud(data)

    return data
