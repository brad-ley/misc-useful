import os
import sys

import numpy as np

sys.path.append('/Users/Brad/Documents/Research/code/python/misc-useful')
from readDataFile import read


def shrink(filename, start=0, end=-1, directory='.'):
    header, data = read(filename)
    data = data[start:end, :]
    savename = directory + '/short/' + filename
    np.savetxt(savename, data, header=header, delimiter=', ')


def shorten(start=0, end=-1, directory='.'):
    filelist = [
        ii for ii in os.listdir(directory)
        if ii.endswith('.dat')
    ]
    try:
        os.makedirs(directory + '/short/')
    except FileExistsError:
        # directory already exists
        pass

    shortfilelist = [
        ii for ii in os.listdir(directory + "/short/")
        if (ii.endswith('.dat'))
    ]

    num = len([ii for ii in filelist if (ii.startswith('M') and ii not in shortfilelist)])
    count = 0 
    oldpercent = 0
    percent = 0
    ps = '|' + '-'*50 + '|'
    print(f"{ps} {percent}% done", end='\r')
    for file in filelist:
        if file.startswith('M') and file not in shortfilelist:
            shrink(file, start=start, end=end, directory=directory)
            lines = open(directory + '/short/' + file, 'r').readlines()
            for line in lines:
                idx = lines.index(line)
                if line.startswith('# '):
                    line = line[2:]
                    lines[idx] = line
                else:
                    data_idx = lines.index(line)
                    blank_idx = data_idx - 1
                    if lines[blank_idx] == '\n':
                        lines[blank_idx] = ''
                    break
            newfile = open(directory + '/short/' + file, 'w')
            for line in lines:
                newfile.write(line)
            newfile.close()
            percent = count*100 // num
            if percent > oldpercent:
                ps = '|' + '='*(percent//2) + '-'*(50 - (percent//2)) + '|'
                print(f"{ps} {percent}% done", end='\r')
                oldpercent = percent
            count += 1
   

if __name__ == "__main__":
    shorten(start=10000, directory='./fold')
