import os, sys
import pycs
import numpy as np


"""
Like crudeopt, but run it on multiple curves
basically, everything here is function
Implement it as a pycs module once its working...

 
WAAAARNIIIIIIINNNNGGG:

The more features I add, the messier this module gets. Before making it public, this should be rewritten using a Class
to store all these parameters, instead of writing tons of separated pkls for each curve...

"""

#########################################################
###   SPLINE FITTING
#########################################################

def fitsplinesinglecurve(rung,pair,workdir="."):
	"""
	I fit a spline on only one one lightcurve
	Spline knotstep is determined according to the spline structure
	"""
	# Select the curve
	lcs = pycs.tdc.util.read(pycs.tdc.util.tdcfilepath('tdc1',rung,pair))
	(lca,lcb) = lcs

	# Compute knotstep and other parameters for the spline fitting
	stats = lca.samplingstats(seasongap=30)
	sampling = stats["med"]

	if not (hasattr(lca, "vario") and hasattr(lcb, "vario")):
		lca.vario = pycs.tdc.vario.vario(lca, verbose=True)
		lcb.vario = pycs.tdc.vario.vario(lcb, verbose=True) 


	knotstep = pycs.tdc.splopt.calcknotstep([lca.vario, lcb.vario])
	bokeps = np.max([sampling, knotstep/3.0])
	bokwindow = None
	# The stab params, quite easy :
	stabext = 300.0
	stabgap = 6.0
	stabstep = sampling
	stabmagerr = -3.0
	knots = pycs.gen.spl.seasonknots(lcs, knotstep, ingap=1)



	# Fit a spline into the first lc
	spline = pycs.gen.spl.fit([lca], knots=knots,
		stab=True, stabext=stabext, stabgap=stabgap, stabstep=stabstep, stabmagerr=stabmagerr,
		bokit=0, bokeps=bokeps, boktests=5, bokwindow=bokwindow, verbose=False)

	lcs=(lca,lcb)
	pycs.gen.lc.display([lca,lcb],[spline],filename="%s/spline.png" %(workdir))
	pycs.gen.util.writepickle(spline,"%s/spline.pkl" %(workdir))	
	return lcs,spline
	

#########################################################
###   GRID DEFINITION
#########################################################

def getgrid(lcs,nmagsteps=20,ntimesteps=100,mintimeshift=200):
	"""
	From the two lightcurves, I return two arrays containing the magshifts and timeshifts to use for the crude delay estimation
	"""

	(lca,lcb) = lcs
	# magnitude grid definition:
	meanmaglca = np.mean(lca.getmags())
	meanmaglcb = np.mean(lcb.getmags())
	magsize = max(np.max(abs(lca.getmags()-meanmaglca)),np.max(abs(lcb.getmags()-meanmaglcb))) #hand-tuned
	meanmagshift = meanmaglca-meanmaglcb

	magsteps = np.linspace(meanmagshift-magsize,meanmagshift+magsize,nmagsteps) # grid around meanmagshift

	# time grid definition:
	timesize  = min(mintimeshift,(max(lca.getjds())-min(lca.getjds()))/2.0)
	timesteps = np.linspace(-timesize,timesize,ntimesteps)

	return magsteps,timesteps




#########################################################
###   RESIDUAL DETERMINATION
#########################################################

# In the regions where the two lightcurves do not overlap, the residuals may be really high
# We need to disregard these points from the computation

def getseasons(lc,seasongap=60):
	"""
	Give me a lightcurve, I compute an array of seasons [(sea_begin,sea_end),(...,...),...],
	each element contains the first and last julian day of the season. I use this to compute the indexes
	"""
			
	seasons=[]
	jds = lc.getjds()	
	beginday = jds[0]
	for ind,jd in enumerate(jds):
		if not ind == len(jds)-1:
			if abs(jd-jds[ind+1])>seasongap:
				endday = jd 
				seasons.append((beginday,endday))
				beginday = jds[ind+1]
		if ind==len(jds)-1:
			endday=jd
			seasons.append((beginday,endday))
	return seasons

	
