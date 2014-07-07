import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from itertools import cycle

matplotlib.rcParams.update({'font.size': 15})

df = pd.read_csv("metrics.csv").dropna(how='any')
df = df[df["team"] == "Tewes"]

fig = plt.figure(figsize=(15, 10))
fig.subplots_adjust(bottom=0.10, top=0.95, left=0.10, right=0.95)
marker = cycle(["o", "^", "<", ">", "h", "d", "s", "p"])

teams = sorted(list(set(df["team"].values)))[::-1]
sels = list(set(df["algorithm"].values))

sels = ["d3cs-vanilla-dou-full", "spl-vanilla-dou-full", "sdi-vanilla-dou-full"]

#sels = ["_spl-vanilla-dou-full", "_spl-k1.5-dou-full", "_spl-ml0.5-dou-full"]

#sels = ["_spl-vanilla-dou-full", "_spl-vanilla-dou-P3percent", "_spl-vanilla-dou-800bestP"]
#sels = ["spl-vanilla-dou-full", "spl-vanilla-doupla-full"]

#sels = ["spl-median-doupla-splagree"]

#sels = ["d3cs-vanilla-dou-full", "d3cs-vanilla-doupla-full"]


for sel in sels:
	seldf = df[[sel in algo for algo in df["algorithm"]]]
	x = np.log10(seldf["chi2"].values)
	y = seldf["f"].values
	c = np.abs(seldf["A"].values)
	print sel, len(x) 
	#sc = plt.scatter(x=x, y=y, c=c, s=100, vmin=0.00005, vmax=0.01, marker=next(marker), edgecolor="None", label="PyCS: "+sel, norm=matplotlib.colors.LogNorm())
	sc = plt.scatter(x=x, y=y, c=c, s=100, vmin=0.0001, vmax=1.0, marker=next(marker), edgecolor="None", label="PyCS: "+sel, norm=matplotlib.colors.LogNorm())
	
	
	
	for (i, sub) in seldf.iterrows():
		s = "%i" % (sub["rung"])
		pos = np.array([np.log10(sub["chi2"]), sub["f"]])
		plt.annotate(s,
			pos, xycoords='data', 
			xytext=(5, 5), textcoords='offset points')

ax = plt.gca()
ax.axvline(x=0.0, zorder=-20, color="black")
plt.xlim(-3, 7)
plt.ylim(0, 1)
cb = plt.colorbar()
cb.set_label(r'|A|', fontsize=26)
plt.xlabel(r"log$_{10} (\chi^2)$", fontsize=26)
plt.ylabel("f", fontsize=26)
plt.legend(scatterpoints=1)
plt.show()
