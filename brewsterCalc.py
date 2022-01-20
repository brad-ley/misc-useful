import ast
import os
from pathlib import Path as P
from pathlib import PurePath as PP

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

from readDataFile import read

WAFER_INDEX = 3.425
WAVELENGTH = 1.25  # mm
PLOT_NUM = 3


def brewster():
    """ 
    Want to look at Gaussian beam approaching silicon wafer and see 
    how much more of our beam power we will lose by reducing the beam waist
    to shrink the silicon wafer in new pulse slicer
    """
    fig = plt.figure(figsize=(8, 3))
    global n, r

    slide_min = 1    # the minimial value of the paramater a
    slide_max = 5   # the maximal value of the paramater a
    a_init = 1   # the value of the parameter a to be used initially, when the graph is created

    # first we create the general layount of the figure
    # with two axes objects: one for the plot of the function
    # and the other for the slider
    main_ax = plt.axes([0.15, 0.25, 0.75, 0.65])
    slider_ax = plt.axes([0.15, 0.05, 0.75, 0.03])

    n = 1 / WAFER_INDEX  # air to silicon, not silicon to air so flip the ratio
    theta = np.linspace(0, 90, 1000) * np.pi / 180

    def r(n, theta):
        return (n * (1 - n**2 * np.sin(theta)**2)**(1 / 2) - np.cos(theta)) / \
            (n * (1 - n**2 * np.sin(theta)**2)**(1 / 2) + np.cos(theta))

    # in plot_ax we plot the function with the initial value of the parameter a
    plt.axes(main_ax)  # select sin_ax
    plt.title('Reflectivity (ratio)')
    real, = plt.plot(theta * 180 / np.pi, np.real(r(n, theta)))
    plt.plot(theta * 180 / np.pi, np.zeros(len(theta)), 'k--')
    # imag, = plt.plot(x, np.imag(cpx))
    # mag, = plt.plot(x, np.abs(cpx))
    # plt.xlim(np.min(x), np.max(x))
    plt.ylabel('$r$')
    plt.xlabel('Angle of incidence ($\phi$)')

    # here we create the slider
    a_slider = Slider(slider_ax,      # the axes object containing the slider
                      r'$n$',            # the name of the slider parameter
                      slide_min,          # minimal value of the parameter
                      slide_max,          # maximal value of the parameter
                      valinit=a_init  # initial value of the parameter
                      )

    def update(n):
        real.set_ydata(r(1 / n, theta))
        fig.canvas.draw_idle()

    a_slider.on_changed(update)
    plt.show()

    return plt


