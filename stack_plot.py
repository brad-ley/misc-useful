import os

import matplotlib.pyplot as plt
import numpy as np

path = '/Users/Brad/Downloads/VT_cwEPR_BDPA_Bz_MultiDomain'
files = sorted(
    [ii for ii in os.listdir() if ii.startswith('dispersion_')],
    key=lambda x: float(x.split('_')[1].replace('p', '.').rstrip('K')))

count = 0

for file in files:
    name = float(file.split('_')[1].rstrip('K'))

    data = np.loadtxt(file, skiprows=1, delimiter=', ')

    plt.figure(1)
    plt.plot(data[:, 0],
             data[:, 1] / np.max(data[:, 1]) + 3 / 4 * count,
             label=name)
    count -= 1

    if file == files[-1]:
        x_min = data[0, 0] * (1 - 1e-4)
        x_max = data[-1, 0] * (1 + 1e-4)

plt.ylabel('Signal (shifted vertically for clarity)')
plt.xlim([x_min, x_max])
plt.tick_params(
    axis='y',  # changes apply to the x-axis
    which='both',  # both major and minor ticks are affected
    left=False,
    labelleft=False)  # ticks along the bottom edge are off

plt.xlabel('Field (T)')
plt.legend().set_draggable(True)
plt.title("cwEPR, $\chi'$ of BDPA-Bz")
plt.savefig('shifted_dispersions_fig.png')
plt.show()
