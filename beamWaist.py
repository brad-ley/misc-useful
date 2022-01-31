import numpy as np


def focus(w0=20, wavelength=1.25, xLens=101.6, fLens=101.6):
    """focus.
    
    :param w0: incoming beam waist
    :param wavelength: same units as w0
    :param xLens: distance to lens element from entrance aperture (SU as w0)
    :param fLens: focal length of lens (SU as w0)

    :return: beam waist at focus for given lens parameters
    """
    rayleigh_range = np.pi * w0**2 / wavelength
    waist = w0 / np.sqrt((1 - xLens / fLens)**2 + (rayleigh_range / fLens)**2)
    return waist


if __name__ == "__main__":
    waist = focused_waist(w0=25)
    print(waist)
