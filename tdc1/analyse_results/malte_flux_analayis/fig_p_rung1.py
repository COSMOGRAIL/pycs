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

def meanbest(pi):
	if len(np.asarray(pi)) < 3:
		return 0.0
	
	#print pi
	medpi = np.median(pi)
	#print medpi
	#print pi <= medpi
	return np.mean(np.asarray(pi)[np.asarray(pi) <= medpi])

def rmsbest(delta):

	squares = np.asarray(delta)**2.0
	med = np.median(squares)
	
	return np.sqrt(np.mean(np.asarray(squares)[squares <= med]))



gridsize = 8
mincnt = 4


txt = "10 x 4 months, 3-day cadence"



db = pycs.gen.util.readpickle(pklfilepath)

db = db.values()

db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones

print "Starting with db length", len(db)


subname = "pycs_tdc1_spl-vanilla-doupla-full"

db = [item for item in db if subname + "_td" in item]


db = [item for item in db if item["rung"] in [1]]

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



#plt.hist(abstruetds)
#plt.show()

#exit()


fig = plt.figure(figsize=(10.2, 7.6))



cmap = matplotlib.cm.get_cmap("rainbow")



ax = fig.add_subplot(2, 2, 1)	
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

stuff = ax.hexbin(abstruetds, maxmagerrs, C=pterms,
	vmin=5e-3, vmax=1.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=mincnt, norm=matplotlib.colors.LogNorm(),
	gridsize = gridsize
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "8%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = LogLocator(subs=range(10)))
cax.set_label("$P$", fontsize=14)


ax.set_xlabel("$|\Delta t|$ [day]", fontsize=12)
ax.set_ylabel("Phot. precision of fainter image [mag]", fontsize=12)
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)
#ax.set_ylim(4e-3, 2.7)
ax.annotate(txt, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')


ax = fig.add_subplot(2, 2, 2)
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

stuff = ax.hexbin(abstruetds, maxmagerrs, C=subtdoffs/truetds,
	vmin=5e-3, vmax=1.0, cmap=cmap, reduce_C_function=rmsd,
	xscale = 'linear', yscale = 'log', mincnt=mincnt,
	norm=matplotlib.colors.LogNorm(),
	gridsize = gridsize
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "8%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = matplotlib.ticker.LogLocator(subs=range(10)))
cax.set_label(r"$\mathrm{RMS}((\widetilde{\Delta t_i} - \Delta t_i) / \Delta t_i)$", fontsize=14)
		
ax.set_xlabel("$|\Delta t|$ [day]", fontsize=12)
ax.set_ylabel("Phot. precision of fainter image [mag]", fontsize=12)
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)
#ax.set_ylim(4e-3, 2.7)
ax.annotate(txt, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')


ax = fig.add_subplot(2, 2, 3)	
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))

stuff = ax.hexbin(abstruetds, maxmagerrs, C=pterms,
	vmin=5e-3, vmax=1.0, cmap=cmap, reduce_C_function=meanbest,
	xscale = 'linear', yscale = 'log', mincnt=2*mincnt, norm=matplotlib.colors.LogNorm(),
	gridsize = gridsize
	)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", "8%", pad="3%")
cax = plt.colorbar(stuff, cax, ticks = LogLocator(subs=range(10)))
cax.set_label("$P$", fontsize=14)


ax.set_xlabel("$|\Delta t|$ [day]", fontsize=12)
ax.set_ylabel("Phot. precision of fainter image [mag]", fontsize=12)
ax.set_xlim(0, 120)
ax.set_ylim(4e-3 ,6e-1)
#ax.set_ylim(4e-3, 2.7)
ax.annotate(txt, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
ax.annotate(r"Best half of $\tilde{P_i}$s in each tile", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -20), textcoords='offset points', ha='left', va='top')


#ax = fig.add_subplot(2, 2, 4)


"""
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


"""


#ax.xaxis.set_minor_locator(AutoMinorLocator(5))
#ax.yaxis.set_minor_locator(AutoMinorLocator(5))
#
#stuff = ax.hexbin(abstruetds, maxmagerrs, C=chi2terms,
#	vmin=0.0, vmax=2.0, cmap=cmap, reduce_C_function=np.mean,
#	xscale = 'linear', yscale = 'log', mincnt=mincnt,
#	#norm=matplotlib.colors.LogNorm(),
#	gridsize = 4
#	)
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", "8%", pad="3%")
#cax = plt.colorbar(stuff, cax)#, ticks = matplotlib.ticker.LogLocator(subs=range(10)))
#cax.set_label(r"$\chi^2$", fontsize=16)
#		
#ax.set_xlabel("$|\Delta t|$ [day]", fontsize=12)
#ax.set_ylabel("Phot. precision of fainter image [mag]", fontsize=12)
#ax.set_xlim(0, 120)
#ax.set_ylim(4e-3 ,6e-1)
##ax.set_ylim(4e-3, 2.7)
##ax.annotate("5 x 4 months, 3-day cadence", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
##ax.annotate("Best half in each tile", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -20), textcoords='offset points', ha='left', va='top')




plt.tight_layout()
fig.subplots_adjust(wspace=0.6)

plt.show()



