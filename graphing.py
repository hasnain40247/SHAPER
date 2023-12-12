## A simple graphing script to see how mutation rate changes with different parameters.
from matplotlib import pyplot as plt
import random

eta = 0.9
gamma = 0.1
idx = 0

etas = []
gammas = []

while True:
    eta = eta*0.95
    gamma = gamma*0.9
    
    eta = max(eta, 0.5)
    gamma = max(gamma, 0.001)
    idx += 1

    etas.append(eta)
    gammas.append(gamma)

    if idx%(75+random.randint(1, 20)) == 0 and random.random() > 0.6:
        eta = eta*2
        eta = max(eta, 0.9)

        gamma = gamma*2
        gamma = max(gamma, 0.1)


    if idx > 350:
        break

plt.plot(gammas)
plt.show()
plt.plot(etas)
plt.show()

