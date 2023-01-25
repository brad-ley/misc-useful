import ast
import os

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path as P
from pathlib import PurePath as PP
from readDataFile import read
from scipy.optimize import curve_fit as cf


def main():
    fit("/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/04/1/data_0T.dat", 52.5, approx=False, dims=False)

def debye_ndim(T, T_D, scale, n):
    c = np.empty(len(T))
    i = np.empty(len(T))
    mols = 0.46E-3 / 495.63 # number of mols of BDPA-Bz
    for index, t in enumerate(T):
        dx = T_D/1000000
        x = np.arange(1E-15, T_D/t, dx)
        integral = np.trapz(x**n / (np.exp(x) - 1),dx=dx)
        c[index] = 9*8.314*scale*mols*n*(t/T_D)**3 * integral
    
    return c

def debye(T, T_D, scale):
    c = np.empty(len(T))
    i = np.empty(len(T))
    mols = 0.46E-3 / 495.63 # number of mols of BDPA-Bz
    for index, t in enumerate(T):
        dx = T_D/1000000
        x = np.arange(1E-15, T_D/t, dx)
        integral = np.trapz(x**4 * np.exp(x) / (np.exp(x) - 1)**2,dx=dx)
        c[index] = 9*8.314*scale*mols*(t/T_D)**3 * integral
    
    return c


def low_T_approx(T, a, b):
    return a*T**(-2)+b*T**3


def fit(filename, debye_T, approx=False, dims=False):
    header, data = read(filename)
    max_T = 15
    data = data[data[:, 0] < max_T]
    if not approx:
        if dims:
            popt, pcov = cf(debye_ndim, data[:,0], data[:, 1], bounds=(([55, 0, 1/2],[65,np.inf,4])))
        else:
            popt, pcov = cf(debye, data[:,0], data[:, 1], bounds=(([55, 0],[65,np.inf])))
    else:
        popt, pcov = cf(low_T_approx, data[:,0], data[:, 1], p0=[150, 10E-3])
    fig, ax = plt.subplots()
    if not approx:
        if dims:
            ax.plot(data[:,0], debye_ndim(data[:, 0], *popt),label=r"$T_D$" + f"={popt[0]:.1f} K\nA={popt[1]:.1e}\nn={popt[2]:.1f}")
        else:
            ax.plot(data[:,0], debye(data[:, 0], *popt),label=r"$T_D$" + f"={popt[0]:.1f} K\nA={popt[1]:.1e}")
    else:
        ax.plot(data[:,0], low_T_approx(data[:, 0], *popt),label=f"A={popt[0]:.3e}; B={popt[1]:.3e}")
    ax.plot(data[:,0], data[:,1], label="raw")
    ax.legend()
    plt.savefig(P(filename).parent.joinpath('fit_to_0T.png'),dpi=300) 
    # ax.set_yscale('log')
    figg, axx = plt.subplots()
    for field in [0, 1, 3, 6, 9]:
        _, data = read(f"/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/04/1/data_{field}T.dat")
        data = data[data[:, 0] < max_T]
        if not approx:
            if dims:
                plt.plot(data[:, 0], data[:, 1] - debye_ndim(data[:, 0], *popt), label=f"{field} T")
            else:
                plt.plot(data[:, 0], data[:, 1] - debye(data[:, 0], *popt), label=f"{field} T")
        else:
            plt.plot(data[:, 0], data[:, 1] - low_T_approx(data[:, 0], *popt), label=f"{field} T")
    axx.legend()
    plt.savefig(P(filename).parent.joinpath('all_fields_subtract_0T_fit.png'),dpi=300) 
    plt.show()


if __name__ == "__main__":
    main()
