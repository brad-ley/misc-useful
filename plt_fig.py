import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import easygui as eg

def makePlot(count):

    file = eg.fileopenbox("Choose file")

    try:
        data = np.array(pd.read_csv(file, engine='python',
                                    index_col=False))
        title, yax, xax, names = eg.multenterbox(title="Plot titles", fields=["Title", "y-axis", "x-axis",
                                                                              "Plot names"])
        nameslist = names.split(", ")
        plt.figure(count)

        for ii in range(len(data[0, :]) - 1):
            plt.plot(data[:, 0], data[:, ii + 1], label=nameslist[ii])
        plt.legend()
        plt.xlabel(xax)
        plt.ylabel(yax)
        plt.title(title)
        plt.savefig(file[:-4] + ".png")
        plt.show()

    except(TypeError, AttributeError):
        pass


def keepRunning():
    msg = "Do you want to run again?"
    if eg.ccbox(msg):  # show a Continue/Cancel dialog
        return True  # user chose Continue
    else:  # user chose Cancel
        sys.exit(0)


def main():
    cont = True
    count = 0
    while cont == True:
        makePlot(count)
        count += 1
        cont = keepRunning()


if __name__ == "__main__":
    main()
else:
    print("plt_fig.main()")
