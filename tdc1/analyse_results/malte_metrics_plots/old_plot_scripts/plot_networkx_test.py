import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from itertools import cycle
import networkx as nx

matplotlib.rcParams.update({'font.size': 15})

df = pd.read_csv("metrics.csv").dropna(how='any')


fig = plt.figure(figsize=(15, 10))
fig.subplots_adjust(bottom=0.10, top=0.95, left=0.10, right=0.95)
marker = cycle(["^", "<", ">", "h", "d", "s", "p", "o"])

teams = sorted(list(set(df["team"].values)))
for team in teams:
	
	x = np.log10(df[df["team"] == team]["chi2"].values)
	y = df[df["team"] == team]["f"].values
	c = np.abs(df[df["team"] == team]["A"].values) 

	#plt.plot(x, y, marker=next(marker), markeredgewidth=0, markersize=10, linestyle="None", label=team)
	sc = plt.scatter(x=x, y=y, c=c, s=70, vmin=0.0001, vmax=1.0, marker=next(marker), label=team, norm=matplotlib.colors.LogNorm())

	# , edgecolors="None",


G=nx.Graph()
data_nodes = []
init_pos = {}

pycs = df[df["team"] == "Tewes"]
for (i, sub) in pycs.iterrows():
	
	#print sub
	s = "-".join(sub["algorithm"].split("_")[2].split("-")[:])
	(x, y) = (np.log10(sub["chi2"]), sub["f"])
	data_str = 'data_{0}'.format(i)
	ano_str = 'ano_{0}'.format(i)
	 
	G.add_node(data_str)
	G.add_node(ano_str)
	G.add_edge(data_str, ano_str)
	data_nodes.append(data_str)
	init_pos[data_str] = (x, y)
	init_pos[ano_str] = (x, y)

pos = nx.spring_layout(G, pos=init_pos, fixed=data_nodes)

for (i, sub) in pycs.iterrows():

	s = "-".join(sub["algorithm"].split("_")[2].split("-")[:])
	(x, y) = (np.log10(sub["chi2"]), sub["f"])
	data_str = 'data_{0}'.format(i)
	ano_str = 'ano_{0}'.format(i)
    
	plt.annotate(s,
		(x, y), xycoords='data', 
		xytext=pos[ano_str], textcoords='data',
		arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))


ax = plt.gca()
ax.axvline(x=1.0, zorder=-20, color="black")
#ax.set_yscale('log')
#ax.set_xscale('log')
plt.xlim(-3, 7)
plt.ylim(0, 1)
cb = plt.colorbar()
cb.set_label(r'|A|', fontsize=26)
plt.xlabel(r"log$_10 (\chi^2)$", fontsize=26)
plt.ylabel("f", fontsize=26)
plt.legend(scatterpoints=1)
plt.show()
