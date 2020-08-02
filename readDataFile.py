import numpy as np


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
    Takes file from EPR computer, removes header, returns numpy array
    """
    file = open(filename, 'r').readlines()
    
    header = ''
    for line in file:
        if line.startswith('[Data]'):
            data_idx = file.index(line)
            skiprows = data_idx + 2
            break
        elif all([isNumber(ii) for ii in line.split(delimiter)]):
            data_idx = file.index(line)
            skiprows = data_idx
            break
        header += line

    data = np.loadtxt(filename, delimiter=delimiter, skiprows=skiprows)
    if data[0, 1] > data[-1, 1]:
        data = np.flipud(data)

    return header, data
