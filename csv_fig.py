import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import easygui as eg
import sys


def makePlot(count):
    file = eg.fileopenbox("Choose file")

    try:
        data = pd.read_csv(file, engine='python',
                           index_col=False).to_numpy()
        title, yax, xax, logs, names, size = eg.multenterbox(title="Plot titles",
                                                       fields=["Title", "y-axis", "x-axis", "Log? (type 'x, y, "
                                                                                  "or xy')",
                                                               "Plot names", "Font size"])

        nameslist = [ii.rstrip(' ').lstrip(' ') for ii in names.split(",")]

        plt.rcParams.update({'font.size': size})

        plt.figure(count)

        if len(nameslist) != len(data[0, :]) - 1:
            nameslist = [names] * (len(data[0, :]) - 1)

        for ii in range(len(data[0, :]) - 1):
            plt.plot(data[:, 0], data[:, ii + 1], label=nameslist[ii])
        plt.legend()
        plt.xlabel(xax)
        plt.ylabel(yax)
        if 'x' in logs:
            plt.xscale('log')
        if 'y' in logs:
            plt.yscale('log')
        plt.title(title)
        plt.tight_layout()
        plt.savefig(file[:-4] + ".png")
        plt.show()

    except(TypeError, AttributeError, ValueError):
        pass


def keepRunning():
    msg = "Do you want to run again?"
    if eg.ccbox(msg):  # show a Continue/Cancel dialog
        pass  # user chose Continue
    else:  # user chose Cancel
        sys.exit(0)


def main():
    count = 0
    while True:
        makePlot(count)
        count += 1
        keepRunning()


if __name__ == "__main__":
    main()
else:
    print("csv_fig.main()")
