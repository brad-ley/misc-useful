import os
import sys

import numpy as np

sys.path.append('/Users/Brad/Documents/Research/code/python/misc-useful')
from readDataFile import read


def shrink(filename, start=0, end=-1):
    header, data = read(filename)
    data = data[start:end, :]
    savename = 'short_' + filename
    np.savetxt(savename, data, header=header, delimiter=', ')


def main(start=0, end=-1, directory='.'):
    filelist = [
        ii for ii in os.listdir(directory)
        if (ii.endswith('.dat'))
    ]
    cur_file = filelist[0]

    for file in filelist:
        if file.startswith('M') and 'short_' + file not in filelist:
            nex_file = '_'.join(file.split('_')[:-1])

            if nex_file != cur_file:
                print(f"Finished {cur_file}")
            cur_file = nex_file
            shrink(file, start=start, end=end)


if __name__ == "__main__":
    main(start=10000)
