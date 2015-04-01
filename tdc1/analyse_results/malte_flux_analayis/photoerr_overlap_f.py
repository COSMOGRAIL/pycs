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


print "do a search replace doupla - douplapla to switch me"




db = pycs.gen.util.readpickle(pklfilepath)

db = db.values()

db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones

# computing overlap (fucked up in db for truetd < 5, why why why ??? FUCK)
for item in db:
	item["overlap"] = item["nseas"] * np.clip(item["meanseaslen"] - abs(item["truetd"]), 0.0, item["meanseaslen"])

print "Starting with db length", len(db)


subname = "pycs_tdc1_spl-vanilla-doupla-full"

for item in db:
	item["isin"] = 0.0
	if subname + "_td" in item:
		item["isin"] = 1.0

db = [item for item in db if item["rung"] in [1, 2, 3]]

inilen = len(db)
#print "before outlier rejection: %i points" % (inilen)
#db = [item for item in db if np.fabs(item[subname + "_td"] - item["truetd"]) < 20.0]
#db = [item for item in db if "truth_overlap_days" in item]


#print "rejection of %i points" % (inilen - len(db))

#go on from here


isins = np.array([item["isin"] for item in db])
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

#######maxmagerrs = minmagerrs



#print minmagerrs
#print maxmagerrs

truetds = np.array([item["truetd"] for item in db])


abstruetds = np.fabs(truetds)
"""
subtds = np.array([item[subname + "_td"] for item in db])
subtderrs = np.array([item[subname + "_tderr"] for item in db])
	
subtdoffs = subtds - truetds
abssubtdoffs = np.fabs(subtdoffs)
chi2terms = (subtdoffs/subtderrs)**2
aterms = subtdoffs/truetds
aabsterms = subtdoffs/np.fabs(truetds)
pterms = subtderrs/np.fabs(truetds)
"""
	
#############



fig = plt.figure(figsize=(19, 6))





ax = fig.add_subplot(1, 3, 1)	

ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

ax.set_yscale('log', nonposy='clip')

cmap = matplotlib.cm.get_cmap("gnuplot2")
cmap = matplotlib.cm.get_cmap("rainbow")

stuff = ax.scatter(overlaps, maxmagerrs, s=30, c=isins, marker="o", lw=0, cmap=cmap, vmin=0.0, vmax=1.0)

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
#cax.set_label("$P_i$")
cax.set_label("Is in doupla (yes/no)")

ax.set_xlabel("Total overlap [day]")
ax.set_ylabel("Median photometric error of faint image [mag]")

ax.set_xlim(0, 1200)
ax.set_ylim(2e-3 ,8e-1)
ax.annotate("3-day cadence, 4-month seasons (rungs 1, 2, 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')



ax = fig.add_subplot(1, 3, 2)	

#cmap = matplotlib.cm.get_cmap("gnuplot2")

stuff = ax.hexbin(overlaps, maxmagerrs, C=isins,
	vmin=0.0, vmax=1.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=10,
	gridsize = 7
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
cax.set_label("$f$ of doupla")
		
ax.set_xlabel("Total overlap [day]")
ax.set_ylabel("Median photometric error of faint image [mag]")
ax.annotate("3-day cadence, 4-month seasons (rungs 1, 2, 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')





db = [item for item in db if item["rung"] in [2, 3]]

print len(db)

isins = np.array([item["isin"] for item in db])
overlaps = np.array([item["overlap"] for item in db])
medmagerrAs = np.array([item["medmagerrA"] for item in db])
medmagerrBs = np.array([item["medmagerrB"] for item in db])
medmagerrstack = np.vstack([medmagerrAs, medmagerrBs])
minmagerrs = np.min(medmagerrstack, axis=0)
maxmagerrs = np.max(medmagerrstack, axis=0)

truetds = np.array([item["truetd"] for item in db])
abstruetds = np.fabs(truetds)

ax = fig.add_subplot(1, 3, 3)	

#cmap = matplotlib.cm.get_cmap("gnuplot2")

stuff = ax.hexbin(abstruetds, maxmagerrs, C=isins,
	vmin=0.0, vmax=1.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=10,
	gridsize = 7
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "5%", pad="3%")
cax = plt.colorbar(stuff, cax)
cax.set_label("$f$ of doupla")
		
ax.set_xlabel("$|\Delta t_i|$")
ax.set_ylabel("Median photometric error of faint image [mag]")

ax.annotate("3-day cadence, 5 x 4-month seasons (rungs 2, 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')




"""

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
"""

plt.tight_layout()
plt.show()



