import matplotlib.pyplot as plt
import numpy as np

p2p = np.loadtxt('peak-to-peak.txt', skiprows=1, delimiter=', ')

plt.figure(1)
plt.plot(p2p[:, 0], p2p[:, 1])
plt.ylabel('Linewidth (G)')
plt.xlabel('Temperature (K)')
plt.title('BDPA linewidth vs. T')
plt.savefig('p2p.png')
plt.show()
