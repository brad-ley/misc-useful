import ast
import os

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path as P
from pathlib import PurePath as PP
from scipy.optimize import curve_fit as cf
from scipy.interpolate import interp1d
from readDataFile import read

TESTING = False
FITALL = False

def debye(T, td, s):

    c = np.empty(len(T))
    i = np.empty(len(T))
    # mols = 0.46E-3 / 495.63 # number of mols of BDPA-Bz
    for index, t in enumerate(T):
        if TESTING:
            dx = td/100
        else:
            dx = td/1000000
        x = np.arange(1E-15, td/t, dx)
        integral = np.trapz(x**4 * np.exp(x) / (np.exp(x) - 1)**2,dx=dx)
        c[index] = 9*8.314*s*(t/td)**3 * integral
    
    return c

def double_debye(T, td1, s1, td2, s2): 
    return debye(T, td1, s1) + debye(T, td2, s2)


def fit(filename, fitax, difax):
    folder = P(filename).parent
    _, data = read(filename)
    field = str(P(filename).stem).split("data_")[-1]
    if TESTING:
        popt, pcov = cf(double_debye, data[:, 0], data[:, 1], method='trf', verbose=0)
        print(field)
    else:
        popt, pcov = cf(double_debye, data[:, 0], data[:, 1], method='trf', verbose=2, p0=[50,10,200,10])
    leg_popt = [f"{ii:.1f}" for ii in popt]
    fitax.plot(data[:,0], double_debye(data[:, 0], *popt), label=f'fit: {field}')
    fitax.plot(data[:, 0], data[:, 1], label=f'raw: {field}')
    fitax.legend()

    difax.plot(data[:, 0], data[:, 1] - double_debye(data[:, 0], *popt), label=f'{field}')
    difax.legend()

    return popt
   

if __name__ == "__main__":
    _, ax = plt.subplots()
    if FITALL:
        fields = [0, 1, 3, 6, 9]
        _, dax = plt.subplots()
        results = {}
        for field in fields:
            filename = f"/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/04/1/data_{field}T.dat"
            results[f"{field}T"] = list(fit(filename, ax, dax))
        P(filename).parent.joinpath('fit_params.txt').write_text(repr(results))
    else:
        fields = [3, 6, 9]
        filename = f"/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/04/1/data_1T.dat"
        params = P(filename).parent.joinpath("fit_params.txt").read_text()
        popt = ast.literal_eval(params)["1T"]
        _, dat = read(filename)
        f = interp1d(dat[:, 0], dat[:, 1])
        for field in fields: 
            # popt = ast.literal_eval(params)[f"{field}T"]
            filename = f"/Users/Brad/Library/Containers/com.eltima.cloudmounter.mas/Data/.CMVolumes/Brad Price/Research/Data/2021/04/1/data_{field}T.dat"
            _, data = read(filename)
            data = data[data[:, 0] <= dat[-1, 0]]
            bdata = f(data[:, 0])
            # ax.plot(data[:, 0], (data[:, 1]-double_debye(data[:, 0], *popt))/(double_debye(data[:,0], *popt))*100, label=f"{field}T")
            ax.plot(data[:, 0], (data[:, 1]-bdata)/bdata*100, label=f"{field}T")
        # ax.plot(data[:, 0], double_debye(data[:, 0], *popt), label="1T fit")
        ax.set_title(r"$T_{D_1}$=" + f"{popt[0]:.1f}, " + f"A={popt[1]:.1f}, " + r"$T_{D_2}$=" + f"{popt[2]:.1f}, B={popt[3]:.1f}")
        # ax.set_yticks([])
        for spine in ['top','right']:
            ax.spines[spine].set_visible(False)
        ax.legend()
        ax.set_xlabel('Temperature (K)')
        # ax.set_ylabel('$C_V$ (JK$^{-1}$mol$^{-1}$)')
        ax.set_ylabel('$\Delta C_P$ % change from 1T')
        # ax.set_yscale('log')
        ax.set_xscale('log')

    plt.show()
