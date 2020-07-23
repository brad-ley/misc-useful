import os


def iterate(filename):
    if '/' in filename:
        savedir = '/'.join(filename.split('/')[:-1]) + '/'
        savefile = filename.split('/')[-1]
    else:
        savedir = './'
        savefile = filename

    newsavefile = savefile
    ii = 1

    while newsavefile in os.listdir(savedir):
        newsavefile = savefile[:-4] + "_" + str(ii).zfill(3) + savefile[-4:]
        ii += 1

    return savedir + newsavefile


if __name__ == "__main__":
    iterate("./data/D,stdev=1213,418_deriv.txt")
