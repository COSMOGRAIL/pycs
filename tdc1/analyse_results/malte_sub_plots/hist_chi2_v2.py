import pycs
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


rangea = 0.01
rangeb = 100

db = pycs.gen.util.readpickle("../db.pkl").values()
db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones
#db = [item for item in db if item["rung"] == 4]

colors = ["red", "blue", "green"]

def subhist(db, subname, subi):
	
	seldb = [item for item in db if subname + "_td" in item] # We keep only the entries that have this submission
	print subname, len(seldb)

	truetds = np.array([item["truetd"] for item in seldb])
	submtds = np.array([item[subname + "_td"] for item in seldb])
	submtderrs = np.array([item[subname + "_tderr"] for item in seldb])
	
	submtdoffs = submtds - truetds

	submtdreloffs = submtdoffs/submtderrs

	chi2 = np.sum(submtdreloffs**2) / len(seldb) 

	#plt.hist(submtdreloffs, bins=75, range=(-range, range), normed=True, histtype="step", color=colors[subi], label="%s: $\\chi^2$ = %.3f" % (subname, chi2))

	#plt.hist(submtdreloffs, bins=75, range=(-range, range), normed=True, histtype="step", color=colors[subi], label="%s" % (subname), lw=1.5)
	
	#plt.hist(np.fabs(submtdreloffs), bins=np.logspace(0.1, 10.0, 10), range=(rangea, rangeb), log=True, normed=False, histtype="step", color=colors[subi], label="%s" % (subname), lw=1.5)

	bins = np.logspace(np.log10(rangea), np.log10(rangeb), 50)
	#print bins
	plt.hist(np.fabs(submtdreloffs), bins=bins, range=(rangea, rangeb), log=True, histtype="step", color=colors[subi], label="%s: $\\chi^2$ = %.3f" % (subname, chi2), lw=1.5)


fig = plt.figure(figsize=(10, 10))
fig.subplots_adjust(bottom=0.15, top=0.95, left=0.08, right=0.95)

subnames = ["pycs_tdc1_d3cs-vanilla-dou-full", "pycs_tdc1_spl-vanilla-dou-full", "pycs_tdc1_sdi-vanilla-dou-full"]

for subi, subname in enumerate(subnames):
	subhist(db, subname, subi)

#x = np.linspace(rangea, rangeb, 1000)
#plt.plot(x, np.log10(norm.pdf(x, 0.0, 1.0)), color="black", label="Standard normal distribution")

#plt.title("All rungs")
plt.xlabel(r"$\left|\frac{\widetilde{\Delta t_i} - \Delta t_i}{\sigma_i}\right|$", fontsize=26)
plt.xlim(rangea, rangeb)
plt.ylim(0.5, 1000)

ax1 = plt.gca()
ax1.set_xscale('log', nonposy='clip')

plt.legend()
plt.show()
#plt.savefig("hist_chi2.pdf")

