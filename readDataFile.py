import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

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
        idx_list = [('Field' in ii.strip()) for ii in datatypes.split(delimiter)]

    if 1 in idx_list:
        idx = idx_list.index(1)
    else:
        idx = 0
    if data[idx, 0] < data[idx, -1]:
        data = np.flipud(data)

    return header, data
