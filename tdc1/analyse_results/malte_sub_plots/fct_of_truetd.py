import pycs
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm



db = pycs.gen.util.readpickle("../db.pkl").values()
db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones
db = [item for item in db if abs(item["truetd"]) > 10.0]

#db = [item for item in db if item["rung"] == 0]

colors = ["red", "blue", "green"]

fig = plt.figure(figsize=(18, 6))
fig.subplots_adjust(bottom=0.15, top=0.95, left=0.1, right=0.97, wspace=0.23)

subnames = ["pycs_tdc1_d3cs-vanilla-doupla-full", "pycs_tdc1_spl-vanilla-doupla-full", "pycs_tdc1_sdi-vanilla-doupla-full"]

nbins = 10
binlims = np.linspace(-120, 120, nbins + 1)
bincenters = 0.5*(binlims[1:] + binlims[:-1])

ax1 = fig.add_subplot(121)

ax2 = fig.add_subplot(122)


for subi, subname in enumerate(subnames):
	seldb = [item for item in db if subname + "_td" in item] # We keep only the entries that have this submission
	print subname, len(seldb)

	truetds = np.array([item["truetd"] for item in seldb])
	abstruetds = np.fabs(truetds)
	subtds = np.array([item[subname + "_td"] for item in seldb])
	subtderrs = np.array([item[subname + "_tderr"] for item in seldb])
	
	subtdoffs = subtds - truetds
	chi2terms = (subtdoffs/subtderrs)**2
	aterms = subtdoffs/truetds
	aabsterms = subtdoffs/np.fabs(truetds)
	pterms = subtderrs/np.fabs(truetds)
	
	#print "A", np.mean(aterms), np.std(aterms)/np.sqrt(len(truetds))
	#print "P", np.mean(pterms), np.std(pterms)/np.sqrt(len(truetds))
	#print "Chi2", np.mean(chi2terms), np.std(chi2terms)/np.sqrt(len(truetds))
	#print "a_abs", np.mean(aabsterms)
	
	digitized = np.digitize(truetds, binlims)
	
	# Accuracy

	binvals = [aterms[digitized == bini] for bini in range(1, len(binlims))]
	binstds = map(np.std, binvals)
	binerrs = binstds/np.sqrt(map(len, binvals))
	binmedians = map(np.median, binvals)
	binmeans = map(np.mean, binvals)

	ax1.plot(bincenters, binmeans, ls="-", color=colors[subi], label="%s, $A = %.5f \\pm %.5f$" % (subname, np.mean(aterms), np.std(aterms)/np.sqrt(len(aterms))), lw=2)
	ax1.plot(bincenters, binmeans+binerrs, ls="--", color=colors[subi], lw=1)
	ax1.plot(bincenters, binmeans-binerrs, ls="--", color=colors[subi], lw=1)
	#ax1.plot(truetds, aterms, "o", color=colors[subi], markeredgecolor="none", markeredgewidth=0, markersize=4, alpha=0.1, zorder=-10)
	
	
	# Chi2
	
	binvals = [chi2terms[digitized == bini] for bini in range(1, len(binlims))]
	binstds = map(np.std, binvals)
	binerrs = binstds/np.sqrt(map(len, binvals))
	binmedians = map(np.median, binvals)
	binmeans = map(np.mean, binvals)

	ax2.plot(bincenters, binmeans, ls="-", color=colors[subi], label="%s, $\\chi^2 = %.5f \\pm %.5f$" % (subname, np.mean(chi2terms), np.std(chi2terms)/np.sqrt(len(aterms))), lw=2)
	ax2.plot(bincenters, binmeans+binerrs, ls="--", color=colors[subi], lw=1)
	ax2.plot(bincenters, binmeans-binerrs, ls="--", color=colors[subi], lw=1)
	#ax2.plot(truetds, chi2terms, "o", color=colors[subi], markeredgecolor="none", markeredgewidth=0, markersize=4, alpha=0.1, zorder=-10)

	#plotwidth = (binlims[1] - binlims[0])/4			
	#offset = (-1 + subi) * plotwidth - 0.5*plotwidth
				
	#plt.bar(binlims[:-1] + offset + subi*plotwidth, binmeans, yerr=binstds,

	#plt.bar(bincenters + offset, binmeans, yerr=binerrs,
	#	width=plotwidth, color=colors[subi], ecolor=colors[subi],
	#	error_kw={"capsize":2.5, "capthick":0.5, "markeredgewidth":0.5},
	#	edgecolor=colors[subi], alpha = 0.5, linewidth=0, label="%s" % (subname))
					
	#
	#bla = plt.hist(aterms, log=True, bins=40, range=(-range, range), histtype="step", color=colors[subi], label="%s: $A$ = %.5f" % (subname, a))
	#plt.axvline(a, color = colors[subi], lw=1, ls="--")
	
	#plt.hist(submtdreloffs, bins=75, range=(-range, range), normed=True, histtype="step", label="%s: $\\chi^2$ = %.3f" % (subname, chi2))


for lim in binlims:
	ax1.axvline(lim, color="black", alpha=0.2, zorder = -30)
	ax2.axvline(lim, color="black", alpha=0.2, zorder = -30)

	
ax1.axhline(0.0, color="black", zorder = -30, lw=1)
ax2.axhline(1.0, color="black", zorder = -30, lw=1)

#exit()
#x = np.linspace(-range, range, 1000)
#plt.plot(x, norm.pdf(x, 0.0, 1.0), color="black", label="Standard normal distribution")

#plt.title("All rungs")
ax1.set_xlabel(r"$\Delta t_i$", fontsize=26)
#plt.ylabel(r"$\frac{\widetilde{\Delta t_i} - \Delta t_i}{\sigma_i}$", fontsize=26)
ax1.set_ylabel(r"$\frac{\widetilde{\Delta t_i} - \Delta t_i}{\Delta t_i}$", fontsize=26)

ax2.set_xlabel(r"$\Delta t_i$", fontsize=26)
#plt.ylabel(r"$\frac{\widetilde{\Delta t_i} - \Delta t_i}{\sigma_i}$", fontsize=26)
ax2.set_ylabel(r"$\left(\frac{\widetilde{\Delta t_i} - \Delta t_i}{\sigma_i}\right)^{2}$", fontsize=26)


ax2.set_ylim(1e-2, 1e2)
ax2.set_yscale('log', nonposy='clip')


#plt.xlim(-range, range)
#plt.ylim(-4, 4)
ax1.legend()
ax2.legend()
plt.show()
#plt.savefig("test.pdf")

