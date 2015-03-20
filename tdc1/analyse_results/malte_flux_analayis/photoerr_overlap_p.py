import pycs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
from matplotlib.lines import Line2D
import os
from matplotlib.ticker import LogLocator

from scipy.stats import norm

pklfilepath = "malte_db.pkl"


def rmsd(delta):	
	return np.sqrt(np.mean(np.asarray(delta)**2.0))


def med(delta):
	return np.median(np.fabs(delta))


print "do a search replace doupla - douplapla to switch me"


"""

db = pycs.gen.util.readpickle("../db.pkl")

# Given that the flag "in_tdc1" has been fucked up (related to truetd > 5), we just overwrite it
# with its original meaning.
for rung in range(5):
	for pair in range(1, 1037):
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid]["in_tdc1"] = 0
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid]["in_tdc1"] = 1


# Read xtrastats again, it seems this was fucked up as well for truetd < 5 ... I'M FUCKING ANGRY
xtrastatsdir = "/users/mtewes/TDC/pycs_svn_tdc1/results_tdc1/xtrastats"

for rung in range(5):
	print rung
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)

		relfilepath = pycs.tdc.util.tdcfilepath(set="tdc1", rung=rung, pair=pair, skipset=False)
		pklpath = os.path.join(xtrastatsdir, relfilepath+".stats.pkl")
		if os.path.exists(pklpath):

			data = pycs.gen.util.readpickle(pklpath, verbose=False)
			db[pairid].update(data)
			
			if "nseas" not in data:
				print "no nseas", pairid
		
		else:
			print "prob with", pairid

pycs.gen.util.writepickle(db, pklfilepath)

"""

db = pycs.gen.util.readpickle(pklfilepath)

db = db.values()

db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones

# computing overlap (fucked up in db for truetd < 5, why why why ??? FUCK)
for item in db:
	item["overlap"] = item["nseas"] * np.clip(item["meanseaslen"] - abs(item["truetd"]), 0.0, item["meanseaslen"])

print "Starting with db length", len(db)


subname = "pycs_tdc1_spl-vanilla-doupla-full"

db = [item for item in db if subname + "_td" in item]


db = [item for item in db if item["rung"] in [2, 3]]

inilen = len(db)
print "before outlier rejection: %i points" % (inilen)

db = [item for item in db if np.fabs(item[subname + "_td"] - item["truetd"]) < 20.0]

print "rejection of %i points" % (inilen - len(db))



meansamplings = np.array([item["meansampling"] for item in db])
nseas = np.array([item["nseas"] for item in db])
nepochs = np.array([item["nepochs"] for item in db])
overlaps = np.array([item["overlap"] for item in db])
sizes = ((overlaps/1200.0)*50.0 + 10.0)**2.0


#plt.hist(overlaps)
#plt.show()
#exit()

medmagerrAs = np.array([item["medmagerrA"] for item in db])
medmagerrBs = np.array([item["medmagerrB"] for item in db])

#print medmagerrAs
#print medmagerrBs

medmagerrstack = np.vstack([medmagerrAs, medmagerrBs])

#print medmagerrstack.shape

minmagerrs = np.min(medmagerrstack, axis=0)
maxmagerrs = np.max(medmagerrstack, axis=0)


truetds = np.array([item["truetd"] for item in db])


abstruetds = np.fabs(truetds)

subtds = np.array([item[subname + "_td"] for item in db])
subtderrs = np.array([item[subname + "_tderr"] for item in db])
	
subtdoffs = subtds - truetds
abssubtdoffs = np.fabs(subtdoffs)
chi2terms = (subtdoffs/subtderrs)**2
aterms = subtdoffs/truetds
aabsterms = subtdoffs/np.fabs(truetds)
pterms = subtderrs/np.fabs(truetds)

	
#############



fig = plt.figure(figsize=(20, 11))



cmap = matplotlib.cm.get_cmap("rainbow")


ax = fig.add_subplot(2, 3, 1)	

ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

ax.set_yscale('log', nonposy='clip')

cmap = matplotlib.cm.get_cmap("rainbow")

stuff = ax.scatter(abstruetds, maxmagerrs, s=30, c=pterms, marker="o", lw=0, cmap=cmap, vmin=5e-3, vmax=3, norm=matplotlib.colors.LogNorm())

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = LogLocator(subs=range(10)))
cax.set_label("$P_i$")
#cax.ax.minorticks_on()
#minorticks = cax.norm(np.linspace(0.0, 1.0, 10))
#cax.ax.yaxis.set_ticks(minorticks, minor=True)