def fieldSim(w0=[9, 15], zr=100, wafer_radius=-1, plot=True):
    """
    Calculations come from https://www.osapublishing.org/DirectPDFAccess/032B85F9-0A0E-48A9-A9E623E5E6B70771_8477/ol-10-8-378.pdf?da=1&id=8477&seq=0&mobile=no
    Returns reflectance as a function of incident angle around Brewster's
    Fundamental waist of FEL is 9 mm
    """
    def r(n, theta):
        return (n * (1 - n**2 * np.sin(theta)**2)**(1 / 2) - np.cos(theta)) / \
            (n * (1 - n**2 * np.sin(theta)**2)**(1 / 2) + np.cos(theta))
    n = 1 / WAFER_INDEX
    tB = np.arctan(1 / n)
    # tB = np.arctan(1 / n) + 0.1 * np.pi / 180
    steps = 10000
    theta = np.linspace(0, 90, steps)
    ti = np.linspace(tB * 180 / np.pi - 10, tB * 180 /
                     np.pi + 10, steps) * np.pi / 180

    def F(n, tB, w0):
        tbidx = np.where(theta > tB * 180 / np.pi)[0][0]

        result = np.abs(r(n, tB) + np.diff(r(n, theta), n=1)[tbidx] * (ti - tB)
                        + 1 / 2 * np.diff(r(n, theta), n=2)[tbidx] * (ti - tB) **
                        2) * (2 * np.pi / WAVELENGTH * w0 ** 2 / (2 * zr)) ** (1
                                                                               / 2) * np.exp(-(2 * np.pi / WAVELENGTH * w0 / 2
                                                                                               )**2 * (ti - tB)**2)

        if wafer_radius != -1:
            dx = zr * (ti - tB)
            result *= (np.abs(dx) <= wafer_radius)

        return result

    data = {}

    if isinstance(w0, int):
        w0 = [w0]

    if plot:
        plt.figure('Gaussian beam reflectance')
        add = ''

        if wafer_radius != -1:
            add += '\n' + r'($r_{waf}=$' + f'{wafer_radius} mm, $z_r=${zr} mm)'

        w_use = []

        if len(w0) > PLOT_NUM:
            for i in list(range(0, len(w0), len(w0) // PLOT_NUM)):
                w_use.append(w0[i])

    for w in w0:
        data[w] = np.column_stack((ti * 180 / np.pi, F(n, tB, w)))

        if plot:
            if w in w_use:
                plt.plot(data[w][:, 0], data[w][:, 1] **
                         2, label=f"$w_0=${w:.1f} mm")

    if plot:
        plt.xlabel(r'$\theta_i$')
        plt.ylabel('Reflectance')
        plt.title(r'Gaussian beam reflectance at $\theta_B$' + add)
        plt.legend()
        plt.tight_layout()

    return data


def internal_reflections(data, thickness=-1, wafer_radius=-1, zr=100):
    """
    Computes power reflected by integrating through incident angles while taking
    into account the weight of each angle and the thickness of silicon wafer
    pg 603 from Zangwill E&M
    """

    def powerTransmitted(R, thickness, theta_trans):
        return 1 / (1 + 4 * R / (1 - R**2) * np.sin(WAFER_INDEX * 2 * np.pi / WAVELENGTH * thickness * np.cos(theta_trans))**2)

    if thickness == -1:
        thickness = 190.101

    plt.figure('Reflected power')
    integ_pR = {}
    w_use = []
    w0 = list(data.keys())

    if len(w0) > PLOT_NUM:
        for i in list(range(0, len(w0), len(w0) // PLOT_NUM)):
            w_use.append(w0[i])

    tB = np.arctan(WAFER_INDEX)

    for key in data:
        theta = data[key][:, 0] * np.pi / 180
        r = data[key][:, 1]
        R = r**2
        theta_trans = np.arcsin(np.sin(theta) / WAFER_INDEX)
        pT = powerTransmitted(R, thickness, theta_trans)

        if wafer_radius != -1:
            dx = zr * (theta - tB)
            pT *= (np.abs(dx) <= wafer_radius)
        pR = 1 - pT
        integ_pR[key] = np.trapz(pT)

        if key in w_use:
            plt.plot(data[key][:, 0], pT, label=f"$w_0=${key:.1f} mm")

    add = ''

    if wafer_radius != -1:
        add += '\n' + r' ($r_{waf}=$' + f'{wafer_radius} mm)'

    plt.ylabel('Power (arb. u)')
    plt.xlabel(r'$\theta_i$')
    plt.title(r'Reflected power vs. $\theta_i$' + add)
    plt.legend()
    plt.tight_layout()

    plt.figure('Power trans. vs. waist')

    ### START OF: want to compute baseline to compare new setup to ###
    cur = 10  # 10 mm radius coming out of horn
    cur_zr = 125
    d = fieldSim(w0=cur, zr=cur_zr, wafer_radius=-1, plot=False)
    theta = d[cur][:, 0] * np.pi / 180
    r = d[cur][:, 1]
    R = r**2
    theta_trans = np.arcsin(np.sin(theta) / WAFER_INDEX)
    pT = powerTransmitted(R, thickness, theta_trans)
    pR = 1 - pT
    integ_pR[-1] = np.trapz(pT)
    ### END OF: want to compute baseline to compare new setup to ###

    for key, val in integ_pR.items():
        if key == -1:
            c = 'r'
            leg = r'current switch setup ($r_{waf}=\infty$' + \
                f', $z_r=${cur_zr} mm)'
            plt.scatter(float(cur), (float(val) - float(integ_pR[-1])) * 100 /
                        float(integ_pR[-1]), c=c, label=leg)
        else:
            c = 'k'
            leg = ''
            plt.scatter(float(key), (float(val) - float(integ_pR[-1])) * 100 /
                        float(integ_pR[-1]), c=c, label=leg)

    plt.ylabel('% change')
    plt.xlabel('Beam waist (mm)')
    plt.title('Power lost compared to old design vs. $w_0$' + add)
    plt.legend()
    plt.tight_layout()


if __name__ == "__main__":
    # brewster()
    """
    Stuff to do:
    -properly treat tranmission to incorporate size of the beam
    -the waist upon tranmission is NOT the waist we are interested in controlling
        -need to use Nick's LabVIEW software to figure out the true waist as a function of input radius
        -input radius was CAN control
    """
    WAFER_RADIUS = 50
    PROP_DISTANCE = 100
    data = fieldSim(w0=np.linspace(5, 25, 41),
                    zr=PROP_DISTANCE, wafer_radius=WAFER_RADIUS)
    internal_reflections(data, thickness=-1,
                         zr=PROP_DISTANCE, wafer_radius=WAFER_RADIUS)
    plt.show()
