import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from itertools import cycle
#import networkx as nx

matplotlib.rcParams.update({'font.size': 15})

df = pd.read_csv("metrics.csv").dropna(how='any')
df = df[df["rung"] == 0]

fig = plt.figure(figsize=(15, 10))
fig.subplots_adjust(bottom=0.10, top=0.95, left=0.10, right=0.95)
marker = cycle(["o", "^", "<", ">", "h", "d", "s", "p"])

teams = sorted(list(set(df["team"].values)))[::-1]
for team in teams:
	
	x = np.log10(df[df["team"] == team]["chi2"].values)
	y = df[df["team"] == team]["f"].values
	c = np.abs(df[df["team"] == team]["A"].values) 

	#plt.plot(x, y, marker=next(marker), markeredgewidth=0, markersize=10, linestyle="None", label=team)
	sc = plt.scatter(x=x, y=y, c=c, s=70, vmin=0.0001, vmax=1.0, marker=next(marker), label=team, norm=matplotlib.colors.LogNorm())

	# , edgecolors="None",

sel = df[(df["team"] == "Tewes") & ["spl" in algo for algo in df["algorithm"]]]

"""
xs = np.log10(sel["chi2"].values)
ys = np.array(sel["f"].values)
poss = np.vstack([xs, ys]).transpose()
center = np.mean(poss, axis=0)
print center
vects = poss - center
mods = np.hypot(vects[:,0], vects[:,1])
vects[:,0] *= np.mean(mods)/mods
vects[:,1] *= np.mean(mods)/mods
print vects.shape
"""

for (i, sub) in sel.iterrows():

	s = "-".join(sub["algorithm"].split("_")[2].split("-")[:])
	pos = np.array([np.log10(sub["chi2"]), sub["f"]])
	#vect = pos - center
	
	disp = 3.0*np.random.randn(2)
	#print i
	#print pos - vects[i,:]
	
	plt.annotate(s,
		pos, xycoords='data', 
		xytext=pos, textcoords='data'),
		#arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))


ax = plt.gca()
ax.axvline(x=0.0, zorder=-20, color="black")
#ax.set_yscale('log')
#ax.set_xscale('log')
plt.xlim(-3, 7)
plt.ylim(0, 1)
cb = plt.colorbar()
cb.set_label(r'|A|', fontsize=26)
plt.xlabel(r"log$_{10} (\chi^2)$", fontsize=26)
plt.ylabel("f", fontsize=26)
plt.legend(scatterpoints=1)
plt.show()
