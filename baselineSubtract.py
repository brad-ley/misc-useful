import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from peakutils import baseline

import matplotlib.pyplot as plt
import numpy as np

def subtract(data):
    """subtract. removes baseline from lineshape, assuming data has been phased
    such that the imag channel shows no real lineshape

    :param indep: independent axis
    :param data: complex-value detection channel (real + 1j*np.imag)
    :param deg: degree of fitting polynomial
    """
    r = np.std(np.real(data))
    i = np.std(np.imag(data))
    if i != 0:
        if r > i:
            basedat = np.imag(data)
        else:
            basedat = np.real(data)
    else:
        basedat = np.real(data)

    base = baseline(basedat)
    return data - base
