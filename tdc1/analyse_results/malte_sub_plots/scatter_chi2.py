import pycs
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm



db = pycs.gen.util.readpickle("../db.pkl").values()
db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones
db = [item for item in db if abs(item["truetd"]) > 10.0]


#db = [item for item in db if item["rung"] == 0]


colors = ["red", "blue", "green"]


nbins = 10
binlims = np.linspace(-120, 120, nbins + 1)
bincenters = 0.5*(binlims[1:] + binlims[:-1])



def subplot(db, subname, subi):
	
	seldb = [item for item in db if subname + "_td" in item] # We keep only the entries that have this submission
	print subname, len(seldb), len(seldb)/1024.0

	truetds = np.array([item["truetd"] for item in seldb])
	abstruetds = np.fabs(truetds)
	subtds = np.array([item[subname + "_td"] for item in seldb])
	subtderrs = np.array([item[subname + "_tderr"] for item in seldb])
	
	subtdoffs = subtds - truetds
	
	chi2terms = subtdoffs/subtderrs
	chi2 = np.sum(chi2terms**2) / len(seldb) 

	aterms = subtdoffs/truetds
	aabsterms = subtdoffs/np.fabs(truetds)
	
	pterms = subtderrs / np.fabs(truetds)
	
	#print "a", np.mean(aterms)
	#print "a_abs", np.mean(aabsterms)
	
	digitized = np.digitize(truetds, binlims)
	binvals = [chi2terms[digitized == bini] for bini in range(1, len(binlims))]
	binstds = map(np.std, binvals)
	binmedians = map(np.median, binvals)
	binmeans = map(np.mean, binvals)

	plotwidth = (binlims[1] - binlims[0])/4			
	offset = (-1 + subi) * plotwidth - 0.5*plotwidth
	
				
	#plt.bar(binlims[:-1] + offset + subi*plotwidth, binmeans, yerr=binstds,
	plt.bar(bincenters + offset, binmeans, yerr=binstds,
		width=plotwidth, color=colors[subi], ecolor=colors[subi],
		error_kw={"capsize":2.5, "capthick":0.5, "markeredgewidth":0.5},
		edgecolor=colors[subi], alpha = 0.5, linewidth=0, label="%s" % (subname))
						
	
	plt.plot(truetds, chi2terms, "o", color=colors[subi], markeredgecolor="none", markeredgewidth=0, markersize=4, alpha=0.1, zorder=-10)
	
	#bla = plt.hist(aterms, log=True, bins=40, range=(-range, range), histtype="step", color=colors[subi], label="%s: $A$ = %.5f" % (subname, a))
	#plt.axvline(a, color = colors[subi], lw=1, ls="--")
	
	#plt.hist(submtdreloffs, bins=75, range=(-range, range), normed=True, histtype="step", label="%s: $\\chi^2$ = %.3f" % (subname, chi2))


fig = plt.figure(figsize=(10, 10))
fig.subplots_adjust(bottom=0.15, top=0.95, left=0.15, right=0.95)

subnames = ["pycs_tdc1_d3cs-vanilla-dou-full", "pycs_tdc1_spl-vanilla-dou-full", "pycs_tdc1_sdi-vanilla-dou-full"]


for subi, subname in enumerate(subnames):
	subplot(db, subname, subi)

for lim in binlims:
	plt.axvline(lim, color="black", alpha=0.2, zorder = -30)

#exit()
#x = np.linspace(-range, range, 1000)
#plt.plot(x, norm.pdf(x, 0.0, 1.0), color="black", label="Standard normal distribution")

#plt.title("All rungs")
plt.xlabel(r"$\Delta t_i$", fontsize=26)
plt.ylabel(r"$\frac{\widetilde{\Delta t_i} - \Delta t_i}{\sigma_i}$", fontsize=26)


#plt.xlim(-range, range)
plt.ylim(-4, 4)
plt.legend()
plt.show()
#plt.savefig("test.pdf")

