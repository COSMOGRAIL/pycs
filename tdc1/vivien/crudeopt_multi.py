import os, sys
import pycs
import numpy as np


"""
Like crudeopt, but run it on multiple curves
basically, everything here is function
Implement it as a pycs module once its working...

 
TODO:
	Create a database with the true delays, the d3cs delay and confidence level, and add the delay estimate from this script  
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
		#pycs.gen.lc.display([lca,lcb],[spline])			
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
				sumresidual = sum(abs(lcbcop.residuals))/float(len(lcbcop.residuals))	
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
	
	# seasonsresults is a list, each element refers to one season, and contain the best magshift and corresponding residuals
	if mode == "sum":
		# return the sum of the best residuals for each season
		overallresidual = np.sum(sorted([seasonsresult[1] for seasonsresult in seasonsresults])[:])
		stdmag = np.std([seasonsresult[0] for seasonsresult in seasonsresults]) # compute std of the magshifts per seasons. Can be useful to characterise ML intensity...
		return overallresidual,stdmag
		
	if mode == "median":
		# return the median of the best residuals for each season
		overallresidual = np.median(sorted([seasonsresult[1] for seasonsresult in seasonsresults])[:])
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
		for line in lines: #ooooh god this is ugly
			if line[0] == filename:
				truedelay = float(line[1])*(-1.0)
				
		plt.figure()
		plt.suptitle(filename)		
		plt.xlabel('B Time Shift [days]')
		plt.ylabel('log10 Absolute average residuals')		
		
		
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

			# Get the best value from residuals
			# WARNING : Dangerous to proceed like this ! Use dict sort instead !!!!
			minindex = resids.index(min(resids))
			timemin = times[minindex]


			resids = np.log10(resids)
			sc = plt.scatter(times,resids,s=50,c=stdmags)
			plt.plot(times,resids,'k--')
			plt.colorbar(sc)
			plt.scatter(timemin,min(resids),s=160,c='grey',marker="d")
			plt.plot([truedelay,truedelay],[min(resids),max(resids)],'--',c='green',linewidth=2.5)
				
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

if __name__ == "__main__":

	rung = 1
	pair = 324
	
	workdir = 'tdc1_%i_%i' %(rung,pair)
	if not os.path.isdir(workdir):
		os.mkdir(workdir)
	
	# get the spline and lcs
	lcs,spline = fitsplinesinglecurve(rung,pair,workdir)

	# get the grid
	magsteps,timesteps = getgrid(lcs,nmagsteps=20,ntimesteps=100)


	# get the residuals
	residuals = getresiduals(lcs,spline,magsteps,timesteps,resmode='perseasons',mode="individual",minoverlap=10,workdir=workdir,display=True)
	

	# plot the residuals
	displaycrudeopt(rung,pair,residuals,timesteps,magsteps,resmode='perseasons',mode="individual",workdir=".",savefig=False)

















