import matplotlib.pyplot as plt
import numpy as np
import re
from pathlib import Path as P
from scipy.signal import savgol_filter


def main():
########### CHANGE FOLDER HERE #############
    process(folder=r"G:\My Drive\Research\Data\2021\03\24")
############################################

def statusBar(percent):
    ps = '|' + '=' * (int(percent) // 2) + '-' * (50 - (int(percent) // 2)) + '|'
    if int(percent) == 100:
        print(f"{ps} {percent:.1f}% complete")
    else:
        print(f"{ps} {percent:.1f}% complete", end='\r')


def process(folder=".", keyword="wvlth", savgol=True, windowing=20, show=False):
    filelist = list(P(folder).glob("*" + keyword + "*.dat"))

    p = re.compile("(wvlth)([0-9]{3})")
    experiments = list(set([p.findall(str(ii))[0] for ii in filelist]))
    fig, ax = plt.subplots()
    filterfig, filterax = plt.subplots()

    for idx, exp in enumerate(sorted(experiments)):
        avglist = list(P(folder).glob("*" + "".join(exp) + "*.dat"))
        avgdata = False
        for idxx, file in enumerate(avglist):
            strlist = P(file).read_text().split("\n")
            lineidx = 0
            for index, line in enumerate(strlist):
                if line == "Time (s), Signal (V) ":
                    lineidx = index + 1
                    break
            data = np.loadtxt(str(file), skiprows=lineidx, delimiter=",")
            if type(avgdata) == bool:
                avgdata = data[2:, :]
                avgdata[:, -1] -= np.average(avgdata[-30:, -1])
            else:
                avgdata[:, -1] += data[2:, -1] - np.average(data[-30:, -1])
            statusBar((idx * len(avglist) + idxx + 1) / len(experiments) / len(avglist) * 100)
        avgdata[:, -1] /= len(avglist)
        filteravg = np.copy(avgdata)
        if savgol:
            filteravg[:, -1] = savgol_filter(avgdata[:, -1], 2 * (len(avgdata[:, -1]) // windowing) + 1, 2)
        ax.plot(avgdata[:, 0], avgdata[:, -1], label="".join(exp))
        filterax.plot(filteravg[:, 0], filteravg[:, -1], label="".join(exp))

    for AX in [ax, filterax]:
        AX.spines['top'].set_visible(False)
        AX.spines['right'].set_visible(False)
        AX.set_xlabel("Time (s)")
        AX.set_ylabel("Signal (V)")
        AX.set_xscale("log")
        AX.legend()
        if AX == ax:
            AX.set_title("Flash photolysis signal vs. log time")
            fig.savefig(P.joinpath(P(folder), "averagedUVVisData.png"), dpi=300)
        elif AX == filterax:
            AX.set_title("Filtered flash photolysis signal vs. log time")
            filterfig.savefig(P.joinpath(P(folder), "FILTEREDaveragedUVVisData.png"), dpi=300)
    if show:
        plt.show()


if __name__ == "__main__":
    main()