def getindexinseasons(lca,lcb,seasongap=60):
	"""
	This function determine which points in lcb are inside lca season (in julian days)
	It returnes the indexes such that lcb.getjds()[index] is in one of the lca season
	
	Give me a lightcurve, I compute an array of seasons [(sea_begin,sea_end),(...,...),...],
	each element contains the first and last julian day of the season. I use this to compute the indexes		
	
	"""		
	
	seasons = getseasons(lca,seasongap)
	
	jds = lcb.getjds()
	indexes = []
	nseasons = len(seasons)
	for ind,jd in enumerate(jds):
		for indsea,season in enumerate(seasons):
			if jd > season[0] and jd < season[1]:
				indexes.append((ind,indsea))
	return indexes,nseasons	



def getresidual_singleshift(lcs,spline,timeshift,magshift,minoverlap=3,display=False,workdir="."):
	"""
	lcs[0] is the one used for spline fitting
	lcs[1] is the one on which we want to compute residuals
	
	We assume the spline has already been created.
	
	We DO NOT apply shifts to any lightcurve here. Only compute the residuals as if the second lightcurve is shifted
			
	This method sum the residuals in absolute value, and divide the sum by the number of points considered
	This is some kind of "average absolute residual"	
	"""
	
	# copy the origninal curves, so they are unaltered	
	lca = lcs[0].copy()
	lcb = lcs[1].copy()
	
	# shift the second lc	
	lcb.shifttime(timeshift)
	lcb.shiftmag(magshift)
	
	# get the residuals. Now, l has l.residual attribute, a vector with a value for each point
	pycs.sim.draw.saveresiduals([lcb],spline)
	
	# get which points of lcb (shifted!) are inside lca
	indexes,nseasons = getindexinseasons(lca,lcb)

	# sum over these residuals only
	sumresidual = 0
	count = 0 
	for index in indexes:
		sumresidual += abs(lcb.residuals[index[0]])
		count += 1
	if count > minoverlap: # Let's say we need at least 4 points overlapping...
		sumresidual = sumresidual/count
	else :
		#print "WARNING, SUMRESIDUALS IS POORLY DEFINED. CHANGE THIS !! "
		sumresidual = 1.5 # CAREFUL WITH THIS !!!	 	
	
	
	
	# For checking purpose, we plot which points were taken into account for the residual computation
	# Warning, this slows down the whole process by a factor "a lot". It also takes a lot of disk space.
	if display:
		for ind,jd in enumerate(lcb.getjds()):
			lcb.mask[ind] = False
		for index in indexes:
			lcb.mask[index[0]] = True
		if not os.path.isdir('%s/inseas' %workdir):
			os.mkdir('%s/inseas' %workdir)				
		pycs.gen.lc.display([lca,lcb],[spline],filename="%s/inseas/t%i_m%.2f.png" %(workdir,timeshift,magshift))
		
	return sumresidual
	

