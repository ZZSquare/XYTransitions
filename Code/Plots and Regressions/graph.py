import matplotlib.pyplot as plt
import pandas as pd
from ExactSolution import Hamiltonianm

df1 = pd.read_csv("J=1.000 Bx=0.030 dB=0.010 BzMax=1.250 dt=2.000 gamma=3.000.csv")
df2 = pd.read_csv("J=1.000 Bx=0.050 dB=0.010 BzMax=1.250 dt=1.600 gamma=4.000.csv")
df3 = pd.read_csv("J=1.000 Bx=0.100 dB=0.010 BzMax=1.250 dt=0.900 gamma=5.000.csv")

#plt.plot(df1['Bz'], df1['mz'], 'r', df2['Bz'], df2['mz'], 'b', df3['Bz'], df3['mz'], 'g')
mzarray, bzarray = Hamiltonianm(1, 0.1)
plt.plot(df3['Bz'], df3['mz'], 'r', bzarray, mzarray, 'g--')
plt.xlabel('Bz Field Magnitude', fontsize=16)
plt.ylabel('mz', fontsize=16)
plt.text(0.08, 0.95, 'exact', fontsize=12)
plt.text(1, 0.9, 'simulator', fontsize=12)
plt.title('Bx = 0.10', fontsize=24)
plt.show()
plt.savefig('1.png')