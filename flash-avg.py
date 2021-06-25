import ast
import os
import re
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np

from readDataFile import read

############### CHANGE FOLDER HERE #################
folder = r"/Users/Brad/Downloads/For Max"
############### CHANGE FOLDER HERE #################


def process(targ):
    if P(targ).is_file():
        targ = P(targ).parent
    regex = re.compile(r"_Scan(\d+).dat")
    experiments = list(set([P("_".join(str(ii).split("_")[:-1]))
                            for ii in P(targ).iterdir() if regex.search(ii.name)]))

    for ind, exp in enumerate(experiments):
        files = [ii for ii in P(targ).iterdir() if ii.name.startswith(
            exp.name) and regex.search(ii.name)]

        for idx, f in enumerate(files):
            header, data = read(f, flipX=False)

            if idx == 0:
                outdata = np.zeros_like(data)
                for row in header.split("\n"):
                    if 'Wavelength:' in row:
                        wv = int(
                            float(("".join([ii for ii in row if ii.isdigit() or ii == "."]))))
            outdata += data
        outdata /= len(files)
        try:
            os.mkdir(str(exp.parent) + '/processed_data/')
        except FileExistsError:
            pass
        fileout = exp.parent.joinpath(
            "processed_data/" + exp.name + f"_{wv}.csv")
        outstr = ""

        for row in outdata:
            if row[0] > 0:
                outstr += f"{row[0]}, {row[1]}\n"
        fileout.write_text(outstr)
        statusBar((ind + 1) / len(experiments) * 100)


def statusBar(percent):
    ps = '|' + '=' * (int(percent) // 2) + '-' * \
        (50 - (int(percent) // 2)) + '|'

    if int(percent) == 100:
        print(f"{ps} {percent:.1f}% complete")
    else:
        print(f"{ps} {percent:.1f}% complete", end='\r')


def main():
    process(folder)


if __name__ == "__main__":
    main()