def getresidual_perseasons(lcs,spline,timeshift,magsteps,mode,minoverlap=3,display=False,workdir="."):
	"""
	lcs[0] is the one used for spline fitting
	lcs[1] is the one on which we want to compute residuals
	
	We assume the spline has already been created.
	
	We DO NOT apply shifts to any lightcurve here. Only compute the residuals as if the second lightcurve is shifted

	This method split the curve into seasons and fit the seasons independently. Thus, we need only an initial timeshift.
	The loop on magshift is performed here ! 	
	"""
	
	# copy the origninal curves, so they are unaltered	
	lca = lcs[0].copy()
	lcb = lcs[1].copy()
	
	# shift the second lc	
	lcb.shifttime(timeshift)

	
	# get which points of lcb (shifted!) are inside lca
	# here, we also need the seasons indices		
	indexes,nseasons = getindexinseasons(lca,lcb)
	
	# Now, consider each season of lcb as an independent lightcurve to shift in mag, optimizing the residuals...
	# Instead of creating new lc, we copy the original, then mask and cut the points we do not want to consider
	# Certainly not fast, but easier to code...
	
	seasonsresults = [] 
	
	for seaind in np.arange(nseasons):

		# cut all the non-considered points
		lcbcop = lcb.copy()
		indextomasks = [index[0] for index in indexes if index[1] == seaind]
		
		for ind,jd in enumerate(lcbcop.getjds()):
			lcbcop.mask[ind] = False
		for indextomask in indextomasks:
			lcbcop.mask[indextomask] = True		
		lcbcop.cutmask()
	
		# compute residuals		
		sumresiduals = []		
		for magshift in magsteps:
		
			lcbcop.shiftmag(magshift)
			if len(lcbcop.getjds()) > minoverlap:
				pycs.sim.draw.saveresiduals([lcbcop],spline)		
				sumresidual = sum(abs(lcbcop.residuals))/float(len(lcbcop.residuals)) / float(np.sqrt(len(lcbcop.residuals)))
			else:
				sumresidual = 100.0	
			
			sumresiduals.append((magshift,sumresidual))
			lcbcop.shiftmag(-magshift) # return to unshifted mag state...
			
		#sort by residuals: the first element is the one with the best residuals
		seasonsresults.append(sorted(sumresiduals,key=lambda sumresidual: sumresidual[1])[0])
		
		# test plot -- is the shift and residual computation working ?
		#lcbcop.shiftmag(seasonsresults[-1][0])
		#pycs.gen.lc.display([lca,lcbcop],[spline])
		#sys.exit()
	


    # how many seasons are kicked off the analysis
	# nrm = nseasons/5*(-1) # Bad idea. We need a better criteria to shoot seasons from analysis.
	
	# seasonsresults is a list, each element refers to one season, and contain the best magshift and corresponding residuals
	if mode == "sum":
		# return the sum of the best residuals for each season
		overallresidual = np.sum(sorted([seasonsresult[1] for seasonsresult in seasonsresults]))
		stdmag = np.std([seasonsresult[0] for seasonsresult in seasonsresults]) # compute std of the magshifts per seasons. Can be useful to characterise ML intensity...
		return overallresidual,stdmag
		
	if mode == "median":
		# return the median of the best residuals for each season
		overallresidual = np.median(sorted([seasonsresult[1] for seasonsresult in seasonsresults]))
		stdmag = np.std([seasonsresult[0] for seasonsresult in seasonsresults]) # compute std of the magshifts per seasons. Can be useful to characterise ML intensity...
		return overallresidual,stdmag		
		

	if mode == "individual":
		# Do not sum here
		return seasonsresults
		

def getresiduals(lcs,spline,magsteps,mytimesteps,resmode,mode="sum",minoverlap=10,workdir=".",display=False):

	"""
	Main function here:
	Now, let's compute the residuals - loop on getresidual_singleshift
	brute force, we test every combination	
	"""
	
	if resmode == "singleshift":
		residuals = [] # we go for the good old list of dicts...beerk
		for magstep in magsteps:
			for timestep in mytimesteps:
				entry={}
				entry["timeshift"]= timestep
				entry["magshift"] = magstep
				entry["medres"] = getresidual_singleshift(lcs,spline,timeshift=timestep,magshift=magstep,minoverlap=minoverlap,display=display,workdir=workdir)
				residuals.append(entry)


		pycs.gen.util.writepickle(residuals,"%s/resids_%s.pkl" %(workdir,resmode))
		
	elif resmode == "perseasons":
	
		if mode == "sum" or mode == "median":
			residuals = []
			for timestep in mytimesteps:
				entry={}
				entry["timeshift"] = timestep
				res,stdmag = getresidual_perseasons(lcs,spline,timeshift=timestep,magsteps=magsteps,mode=mode,minoverlap=minoverlap,display=display,workdir=workdir)
				entry["medres"] = res
				entry["stdmag"] = stdmag 
				residuals.append(entry)
				
		elif mode == "individual":		
			residuals = []
			for timestep in mytimesteps:
				entry={}
				entry["timeshift"] = timestep
				seasonsresults = getresidual_perseasons(lcs,spline,timeshift=timestep,magsteps=magsteps,mode=mode,minoverlap=minoverlap,display=display,workdir=workdir)
				for ind,seasonsresult in enumerate(seasonsresults):
					entry["s%i_medres"%int(ind+1)] = seasonsresult[1]
					entry["s%i_mag"%int(ind+1)] = seasonsresult[0]				
				residuals.append(entry)
		else:
			print "Hey, give me a correct mode! I do not know %s" %mode
			sys.exit()
						
		pycs.gen.util.writepickle(residuals,"%s/resids_%s_%s.pkl" %(workdir,resmode,mode))
		
					
	else:
		print "Hey, give me a correct resmode! I do not know %s" %resmode
		sys.exit()
	
	return residuals
	


