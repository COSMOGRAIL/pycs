import pycs
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


r = 5
samples = 1000
x = np.linspace(-r, r, samples)

y1 = norm.pdf(x, -2, 0.1)
y2 = norm.pdf(x, 2, 1)

plt.plot(x, y1, color="red")
plt.plot(x, y2, color="blue")

plt.plot(x, y1*y2, color="black")

	
plt.show()

