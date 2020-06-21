import matplotlib.pyplot as plt
import numpy as np

file = '/Users/Brad/Box Sync/Sherwin Lab/Data/20200618/rephase/combined_abs.txt'
data_names = [
    ii.rstrip(', ')
    for ii in open(file, 'r').readlines()[0].rstrip('\n').split(', ')
]

data = np.loadtxt(file, skiprows=1, delimiter=', ')

for ii in range(1, np.shape(data)[1]):
    plt.figure(1)
    plt.plot(data[:, 0],
             data[:, ii] / np.max(data[:, ii]) - ii,
             label=data_names[ii])

plt.ylabel('Signal (shifted vertically for clarity)')
plt.tick_params(
    axis='y',  # changes apply to the x-axis
    which='both',  # both major and minor ticks are affected
    left=False,
    labelleft=False)  # ticks along the bottom edge are off

plt.xlabel(data_names[0])
plt.legend().set_draggable(True)
plt.title('cwEPR of BDPA-Bz at LN$_2$ temperatures')
plt.savefig(file.split('/')[-1][:-4] + '_shifted_fig.png')
plt.show()