def getconfparams(residuals, workdir=".", mode="undefined"):

    from scipy.signal import argrelextrema as ag
    """
    First attempt to return confidence parameters for the crude estimation
    I look at the "shape" of the residual curve, looking for a "strong" minimum corresponding to the guessed delay

    For now, works only with sum and median residuals


    """

    # Collect the values from residuals
    times     = []
    resids    = []
    stdmags   = []
    for residual in residuals:
        if residual["medres"] < 100:
            stdmags.append(residual["stdmag"])
            times.append(residual["timeshift"])
            resids.append(residual["medres"])

    # look for minimas in resids:
    resids = np.array(resids)
    minimas = ag(resids, np.less, axis=0, order=10, mode='clip')

    # compute mean and std for sigma display of residuals and magshifts
    meansig = np.mean(stdmags)
    stdsig  = float(np.std(stdmags))
    meanres =  np.mean(resids)
    stdres = float(np.std(resids))

    # rescale residuals and magshifts
    sigresids = [abs(resid-meanres)/stdres for resid in resids] # to characterise the depth of the minimas
    sigstdmags = [(stdmag-min(stdmags))/stdsig for stdmag in stdmags] # to characterise the strength of microlensing


    # compute special statistics for the minimas
    minparams = []
    for ind,minima in enumerate(minimas[0]):
        minparam = {}
        # compute sigma scatter on the whole curve
        sigres = (meanres-resids[minima])/stdres
        sigmag = (meansig-stdmags[minima])/stdsig

        #if sigscat >=  1.5:
        #print "Minima %i:" %int(ind+1), " dt = %.2f"%times[minima], " res = %.2f"%resids[minima], " scatter = %.2f"%sigscat

        minparam["time"]  = times[minima]
        minparam["resid"] = resids[minima]
        minparam["sigres"] = sigres
        minparam["sigmag"] = sigmag
        minparams.append(minparam)


	# this is stupid. Like, really stupid.
    conflevel = 3
    if len(minparams) > 0:
	if max([minparam["scatter"] for minparam in minparams]) >= 2:
	    conflevel = 1
	elif max([minparam["scatter"] for minparam in minparams]) >= 1:
	    conflevel = 2
    else:
	    conflevel = 4


    pycs.gen.util.writepickle((sigresids,sigstdmags,minparams,conflevel),os.path.join(workdir, "%s_mins.pkl" %mode))
    return (sigresids,sigstdmags,minparams,conflevel)



