import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP
from readDataFile import read

import PIL
import matplotlib.pyplot as plt
import numpy as np


def main(f, x=0, y=1, delimiter=', ', skiprows=0):
    """
    Create a new file with just two columns, x column on left and y column on right
    """
    _, data = read(P(f))
    outstr = ""
    for row in data:
        outstr += f"{row[x]}, {row[y]}\n"
    P(f).parent.joinpath(P(f).stem + f'_y={y}_XYfile.txt').write_text(outstr)


if __name__ == "__main__":
    FILE = '/Volumes/GoogleDrive/My Drive/Research/Data/2022/2/7/406 check/M02_usweep_LightOff_rephased.dat'
    main(FILE, x=1, y=3)
