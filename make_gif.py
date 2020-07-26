import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

# sys.path.append('/Users/Brad/Documents/Research/code/python/misc-useful')
from iterateFilename import iterate


def main(filename):
    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    ax.grid()
    ax.set_xlabel('Field (mT)')
    ax.set_ylabel('Absorption (arb. u)')
    ax.set_yticks([])
    r_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    xdata, ydata = [], []
    data = np.loadtxt(filename, delimiter=',')

    if np.shape(data)[0] > np.shape(data)[1]:
        data = np.transpose(data)
    init_max_y = np.max(data[0, :])
    init_min_y = np.min(data[0, :])

    def data_gen(data):
        for ii in range(len(data)):
            yield np.linspace(-3, 3, np.shape(data)[1]), data[ii, :], ii

    def init():
        ax.set_xlim(-3, 3, np.shape(data)[1])
        ax.set_ylim(init_min_y, init_max_y)
        r_text.set_text('')
        del xdata[:], ydata[:]
        line.set_data(xdata, ydata)

        return line,

    def run(data):
        xdata, ydata, ii = data
        r_text.set_text(f"r={1+np.linspace(0,5,len(xdata))[ii]:.2f} nm")

        max_y = np.max(ydata)
        min_y = np.min(ydata)
        ax.set_ylim([1.1 * min_y, 1.1 * max_y])
        ax.figure.canvas.draw()
        line.set_data(xdata, ydata)

        return line,

    ani = FuncAnimation(fig,
                        run,
                        frames=data_gen(data),
                        blit=False,
                        repeat=False,
                        init_func=init,
                        save_count=np.shape(data)[0])

    startsave = '/'.join(filename.split('/')[:-1]) + '/gifs/' + filename.split(
        '/')[-1][:-4] + '.gif'
    savefile = iterate(startsave)
    ani.save(savefile, writer=PillowWriter(fps=10))


if __name__ == "__main__":
    # main("./data/D,stdev=1213,418_deriv.txt")
    main(
        "/Users/Brad/Box Sync/Sherwin Lab/matlab/Gd(III) Label Modeling Project/Calculations/Rewritten CWdipFit/Data/PyMTA_240GHz_add_SIMS.txt"
    )