#########################################################
###   PLOT RESULTS
#########################################################
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def displaycrudeopt(rung,pair,residuals,timesteps,magsteps,resmode,mode="sum",workdir=".",savefig=False):
	
	"""
	Display the residuals
	"""
	if resmode == "singleshift":	
		# Get the true time delay from truth.txt
		lines = open('../analyse_results/truth.txt').readlines()
		lines = [line.split() for line in lines]
		filename = os.path.basename(pycs.tdc.util.tdcfilepath('tdc1',rung,pair))
		truedelay = 0
		for line in lines: #ooooh god this is ugly
			if line[0] == filename:
				truedelay = float(line[1])*(-1.0)

		# Collect the values from residuals
		times  = []
		mags   = []
		resids = []
		for residual in residuals:
			times.append(residual["timeshift"])
			mags.append(residual["magshift"])
			resids.append(residual["medres"])


		# Get the best value from residuals
		# WARNING : Dangerous to proceed like this ! Use dict sort instead !!!!
		minindex = resids.index(min(resids))
		timemin = times[minindex]
		magmin  = mags[minindex]


		# Arrange them to get a nice colormap
		times = np.asarray(times)
		mags = np.asarray(mags)
		resids = np.asarray(resids)
		resids = np.log10(resids) # more precise in log10

		X,Y=np.meshgrid(timesteps,magsteps)
		resids=np.reshape(resids,X.shape)


		# Finally, the plot !
		plt.figure()	
		CS=plt.contourf(X,Y,resids,100,cmap=cm.bone)
		plt.contour(X,Y,resids,30,colors='white')
		plt.colorbar(CS)
		plt.suptitle(filename)
		plt.xlabel('B Time Shift [days]')
		plt.ylabel('B Magnitude Shift [mag]')
		plt.plot([truedelay,truedelay],[min(mags),max(mags)],'--',c='white',linewidth=2.5)
		plt.scatter(timemin,magmin,s=80,c='cyan')
		if savefig==True:
			plt.savefig("%s/plot_res_%s.png" %(workdir,resmode))
			plt.close()
		else:	
			plt.show()
			
	elif resmode == 'perseasons':
		
	
		# Get the true time delay from truth.txt
		lines = open('../analyse_results/truth.txt').readlines()
		lines = [line.split() for line in lines]
		filename = os.path.basename(pycs.tdc.util.tdcfilepath('tdc1',rung,pair))
		truedelay = 0
		for line in lines:  # ooooh god this is ugly
			if line[0] == filename:
				truedelay = float(line[1])*(-1.0)
				
		fig = plt.figure()
		plt.subplots_adjust(left=0.11, right=1, top=0.9, bottom=0.1)
		ax=fig.add_subplot(111)
		plt.suptitle(filename, fontsize =15)
		plt.xlabel('Time Shift [days]',fontsize=15)
		plt.ylabel('log10 absolute average residuals', fontsize=15)
		for tick in ax.xaxis.get_major_ticks():
			tick.label.set_fontsize(15)
		for tick in ax.yaxis.get_major_ticks():
			tick.label.set_fontsize(15)

		
		if mode == "sum" or mode == "median":
			# Collect the values from residuals
			times     = []
			stdmags   = []
			resids    = []
			for residual in residuals:
				if residual["medres"] < 100:
					times.append(residual["timeshift"])
					stdmags.append(residual["stdmag"])
					resids.append(residual["medres"])


			# get confidence parameters
			(sigresids, sigstdmags,minparams, conflevel) = getconfparams(residuals, workdir=workdir, mode=mode)
			for minparam in minparams:
				print minparam["time"],minparam["resid"]
				plt.annotate("%.2f" %minparam["scatter"], xy=[minparam["time"]-10,np.log10(minparam["resid"])-0.045], fontsize=15)



			# Get the best value from residuals
			# WARNING : Dangerous to proceed like this ! Use dict sort instead !!!!
			minindex = resids.index(min(resids))
			timemin = times[minindex]


			resids = np.log10(resids)
			confcolors=["blue", "green", "yellow", "red"]
			plt.scatter(timemin,min(resids),s=350,c=confcolors[conflevel-1],marker="d",alpha=0.5)
			plt.plot([truedelay,truedelay],[min(resids),max(resids)],'--',c='black',linewidth=2.5, alpha=0.5)
			sc = plt.scatter(times,resids,s=50,c=sigstdmags)
			plt.plot(times,resids,'k--')
			cbar = plt.colorbar(sc)
			cbar.set_label("mean seasonal magnitude shift [sigma]", fontsize=15)
			cbar.ax.tick_params(labelsize=15)

		elif mode == "individual":
		
			# Initialise a list of fancy colors, one per season (max.# of seasons = 10)
			colors = ['red','green','blue','orange','black','crimson','chartreuse','magenta','gray','salmon']
		
			# Collect the values from residuals
			times_seas     = []
			mags_seas      = []
			resids_seas    = []
			
			# get the number of seasons in residuals, by looking at the number of times *_medres is present as a keyword in the first residual
			nseasons = len([kw for kw in residuals[0] if "medres" in kw.split('_')])

			# initialise empty arrays, one per season
			for ind in np.arange(nseasons):
				times_seas.append([])
				mags_seas.append([])
				resids_seas.append([])				
			

			# fill these arrays
			for residual in residuals: # loop over time
				for ind in np.arange(nseasons): # loop over seasons				
					if residual["s%i_medres"%int(ind+1)] < 100:
						times_seas[ind].append(residual["timeshift"])
						mags_seas[ind].append(residual["s%i_mag"%int(ind+1)])
						resids_seas[ind].append(residual["s%i_medres"%int(ind+1)])
			for ind in np.arange(nseasons):
				resids_seas[ind] = [np.log10(elt) for elt in resids_seas[ind]] # more precise in log10
					
						
			# plot the shit out of them
			for ind in np.arange(nseasons):
			
				minindex = resids_seas[ind].index(min(resids_seas[ind]))
				timemin = times_seas[ind][minindex]
			

				plt.plot(times_seas[ind],resids_seas[ind],color=colors[ind],linewidth=2,label='s%i'%int(ind+1))
				plt.scatter(timemin,min(resids_seas[ind]),s=160,c=colors[ind])
			
			plt.legend()	
			plt.plot([truedelay,truedelay],[min([min(resids_sea) for resids_sea in resids_seas]),max([max(resids_sea) for resids_sea in resids_seas])],'--',c='indigo',linewidth=2.5)
			
				
		if savefig==True:
			plt.savefig("%s/plot_res_%s_%s.png" %(workdir,resmode,mode))
			plt.close()
		else:	
			plt.show()
		
