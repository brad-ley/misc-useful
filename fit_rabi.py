import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit as cf


def func(xdata, a, b, c, d):
    return a + d * np.exp(-b * xdata) * np.cos(c * xdata)


def process(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    data_idx = lines.index('[Data]\n')
    data = []

    for ii in range(data_idx + 2, len(lines) - 1):
        data.append([
            float(lines[ii].rstrip('\n').split(',')[0]),
            float(lines[ii].rstrip('\n').split(',')[1]),
            float(lines[ii].rstrip('\n').split(',')[2])
        ])

    data_array = np.array(data)
    data_dict = {
        'param': 1E6 * data_array[:, 0],
        'real': data_array[:, 1],
        'imag': data_array[:, 2]
    }

    popt, pcov = cf(
        func, data_dict['param'],
        np.sqrt(data_dict['real']**2 + data_dict['imag']**2) /
        np.max(np.sqrt(data_dict['real']**2 + data_dict['imag']**2)))
    min_idx = np.where(
        func(data_dict['param'], *popt) == np.min(
            func(data_dict['param'], *popt)))
    min_time = data_dict['param'][min_idx][0]
    rabi_freq = 1 / (2 * min_time * 10**(-6)) / 10**(6)
    print(popt)
    plt.plot(
        data_dict['param'],
        np.sqrt(data_dict['real']**2 + data_dict['imag']**2) /
        np.max(np.sqrt(data_dict['real']**2 + data_dict['imag']**2)))
    plt.plot(data_dict['param'], func(data_dict['param'], *popt))
    plt.text(2*min_time, (popt[0] + 1)/2, f"Min time: {min_time} $\mu$s\nFreq: {rabi_freq:.2f} MHz")
    plt.ylabel('Echo intensity (arb. u)')
    plt.xlabel('Time ($\mu$s)')
    plt.show()


process('M08_rabi_000.dat')
