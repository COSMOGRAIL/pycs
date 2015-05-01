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

from scipy.stats import norm

pklfilepath = "malte_db.pkl"


def rmsd(delta):	
	return np.sqrt(np.mean(np.asarray(delta)**2.0))


def med(delta):
	return np.median(np.fabs(delta))
	

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


# Read xtrastats again, this was missing as well for truetd < 5 it seems
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

#db = [item for item in db if abs(item["truetd"]) >= 10.0]

db = [item for item in db if item["rung"] in [1, 2, 3]]

inilen = len(db)
print "before outlier rejection: %i points" % (inilen)
db = [item for item in db if np.fabs(item[subname + "_td"] - item["truetd"]) < 20.0]
#db = [item for item in db if "truth_overlap_days" in item]


print "rejection of %i points" % (inilen - len(db))

#go on from here

meansamplings = np.array([item["meansampling"] for item in db])
nseas = np.array([item["nseas"] for item in db])
nepochs = np.array([item["nepochs"] for item in db])
overlaps = np.array([item["overlap"] for item in db])
sizes = ((overlaps/1200.0)*50.0 + 10.0)**2.0


#plt.hist(sizes)
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

##########maxmagerrs = minmagerrs

#print minmagerrs
#print maxmagerrs

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



fig = plt.figure(figsize=(19, 10))
ax = fig.add_subplot(2, 3, 1)	

ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

ax.set_yscale('log', nonposy='clip')
ax.set_xscale('log', nonposy='clip')

cmap = matplotlib.cm.get_cmap("coolwarm")

#stuff = ax.scatter(minmagerrs, maxmagerrs, c=pterms, marker="o", lw=0, s=30, cmap=cmap, vmin=0.0, vmax=0.1)
#stuff = ax.scatter(minmagerrs, maxmagerrs, c=subtderrs, marker="o", lw=0, s=30, cmap=cmap, vmin=0.0, vmax=2.0)
stuff = ax.scatter(minmagerrs, maxmagerrs, c=subtdoffs, marker="o", lw=0, s=30, cmap=cmap, vmin=-10.0, vmax=10.0)


divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
#cax.set_label("$P_i$")
cax.set_label("$\widetilde{\Delta t_i} - \Delta t_i$ [day]")

ax.set_xlabel("Median photometric error of bright image [mag]")
ax.set_ylabel("Median photometric error of faint image [mag]")

ax.set_xlim(6e-4, 2e-1)
ax.set_ylim(2e-3 ,8e-1)

ax.annotate("PyCS spl, 3-day cadence, 4-month seasons", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')







ax = fig.add_subplot(2, 3, 4)	

ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

ax.set_yscale('log', nonposy='clip')

cmap = matplotlib.cm.get_cmap("gnuplot2")
cmap = matplotlib.cm.get_cmap("rainbow")

stuff = ax.scatter(overlaps, maxmagerrs, s=30, c=abssubtdoffs, marker="o", lw=0, cmap=cmap, vmin=0.01, vmax=10.0, norm=matplotlib.colors.LogNorm())
#stuff = ax.scatter(overlaps, maxmagerrs, s=30, c=pterms, marker="o", lw=0, cmap=cmap, vmin=0.0, vmax=0.1)

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = matplotlib.ticker.LogLocator(subs=range(10)))
#cax.set_label("$P_i$")
cax.set_label("$|\widetilde{\Delta t_i} - \Delta t_i|$ [day]")

ax.set_xlabel("Total overlap [day]")
ax.set_ylabel("Median photometric error of faint image [mag]")

ax.set_xlim(0, 1200)
ax.set_ylim(2e-3 ,8e-1)



ax = fig.add_subplot(2, 3, 2)	

stuff = ax.hexbin(minmagerrs, maxmagerrs, C=subtdoffs,
	vmin=0.0, vmax=5.0, cmap=cmap, reduce_C_function=rmsd,
	xscale = 'log', yscale = 'log', mincnt=10,
	gridsize = 10
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
cax.set_label("RMS $(\widetilde{\Delta t_i} - \Delta t_i)$ [day]")
		
ax.set_xlabel("Median photometric error of bright image [mag]")
ax.set_ylabel("Median photometric error of faint image [mag]")









ax = fig.add_subplot(2, 3, 5)	

stuff = ax.hexbin(overlaps, maxmagerrs, C=subtdoffs,
	vmin=0.0, vmax=5.0, cmap=cmap, reduce_C_function=rmsd,
	xscale = 'linear', yscale = 'log', mincnt=10,
	gridsize = 10
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
cax.set_label("RMS $(\widetilde{\Delta t_i} - \Delta t_i)$ [day]")
		
ax.set_xlabel("Total overlap [day]")
ax.set_ylabel("Median photometric error of faint image [mag]")




###### bonus with median instead of RMSD

ax = fig.add_subplot(2, 3, 3)	

stuff = ax.hexbin(minmagerrs, maxmagerrs, C=subtdoffs,
	vmin=0.0, vmax=5.0, cmap=cmap, reduce_C_function=med,
	xscale = 'log', yscale = 'log', mincnt=10,
	gridsize = 10
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
cax.set_label("median $|]\widetilde{\Delta t_i} - \Delta t_i|$ [day]")
		
ax.set_xlabel("Median photometric error of bright image [mag]")
ax.set_ylabel("Median photometric error of faint image [mag]")




ax = fig.add_subplot(2, 3, 6)	

stuff = ax.hexbin(overlaps, maxmagerrs, C=subtdoffs,
	vmin=0.0, vmax=5.0, cmap=cmap, reduce_C_function=med,
	xscale = 'linear', yscale = 'log', mincnt=10,
	gridsize = 10
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
cax.set_label("median $|\widetilde{\Delta t_i} - \Delta t_i|$ [day]")
		
ax.set_xlabel("Total overlap [day]")
ax.set_ylabel("Median photometric error of faint image [mag]")


plt.tight_layout()
plt.show()




#subtds = np.array([item[subname + "_td"] for item in seldb])


#print len(db)


#exit()

#db = [item for item in db if abs(item["truetd"]) > 10.0]

#db = [item for item in db if item["rung"] in [1, 2, 3]]

print len(db)
for (key, val) in db[0].items():
	if "pycs" not in key:
		print "%50s : %s" % (key, val)


#subtds = np.array([item[subname + "_td"] for item in seldb])


exit()
