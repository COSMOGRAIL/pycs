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




gridsize = 8
mincnt = 4





db = pycs.gen.util.readpickle(pklfilepath)

db = db.values()

db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones

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

medmagerrAs = np.array([item["medmagerrA"] for item in db])
medmagerrBs = np.array([item["medmagerrB"] for item in db])
medmagerrstack = np.vstack([medmagerrAs, medmagerrBs])
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



fig = plt.figure(figsize=(10, 3.8))



cmap = matplotlib.cm.get_cmap("rainbow")



ax = fig.add_subplot(1, 2, 1)	
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

stuff = ax.hexbin(abstruetds, maxmagerrs, C=pterms,
	vmin=5e-3, vmax=3.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=mincnt, norm=matplotlib.colors.LogNorm(),
	gridsize = gridsize
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "8%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = LogLocator(subs=range(10)))
cax.set_label("$P$", fontsize=14)


ax.set_xlabel("$|\Delta t_i|$ [day]", fontsize=12)
ax.set_ylabel("Phot. precision of fainter image [mag]", fontsize=12)
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)
#ax.set_ylim(4e-3, 2.7)
ax.annotate("5 x 4 months, 3-day cadence", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')


ax = fig.add_subplot(1, 2, 2)
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

stuff = ax.hexbin(abstruetds, maxmagerrs, C=subtdoffs/truetds,
	vmin=5e-3, vmax=3.0, cmap=cmap, reduce_C_function=rmsd,
	xscale = 'linear', yscale = 'log', mincnt=mincnt,
	norm=matplotlib.colors.LogNorm(),
	gridsize = gridsize
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "8%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = matplotlib.ticker.LogLocator(subs=range(10)))
cax.set_label(r"$\mathrm{RMS}((\widetilde{\Delta t_i} - \Delta t_i) / \Delta t_i)$", fontsize=14)
		
ax.set_xlabel("$|\Delta t_i|$ [day]", fontsize=12)
ax.set_ylabel("Phot. precision of fainter image [mag]", fontsize=12)
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)
#ax.set_ylim(4e-3, 2.7)
ax.annotate("5 x 4 months, 3-day cadence", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')





plt.tight_layout()
plt.show()



