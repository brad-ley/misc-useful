import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

def plot(fig, x, cpx, xlabel='Field (T)'):
    
    global cpxx
    cpxx = np.copy(cpx)

    slide_min = 0    # the minimial value of the paramater a
    slide_max = 180   # the maximal value of the paramater a
    a_init = 0   # the value of the parameter a to be used initially, when the graph is created

# first we create the general layount of the figure
# with two axes objects: one for the plot of the function
# and the other for the slider
    sin_ax = plt.axes([0.15, 0.2, 0.75, 0.65])
    slider_ax = plt.axes([0.15, 0.05, 0.75, 0.05])


# in plot_ax we plot the function with the initial value of the parameter a
    plt.axes(sin_ax) # select sin_ax
    plt.title('Averaged and demodulated')
    real, = plt.plot(x, np.real(cpx))
    imag, = plt.plot(x, np.imag(cpx))
    mag, = plt.plot(x, np.abs(cpx))
    plt.xlim(np.min(x), np.max(x))
    plt.ylabel('Signal (arb. u)')
    plt.xlabel(xlabel)

# here we create the slider
    a_slider = Slider(slider_ax,      # the axes object containing the slider
                      r'$\phi$',            # the name of the slider parameter
                      slide_min,          # minimal value of the parameter
                      slide_max,          # maximal value of the parameter
                      valinit=a_init  # initial value of the parameter
                     )

    def update(phi):
        dat = np.copy(cpxx)
        dat *= np.exp(1j * 2 * np.pi * phi / 180)
        real.set_ydata(np.real(dat))
        imag.set_ydata(np.imag(dat))
        fig.canvas.draw_idle()

    a_slider.on_changed(update)
    plt.show()
    return plt
