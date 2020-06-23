import os

import matplotlib.pyplot as plt
import numpy as np

# set to 1 for dispersive lineshapes, set to zero for absorptive
DISPERSIVE = 0

if DISPERSIVE == 1:
    start = 'dispersion_'
    shift = 3 / 4
    chi = "$\chi'$"
else:
    start = 'absorption_'
    shift = 1.5
    chi = "$\chi''$"

path = '/Users/Brad/Downloads/VT_cwEPR_BDPA_Bz_MultiDomain'
files = sorted(
    [ii for ii in os.listdir() if ii.startswith(start)],
    key=lambda x: float(x.split('_')[1].replace('p', '.').rstrip('K')))

count = 0

for file in files:
    name = float(file.split('_')[1].rstrip('K'))

    data = np.loadtxt(file, skiprows=1, delimiter=', ')

    plt.figure(1)
    plt.plot(data[:, 0],
             data[:, 1] / np.max(data[:, 1]) + shift * count,
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
plt.title(f"cwEPR, {chi} of BDPA-Bz")
plt.savefig(f"shifted_{start}fig.png")
plt.show()
