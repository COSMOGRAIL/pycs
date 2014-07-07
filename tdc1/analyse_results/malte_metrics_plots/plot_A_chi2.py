import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from itertools import cycle

matplotlib.rcParams.update({'font.size': 15})

df = pd.read_csv("metrics.csv").dropna(how='any')
df = df[df["rung"] == 0]
#df = df[np.fabs(df["f"] - 0.25) <= 0.05 ]
df = df[df["f"] > 0.3]

fig = plt.figure(figsize=(15, 10))
fig.subplots_adjust(bottom=0.10, top=0.95, left=0.10, right=0.95)
marker = cycle(["o", "^", "<", ">", "h", "d", "s", "p"])

teams = sorted(list(set(df["team"].values)))[::-1]
#sels = list(set(df["algorithm"].values))

#sels = ["d3cs-vanilla-dou-full", "spl-vanilla-dou-full", "sdi-vanilla-dou-full"]

#sels = ["_spl-vanilla-dou-full", "_spl-k1.5-dou-full", "_spl-ml0.5-dou-full"]

#sels = ["_spl-vanilla-dou-full", "_spl-vanilla-dou-P3percent", "_spl-vanilla-dou-800bestP"]
#sels = ["spl-vanilla-dou-full", "spl-vanilla-doupla-full"]

#sels = ["spl-median-doupla-splagree"]

#sels = ["d3cs-vanilla-dou-full", "d3cs-vanilla-doupla-full"]


for team in teams:
#for sel in sels:
	#seldf = df[[sel in algo for algo in df["algorithm"]]]
	seldf = df[df["team"] == team]
	
	#x = np.log10(seldf["chi2"].values)
	x = seldf["chi2"].values
	xerr = seldf["chi2err"].values
	y = np.abs(seldf["A"].values)
	yerr = seldf["Aerr"].values
	c = seldf["P"].values
	#print sel, len(x) 
	#sc = plt.scatter(x=x, y=y, c=c, s=100, vmin=0.00005, vmax=0.01, marker=next(marker), edgecolor="None", label="PyCS: "+sel, norm=matplotlib.colors.LogNorm())
	plt.errorbar(x,y,xerr=xerr, yerr=yerr, linestyle="None", ecolor="gray", color="black", zorder = 1, capsize=0)
	
	sc = plt.scatter(x=x, y=y, c=c, s=100, vmin=0.001, vmax=1.0, marker=next(marker), zorder = 2, label=team, norm=matplotlib.colors.LogNorm())
	
	
	
	for (i, sub) in seldf.iterrows():
		#s = "%i" % (sub["rung"])
		s = "%s" % (sub["algorithm"])
		offset = np.random.uniform(-30, 30, 2)
		#print offset
		pos = np.array([sub["chi2"], abs(sub["A"])])
		plt.annotate(s,
			pos, xycoords='data', 
			xytext=(5,5), textcoords='offset points', fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="gray", alpha=0.1, ec="b", lw=1))
		#arrowprops=dict(arrowstyle="-",connectionstyle="arc3")

ax = plt.gca()
ax.axvline(x=0.0, zorder=-20, color="black")
ax.set_yscale('log', nonposy='clip')
ax.set_xscale('log', nonposx='clip')
plt.xlim(1e-3, 4e6)
plt.ylim(1e-5, 1e0)
cb = plt.colorbar()
cb.set_label(r'$P$', fontsize=26)
plt.xlabel(r"$\chi^2$", fontsize=26)
plt.ylabel(r"$|A|$", fontsize=26)
plt.legend(scatterpoints=1, loc='lower right')
plt.show()
