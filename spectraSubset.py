import numpy as np


def subset(x_in, y_in, elem=-1, start=-1, end=-1):
    """
    Meant to allow a user to select and interpolate a subset of a dataset
    elem: integer
    start, end: field in mT
    """
    if elem != -1:
        x, x_in, y_in = new_x(start, end, elem, x_in, y_in)
    else:
        elem = len(x_in)
        x, x_in, y_in = new_x(start, end, elem, x_in, y_in)

    return x, np.interp(x, x_in, y_in)


def new_x(start, end, elem, x, y):
    """
    Subset chooser
    """

    if start != -1 and end != -1:
        start = start / 1000
        end = end / 1000
        start_idx = np.where(x > start)[0][0]
        end_idx = np.where(x < end)[0][-1]
        newx = np.linspace(start, end, elem)
        y = y[start_idx:end_idx]
        x = x[start_idx:end_idx]
    elif start != -1:
        start = start / 1000
        start_idx = np.where(x > start)[0][0]
        newx = np.linspace(start, x[-1], elem)
        y = y[start_idx:]
        x = x[start_idx:]
    elif end != -1:
        end = end / 1000
        end_idx = np.where(x < end)[0][-1]
        newx = np.linspace(x[0], end, elem)
        y = y[:end_idx]
        x = x[:end_idx]
    else:
        newx = np.linspace(x[0], x[-1], elem)

    return newx, x, y