##############
###   MAIN
##############

# Let's play directly with these functions
# For testing purposes...

if __name__ == "__main__":


	rung = 1
	pair = 224

	workdir = 'tdc1_%i_%i' %(rung,pair)
	if not os.path.isdir(workdir):
		os.mkdir(workdir)

	# get the spline and lcs
	lcs,spline = fitsplinesinglecurve(rung,pair,workdir)

	# get the grid
	magsteps,timesteps = getgrid(lcs,nmagsteps=20,ntimesteps=100)


	# get the residuals, and plot them
	# residuals = getresiduals(lcs,spline,magsteps,timesteps,resmode='singleshift',minoverlap=10,workdir=workdir,display=False)
	# displaycrudeopt(rung,pair,residuals,timesteps,magsteps,resmode='singleshift',workdir=workdir,savefig=True)

	residuals = getresiduals(lcs,spline,magsteps,timesteps,resmode='perseasons',mode="sum",minoverlap=0,workdir=workdir,display=False)
	displaycrudeopt(rung,pair,residuals,timesteps,magsteps,resmode='perseasons',mode="sum",workdir=workdir,savefig=False)

	"""
	residuals = getresiduals(lcs,spline,magsteps,timesteps,resmode='perseasons',mode="median",minoverlap=3,workdir=workdir,display=False)
	displaycrudeopt(rung,pair,residuals,timesteps,magsteps,resmode='perseasons',mode="median",workdir=workdir,savefig=True)

	residuals = getresiduals(lcs,spline,magsteps,timesteps,resmode='perseasons',mode="individual",minoverlap=3,workdir=workdir,display=False)
	displaycrudeopt(rung,pair,residuals,timesteps,magsteps,resmode='perseasons',mode="individual",workdir=workdir,savefig=True)

	import combine_pngs
	combine_pngs.makeplot(".",[workdir],False)
	"""