ax.set_xlabel("$|\Delta t_i|$ [day]")
ax.set_ylabel("Median photometric error of fainter image [mag]")

ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)
ax.annotate("3-day cadence, 5 x 4-month seasons (rungs 2 & 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')



ax = fig.add_subplot(2, 3, 2)	
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

stuff = ax.hexbin(abstruetds, maxmagerrs, C=pterms,
	vmin=5e-3, vmax=3.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=3, norm=matplotlib.colors.LogNorm(),
	gridsize = 8
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = LogLocator(subs=range(10)))
cax.set_label("mean($P_i$)")


ax.set_xlabel("$|\Delta t_i|$ [day]")
ax.set_ylabel("Median photometric error of fainter image [mag]")
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)


ax = fig.add_subplot(2, 3, 3)


# scatter plot of p_i in bins as a function of rms of residuals


a = subtderrs
b = np.fabs(subtdoffs) / subtderrs
nbins = 5

alims = np.logspace(-0.8, 1.4, nbins)
#alims = np.linspace(0.05, 10.0, nbins)
abincenters = 0.5 * (alims[1:] + alims[:-1])

bininds = np.digitize(a, alims)

#print alims

xvals = []
yvals = []
for i in range(0, nbins-1):

	#print i
	xvals.append(abincenters[i])
		
	isin = bininds == i+1
	
	#yvals.append(med(b[isin]))
	yvals.append(rmsd(b[isin]))
	
	
ax.set_xscale('log', nonposy='clip')
#ax.set_yscale('log', nonposy='clip')


for lim in alims:
	ax.axvline(lim, color="gray")

ax.scatter(a, b, s=10, c=pterms, marker="o", lw=0, cmap=cmap, vmin=5e-3, vmax=3, norm=matplotlib.colors.LogNorm())
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = LogLocator(subs=range(10)))
cax.set_label("$P_i$")

ax.set_ylim(0, 3.5)

ax.plot(xvals, yvals, "r-", lw=3)
ax.set_xlabel("$\delta_i$ [day]")
#ax.set_ylabel("$|\widetilde{\Delta t_i} - \Delta t_i| / \delta_i$")
ax.set_ylabel("RMS$(\widetilde{\Delta t_i} - \Delta t_i) / \delta_i$")




ax = fig.add_subplot(2, 3, 4)
ax.set_yscale('log', nonposy='clip')
stuff = ax.scatter(abstruetds, maxmagerrs, s=30, c=abssubtdoffs, marker="o", lw=0, cmap=cmap, vmin=0.01, vmax=10.0, norm=matplotlib.colors.LogNorm())


divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = matplotlib.ticker.LogLocator(subs=range(10)))
cax.set_label("$|\widetilde{\Delta t_i} - \Delta t_i|$ [day]")
		
ax.set_xlabel("$|\Delta t_i|$ [day]")
ax.set_ylabel("Median photometric error of fainter image [mag]")
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)






ax = fig.add_subplot(2, 3, 5)

stuff = ax.hexbin(abstruetds, maxmagerrs, C=subtdoffs,
	vmin=0.0, vmax=5.0, cmap=cmap, reduce_C_function=rmsd,
	xscale = 'linear', yscale = 'log', mincnt=10,
	gridsize = 6
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
cax.set_label("RMS $(\widetilde{\Delta t_i} - \Delta t_i)$ [day]")
		
ax.set_xlabel("$|\Delta t_i|$ [day]")
ax.set_ylabel("Median photometric error of fainter image [mag]")
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)




ax = fig.add_subplot(2, 3, 6)

stuff = ax.hexbin(abstruetds, maxmagerrs, C=subtdoffs/truetds,
	vmin=5e-3, vmax=3.0, cmap=cmap, reduce_C_function=rmsd,
	xscale = 'linear', yscale = 'log', mincnt=3,
	norm=matplotlib.colors.LogNorm(),
	gridsize = 8
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = matplotlib.ticker.LogLocator(subs=range(10)))
cax.set_label("RMS $((\widetilde{\Delta t_i} - \Delta t_i) / \Delta t_i)$ [day]")
		
ax.set_xlabel("$|\Delta t_i|$ [day]")
ax.set_ylabel("Median photometric error of fainter image [mag]")
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)





plt.tight_layout()
plt.show()



