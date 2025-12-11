import numpy as np
import matplotlib.pyplot as plt

rmin, rmax = 80, 120
f = lambda r1,r2: r1/(r1+r2)
x = 1.2**np.arange(0,60)
y = [f(r,rmin)-f(r,rmax) for r in x]

plt.figure(figsize=(4,4), dpi=240)
plt.plot(x,y,'-', label=f'R2min = {rmin},  R2max = {rmax}')
plt.xlabel('R1')
plt.ylabel('R1 / (R1+R2min) - R1 / (R1+R2max)')
plt.legend(loc='upper right')
plt.xscale('log')
plt.show()

print(f(10,80)-f(10,120))
print(f(100,80)-f(100,120))
