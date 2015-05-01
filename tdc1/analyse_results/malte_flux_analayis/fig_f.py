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


db = pycs.gen.util.readpickle(pklfilepath)

db = db.values()

db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones


print "db length", len(db)

for item in db:
	item["isindoupla"] = 0.0
	item["isindou"] = 0.0
	if "pycs_tdc1_spl-vanilla-doupla-full_td" in item:
		item["isindoupla"] = 1.0
	if "pycs_tdc1_spl-vanilla-dou-full_td" in item:
		item["isindou"] = 1.0
	
		


gridsize = (8, 4)
mincnt = 4


emin = np.log10(3e-3)
#-2.3979400086720375
emax = np.log10(3.0)
#0.43136376415898736

tmin = -3
tmax = 120


cmap = matplotlib.cm.get_cmap("rainbow")

fig = plt.figure(figsize=(14.3, 4.2))
fig.subplots_adjust(left=0.05, right=0.92, top=0.95, bottom=0.12, wspace=0.13)





ax = fig.add_subplot(1, 3, 1)	
ax.xaxis.set_minor_locator(AutoMinorLocator(5))


dbsel = [item for item in db if item["rung"] in [2, 3]]

isindous = np.array([item["isindou"] for item in dbsel])
isindouplas = np.array([item["isindoupla"] for item in dbsel])
medmagerrAs = np.array([item["medmagerrA"] for item in dbsel])
medmagerrBs = np.array([item["medmagerrB"] for item in dbsel])
medmagerrstack = np.vstack([medmagerrAs, medmagerrBs])
minmagerrs = np.min(medmagerrstack, axis=0)
maxmagerrs = np.max(medmagerrstack, axis=0)
truetds = np.array([item["truetd"] for item in dbsel])
abstruetds = np.fabs(truetds)


stuff = ax.hexbin(abstruetds, maxmagerrs, C=isindous,
	vmin=0.0, vmax=1.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=mincnt,extent=(tmin, tmax, emin, emax),
	gridsize = gridsize
	)
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", "5%", pad="3%")
#cax = plt.colorbar(stuff, cax)
#cax.set_label('$f$ of "doubtless"')
		
ax.set_xlabel("$|\Delta t|$ [day]", fontsize=16)
ax.set_ylabel("Phot. precision of fainter image [mag]", fontsize=14)

#ax.annotate("3-day cadence, 5 x 4-month seasons (rungs 2, 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
ax.annotate('Fraction of "doubtless" delays', xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
ax.annotate("5 x 4 months, 3-day cadence (rungs 2 & 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top')

ax.set_xlim(tmin, tmax)
ax.set_ylim(4e-3, 2.7)



ax = fig.add_subplot(1, 3, 2)	
ax.xaxis.set_minor_locator(AutoMinorLocator(5))

stuff = ax.hexbin(abstruetds, maxmagerrs, C=isindouplas,
	vmin=0.0, vmax=1.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=mincnt, extent=(tmin, tmax, emin, emax),
	gridsize = gridsize
	)

#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", "5%", pad="3%")
#cax = plt.colorbar(stuff, cax)


#cax = fig.add_axes([0.92, 0.12, 0.02, 0.83])
#fig.colorbar(stuff, cax=cax)
#cax = plt.colorbar(stuff, cax)
#cax.set_label('Fraction of measured delays')
	
ax.set_xlabel("$|\Delta t|$ [day]", fontsize=16)
#ax.set_ylabel("Median photometric error of fainter image [mag]")

#ax.annotate("3-day cadence, 5 x 4-month seasons (rungs 2, 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
ax.annotate('Fraction of "plausible" & "doubtless" delays', xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
ax.annotate("5 x 4 months, 3-day cadence (rungs 2 & 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top')

ax.set_xlim(tmin, tmax)
ax.set_ylim(4e-3, 2.7)









ax = fig.add_subplot(1, 3, 3)	
ax.xaxis.set_minor_locator(AutoMinorLocator(5))


dbsel = [item for item in db if item["rung"] in [1]]

isindous = np.array([item["isindou"] for item in dbsel])
isindouplas = np.array([item["isindoupla"] for item in dbsel])
medmagerrAs = np.array([item["medmagerrA"] for item in dbsel])
medmagerrBs = np.array([item["medmagerrB"] for item in dbsel])
medmagerrstack = np.vstack([medmagerrAs, medmagerrBs])
minmagerrs = np.min(medmagerrstack, axis=0)
maxmagerrs = np.max(medmagerrstack, axis=0)
truetds = np.array([item["truetd"] for item in dbsel])
abstruetds = np.fabs(truetds)




stuff = ax.hexbin(abstruetds, maxmagerrs, C=isindouplas,
	vmin=0.0, vmax=1.0, cmap=cmap, reduce_C_function=np.mean,
	xscale = 'linear', yscale = 'log', mincnt=mincnt,extent=(tmin, tmax, emin, emax),
	gridsize = gridsize
	)

#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", "5%", pad="3%")
#cax = plt.colorbar(stuff, cax)


cax = fig.add_axes([0.94, 0.12, 0.02, 0.83])
fig.colorbar(stuff, cax=cax)
cax = plt.colorbar(stuff, cax)
cax.set_label('Fraction of discovered delays', fontsize=14)
	
ax.set_xlabel("$|\Delta t|$ [day]", fontsize=16)
#ax.set_ylabel("Median photometric error of fainter image [mag]")

#ax.annotate("3-day cadence, 5 x 4-month seasons (rungs 2, 3)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
ax.annotate('Fraction of "plausible" & "doubtless" delays', xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
ax.annotate("10 x 4 months, 3-day cadence (rung 1)", xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top')

ax.set_xlim(tmin, tmax)
ax.set_ylim(4e-3, 2.7)


#plt.tight_layout()
plt.show()



