import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, optimize
from scipy.stats import cauchy

# set to 1 for dispersive lineshapes, set to zero for absorptive
DISPERSIVE = 0

if DISPERSIVE == 1:
    start = 'dispersion_'
    shift = 1
    chi = "$\chi'$"
else:
    start = 'absorption_'
    shift = 1.5
    chi = "$\chi''$"

target_directory = '/Volumes/GoogleDrive/My Drive/Research/Data/2020-07-12/'

if not target_directory:
    target_directory = os.getcwd()


def lorentzian(x, x0, a, gam):
    return 1 / np.pi * a * 1 / 2 * gam / ((1 / 2 * gam)**2 + (x - x0)**2)


files = sorted(
    [ii for ii in os.listdir(target_directory) if ii.startswith(start)],
    key=lambda x: float(x.split('_')[-2].replace('p', '.').rstrip('K')),
    reverse=True)

count = 0
fig, axes = plt.subplots(len(files), sharex=True)

for file in files:
    temperature = float(file.split('_')[-2].rstrip('K'))
    name = str(temperature) + ' K'

    data = np.loadtxt(target_directory + file, skiprows=1, delimiter=', ')
    x = data[:, 0]
    y = data[:, 1]
    y = y / np.max(np.abs(y))

    integral_data = integrate.cumtrapz(y, x, initial=0)
    integral_y = integral_data / np.max(np.abs(integral_data))
    max_idx = np.where(integral_y == np.max(integral_y))[0]
    # max_idx = max_idx[len(max_idx)//2]
    max_idx = max_idx[0]
    # p0 = [x[max_idx], 1, 5e-4]
    p0 = [8.583, 1, 5e-4]
    popt, pcov = optimize.curve_fit(lorentzian,
                                    x,
                                    integral_y,
                                    maxfev=10000,
                                    p0=p0)
    axes[files.index(file)].plot(x, integral_y, 'k')
    axes[files.index(file)].plot(x,
                                 lorentzian(x, *popt), 'r',
                                 label=f"{popt[2]*10**(4):.2f} G @ {name}")
    axes[files.index(file)].set_yticks([])
    axes[files.index(file)].legend(loc='center left')

    if file == files[-1]:
        axes[files.index(file)].set_xlabel('Field (T)')

    if file == files[len(files) // 2]:
        axes[files.index(file)].set_ylabel('Absorption (arb. u)')

    fig.suptitle('Absorption (red: fit, black: experiment) vs\nfield for varying temperature T')
    fig.savefig(target_directory + 'fitted_absorptions.png')
    
    plt.figure('Stacked absorption')
    plt.plot(x,
             y / np.max(np.abs(y)) + shift * count,
             label=name)
    count -= 1

    if file == files[-3]:
        x_min = data[0, 0] * (1 - 1e-4)
        x_max = data[-1, 0] * (1 + 1e-4)
plt.xlim([x_min, x_max])

plt.ylabel('Signal (shifted vertically for clarity)')
plt.tick_params(
    axis='y',  # changes apply to the x-axis
    which='both',  # both major and minor ticks are affected
    left=False,
    labelleft=False)  # ticks along the bottom edge are off

plt.xlabel('Field (T)')
plt.legend().set_draggable(True)
plt.title(f"cwEPR, {chi} of BDPA-Bz")
plt.savefig(target_directory + f"shifted_{start}fig.png")
plt.show()
