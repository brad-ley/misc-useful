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
    Takes file from EPR computer, removes header, returns header, numpy array
    :args: filename
    :kwargs: delimiter
    :return: header, data
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
    for line in header.split('\n')[::-1]:
        if line != '':
            datatypes = line
            break

    idx_list = [('Field' in ii.strip()) for ii in datatypes.split(delimiter)]
    if 1 in idx_list:
        idx = idx_list.index(1)
        if data[idx, 0] < data[idx, -1]:
            data = np.flipud(data)

    return header, data
