"""
Stuff to manipulate time delay estimations from different techniques, specific to the TDC.
"""

import pycs.gen.lc
import numpy as np
import sys
import csv
import glob
import os
import datetime
import copy as pythoncopy


class Estimate:
	"""
	Class to hold delay estimates for TDC curves, as obtained by various delay estimators.
	"""
	
	def __init__(self, set="tdc0", rung=0, pair=1, method="None", methodpar="None", td=0.0, tderr=0.0, ms=0.0, confidence=0, timetaken=0.0):
		"""

		:param set: What set (e.g., "tdc0") the curves are from
		:param rung: rung
		:param pair: pair
		
		:param method: Name of the method
		:param methodpar: String containing parameters of this method, or username...

		:param td: time delay point estimate
		:param tderr: 1sigma error estimate on the time delay
		:param ms: magnitude shift estimate
		
		:param confidence: confidence level. 0 = not estimated, 1 = doubtless, 2 = plausible, ...
		:param timetaken: seconds it took to get this estimate

		"""
	
		self.set = set
		self.rung = rung
		self.pair = pair
		
		self.method = method
		self.methodpar = methodpar

		self.td = td
		self.tderr = tderr
		self.ms = ms
		
		self.confidence = confidence
		self.timetaken = timetaken
		
		self.setid()
		self.check()

	def __str__(self):
		return "%s %s (%s, %i, %i): %.2f +/- %.2f, conf. %i" % (self.method, self.methodpar, self.set, self.rung, self.pair, self.td, self.tderr, self.confidence)
	
	def aslist(self):
		return [self.set, self.rung, self.pair, self.method, self.methodpar, self.td, self.tderr, self.ms, self.confidence, self.timetaken]
	
	def check(self):
		
		#assert self.tderr >= 0.0
		if self.tderr < 0.0:
			raise RuntimeError("Negative error...")
	
	def copy(self):
		return pythoncopy.deepcopy(self)	

	def getcolor(self):
		if self.confidence==0: return "black"
		elif self.confidence==1: return "blue"
		elif self.confidence==2: return "green"
		elif self.confidence==3: return "orange"
		elif self.confidence==4: return "red"
		else: return "purple"	

	def setid(self):
		self.id = "%s_%i_%i" % (self.set, self.rung, self.pair)
		self.niceid = "(%s, %i, %i)" % (self.set, self.rung, self.pair)
	
	def applytolcpair(lca, lcb):
		lca.timeshift = 0.0
		lca.magshift = 0.0
		lca.fluxshift = 0.0
		
		lcb.timeshift = self.td
		lcb.magshift = self.ms
		lcb.fluxshift = 0.0
	
	
def readcsv(filepath):
	"""
	Read a CSV file of estimates.
	You can specify a directory instead of a file, and I will read in all .csv files form there.
	"""
	
	if os.path.isdir(filepath):
		files = sorted(glob.glob(os.path.join(filepath, "*.csv")))
		estimates = []
		for file in files:
			estimates.extend(readcsv(file))
		return estimates
			
	else:
		f = open(filepath, 'rb')
		reader = csv.reader(f, delimiter=',', quotechar='"')
		estimates = []
		for row in reader:
			for i in [1, 2, 8]:
				row[i] = int(row[i])
			for i in [5, 6, 7, 9]:
				row[i] = float(row[i])
			estimates.append(Estimate(*row))
		f.close()
		print "Read %i estimates from %s" % (len(estimates), filepath)
		return estimates
        
	
def writecsv(estimates, filepath, append=False):
	"""
	Write a CSV file of estimates.
	If append = True, I do NOT overwrite an existing file, but append to it !
	"""
	if append:
		f = open(filepath, "a")
	else:
		f = open(filepath, "w")
	writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
  	for est in estimates:
  		#est.td = "%.5f" % (est.td)
  		#est.tderr = "%.5f" % (est.tderr)
  		#est.ms = "%.5f" % (est.ms)
  		#est.timetaken = "%.5f" % (est.timetaken)
 		writer.writerow(est.aslist()) 
	f.close()
	print "Wrote %i estimates into %s" % (len(estimates), filepath)


def importfromd3cs(filepath, set="tdc0"):
	"""
	Reads a d3cs log file and returns the list of estimates
	"""
	
	logfile = open(filepath, 'r')
	lines = logfile.readlines()
	logfile.close()
	
	lines = [line.split(',') for line in lines]
	lines = [[element.strip() for element in line] for line in lines]
	
	estimates = [
		Estimate(set=set,
			rung = int(line[3]),
			pair = int(line[4]),
			method = "D3CS", 
			methodpar = line[2], 
			td = float(line[5]), 
			tderr = float(line[6]), 
			ms = float(line[7]),  
			confidence = int(line[9]), 
			timetaken = float(line[10]))
		for line in lines]

	print "Read %i D3CS estimates from %s" % (len(estimates), filepath)
	return estimates
	

def select(estimates, sets=None, rungs=None, pairs=None):
	"""
	Returns a sublist of the estimates selected according to the specified arguments.
	"""
	if sets == None:
		sets = [e.set for e in estimates]
	if rungs == None:
		rungs = [e.rung for e in estimates]
	if pairs == None:
		pairs = [e.pair for e in estimates]
		
	return [e for e in estimates if (e.set in sets) and (e.rung in rungs) and (e.pair in pairs)]
	

def group(estimates, verbose=True):
	"""
	Groups estimates by "quasar"
	In other words : takes a messy list of mixed estimates and returns a list of lists of estimates for a pair.
	"""
	estids = sorted(list(set([est.id for est in estimates])))
	groups = [[est for est in estimates if est.id == estid] for estid in estids]
	if verbose:
		print "Grouped %i estimates of %i different lenses" % (len(estimates), len(groups))	
	return groups
	
def checkunique(estimates):
	"""
	Checks that there is only one estimate per pair
	"""
	if len(estimates) != len(group(estimates, verbose=False)):
		raise RuntimeError("Your estimates are not unique !")
		
		
def checkallsame(estimates):
	"""
	Checks that the estimates are all about the same quasar
	If yes, return the set, rung and pair
	"""
	
	for est in estimates:
		if est.id != estimates[0].id:
			raise RuntimeError("Your estimates are related to different curves !")
	
	return (estimates[0].set, estimates[0].rung, estimates[0].pair)		
	

def match(candestimates, refestimates):
	"""
	candestimates and refestimates are two lists of estimates.
	I return a tuple of two lists :
		- those estimates of candestimates which are about quasars that are present in refestimates.
		- the remaining candestimates, about quasars not in refestimates
	"""
	
	refids = sorted(list(set([est.id for est in refestimates])))
	matched = []
	notmatched = []
	for e in candestimates:
		if e.id in refids:
			matched.append(e)
		else:
			notmatched.append(e)
	return (matched, notmatched)
	
	

def removebad(estimates,verbose=False):
	"""
	Remove the estimates with bad confidence level (typically 4)
	
	
	"""
	if verbose:
		for est in [est for est in estimates if est.confidence == 4]:
			print '     ----- WARNING -----     '
			print 'Estimate for curve %s removed.' % est.niceid
			print '         dt = %.2f   , dterr = %.2f' % (est.td, est.tderr)
				
	return [est for est in estimates if est.confidence < 4]



	
def combine(estimates,method='meanstd',methodcl=None):
	"""
	Combine estimates according the method of your choice. Return an estimate object
	
	list of methods (add yours): 
	- meanstd
	- ... 
	
	Methods should define : td, tderr, confidence, ms
	"""
	
	
	(set, rung, pair) = checkallsame(estimates)
	
	if method == 'meanstd':		
		
		estimates = removebad(estimates,verbose=True)
		
		tds   = [est.td for est in estimates]
		
		if len(tds) > 1:
			td     	   = np.mean(tds)
			tderr 	   = np.std(tds)/np.sqrt(len(tds))
			if tderr < 5:
				confidence = 0
			else:
				confidence = 4				

		else :
			td 	   = 0.
			tderr 	   = 0.
			confidence = 4	
		
		ms = 0.0
		
	if method == "initialestimation":
		"""
		To get safe initial conditions for automatic optimizers
		"""	
		td = np.median(np.array([est.td for est in estimates]))
		tderr = np.median(np.array([est.tderr for est in estimates]))
		ms = np.median(np.array([est.ms for est in estimates]))
		
		if np.max([est.confidence for est in estimates]) >= 3:
			confidence = 4
		else:
			confidence = int(np.ceil(np.median(np.array([est.confidence for est in estimates]))))

		
	combiest = Estimate(set=set, rung=rung, pair=pair, method="combi", methodpar=method, td=td, tderr=tderr, ms = ms, confidence=confidence)
	combiest.check()
	
	return combiest

	
def multicombine(estimates, method='meanstd'):
	"""
	Wrapper around combine.
	Multiple calls to the combine function. Eats a list of messy estimates, groups and combine them
	by quasar according to method, and return the list of combinated estimates. Can be used to feed writesubmission.	
	"""	

	newests=[]
	listests = group(estimates)
	
	for ests in listests:
		newests.append(combine(ests,method))
	
	checkunique(newests)
	newests = removebad(newests,verbose=True)
	return newests		
	
	

	
	
def writesubmission(estimates, filepath):
	"""
	Write a submissible TDC file from a list of estimates
	It takes td and tderr of estimates
		
	The delay td is in positive units (?)
	"""
	
	#if os.path.exists(filepath):
	#	print "WARNING, THAT FILE EXISTS !"
	#	return
	
	checkunique(estimates)
	for estimate in estimates:
		if estimate.confidence >= 4:
			print estimate
			raise RuntimeError("Bad confidence in your submission !")
	
	tdcfile = open(filepath, "w")
	
	tdcfile.write("# TDC submission written by PyCS\n")
	tdcfile.write("# %s\n" % (datetime.datetime.now()))
	tdcfile.write("# \n")
	tdcfile.write("# (Some room for your comment...)\n")
	tdcfile.write("# \n")
	tdcfile.write("# \n")
	tdcfile.write("# datafile              dt      dterr\n")
		
	for est in estimates:
		est.check()
		name = "%s_rung%i_pair%i.txt" % (est.set, est.rung, est.pair)
		tdcfile.write("%s\t%.2f\t%.2f\n" % (name, est.td, est.tderr))
		
	tdcfile.close()	
	



def bigplot(estimates, shadedestimates = None, plotpath = None, minradius=100):
	"""
	Large graphical representation of your estimates.
	
	:param minradius: Minimal half-width of the time delay axes, in day.
	
	:param shadedestimates: Here you can give me a list of "unique" estimates (typical the result of a multicombine)
		that I will show as shaded bars instead of errorbars.
		However, it's estimates that determines which panels I will draw and with what range,
		so that you can get panels shown without any shadedestimate.
	
	"""
	
	import matplotlib.pyplot as plt
	
	
	estids = sorted(list(set([est.id for est in estimates])))
	
	if shadedestimates != None:
		checkunique(shadedestimates)
		
	fig, axes = plt.subplots(nrows=len(estids), figsize=(10, 1.0*(len(estids))))
	fig.subplots_adjust(top=0.99, bottom=0.05, left=0.13, right=0.98, hspace=0.32)
   
	for ax, thisestid in zip(axes, estids):
		thisidests = [est for est in estimates if est.id == thisestid]
		n = len(thisidests)
		
		# The error bars for regular estimates :
		tds = np.array([est.td for est in thisidests])
		tderrs = np.array([est.tderr for est in thisidests])
 		ys = np.arange(n)
 		colors = [e.getcolor() for e in thisidests]
		#ax.scatter(tds, ys)
		ax.errorbar(tds, ys, yerr=None, xerr=tderrs, fmt='.', ecolor="gray", capsize=3)
		ax.scatter(tds, ys, s = 50, c=colors, linewidth=0, zorder=20)#, cmap=plt.cm.get_cmap('jet'), vmin=0, vmax=4)
		
		for (est, y) in zip(thisidests, ys):
			ax.text(est.td, y+0.3, "  %s (%s)" % (est.method, est.methodpar), va='center', ha='left', fontsize=6)
		
		# The shadedestimates
		if shadedestimates != None:
			shadedests = [est for est in shadedestimates if est.id == thisestid]
			if len(shadedests) == 1:
				shadedest = shadedests[0]
				ax.axvspan(shadedest.td - shadedest.tderr, shadedest.td + shadedest.tderr, color=shadedest.getcolor(), alpha=0.2, zorder=-20)
				ax.text(shadedest.td, -0.9, "%s (%s)" % (shadedest.method, shadedest.methodpar), va='center', ha='center', fontsize=6)
		
		ax.set_ylim(-1.3, n)
		
		meantd = np.mean(tds)
		maxdist = np.max(np.fabs(tds - meantd))
		if maxdist < minradius:
			tdr = minradius
		else:
			tdr = maxdist*1.2
		ax.set_xlim(meantd - tdr, meantd + tdr)
		
  		pos = list(ax.get_position().bounds)
   		x_text = pos[0] - 0.01
		y_text = pos[1] + pos[3]/2.
		fig.text(x_text, y_text, thisidests[0].niceid, va='center', ha='right', fontsize=14)
		
	for ax in axes:
		ax.set_yticks([])

	#cbar = plt.colorbar(sc, cax = axes[0], orientation="horizontal")
	#cbar.set_label('Confidence')

	if plotpath:
		plt.savefig(plotpath)
		print "Wrote %s" % (plotpath)
	else:
		plt.show()




def show(estimates, rung, pair):

	'''
	display the rung / pair curve for each corresponding estimate 
	'''
	
	
	# I select only the estimates with the rung and pair desired
	estimates = [est for est in estimates if est.rung == rung and est.pair == pair]

	setlist=[]
		
	# import the curve from data
	filepath = 'tdc0/rung%0i/tdc0_rung%0i_pair%0i.txt' % (rung,rung,pair)
		
	for est in estimates:	
		lcs = pycs.tdc.util.read(filepath)
		lcs[1].shifttime(est.td)
		lcs[1].shiftmag(est.ms)
		setlist.append([lcs,est.methodpar])
	
	pycs.gen.lc.multidisplay(setlist, showlegend = False, showdelays = True)		
		
	
def d3cs(rung,pair):
	'''
	Open d3cs with the rung/pair curve in your default browser
		
	'''
	import webbrowser
	cmd='http://www.astro.uni-bonn.de/~mtewes/d3cs/index.php?user=display&loadrung=%i&loadpair=%i' %(rung,pair)
	webbrowser.open(cmd)

	
	

def interactivebigplot(estimates, shadedestimates = None, plotpath = None, interactive = True, groupbyrung = False, minibox = False, minradius=100):

	"""
	Interactive version of the big plot above
	Set groupbyrung as True and be amazed !
	"""
	
	import matplotlib.pyplot as plt
	import matplotlib.axes as maxes
	from matplotlib.widgets import Button
	
	estids = sorted(list(set([est.id for est in estimates])))
	
	if shadedestimates != None:
		checkunique(shadedestimates)
			
	# Check that interactive is set on before allowing groupbyrung
	if groupbyrung == True and interactive == False:
		print 'WARNING : interactive option is set to False -- groupbyrung option is not allowed to be True'
		print 'groupbyrung is set to False' 
		groupbyrung = False
	
	
	if groupbyrung:
			
		# grouping the estids by rung
		
		groupestids=[]
		for ind in np.arange(7):
			groupestids.append([])
		
		for estid in estids: 
			for ind in np.arange(7):
				if estid[5] == str(ind):
					groupestids[ind].append(estid)
							
				
	def colour(est):
		if est.confidence==0: return "black"
		if est.confidence==1: return "blue"
		if est.confidence==2: return "green"
		if est.confidence==3: return "orange"
		if est.confidence==4: return "red"
	
		

	def interactiveplot(estids, figname=None):
		
		buttonstod3cs=[]
		buttonstoshow=[]	
	
		if len(estids)==0:
			print 'No pair in your estimates for this rung !'
			return
		
		if figname == None:
			figname = 'various estimates'
		
		fig, axes = plt.subplots(nrows=len(estids), figsize=(10, 1.0*(len(estids))), num=figname)
		fig.subplots_adjust(top=0.99, bottom=0.05, left=0.13, right=0.98, hspace=0.32)
		for ax, estid in zip(axes, estids):

			# resize ax and add a new box we will fill with other informations (see below)
			
			if minibox:
			
				bbox = ax.get_position()
				points = bbox.get_points()

				xright = points[1][0] 
				points[1][0] = 0.8
				bbox.set_points(points)
				ax.set_position(bbox)

				hspace = 0.02
				width  = xright-hspace-points[1][0]
				height = points[1][1]-points[0][1]

				rect = points[1][0]+hspace, points[0][1], width, height
				ax2 = fig.add_axes(rect)



			### arange and compute values to fill the left box (ax)	

			thisidests = [est for est in estimates if est.id == estid]
			n = len(thisidests)

			tds = np.array([est.td for est in thisidests])
			tderrs = np.array([est.tderr for est in thisidests])
			meantd = np.mean(tds)

 			ys = np.arange(n)

			colours = map(colour, thisidests)

			#ax.scatter(tds, ys)
			ax.errorbar(tds, ys, yerr=None, xerr=tderrs, fmt='.', ecolor="grey", capsize=3)
			ax.scatter(tds, ys, s = 50, c=colours, linewidth=0, zorder=20)#, cmap=plt.cm.get_cmap('jet'), vmin=0, vmax=4)

			for (est, y) in zip(thisidests, ys):
				ax.text(est.td, y+0.3, "  %s (%s)" % (est.method, est.methodpar), va='center', ha='left', fontsize=6)

			# The shadedestimates
			if shadedestimates != None:
				shadedests = [est for est in shadedestimates if est.id == estid]
				if len(shadedests) == 1:
					shadedest = shadedests[0]
					ax.axvspan(shadedest.td - shadedest.tderr, shadedest.td + shadedest.tderr, color=shadedest.getcolor(), alpha=0.2, zorder=-20)
					ax.text(shadedest.td, -0.9, "%s (%s)" % (shadedest.method, shadedest.methodpar), va='center', ha='center', fontsize=6)


			ax.set_ylim(-1.3, n)
			
			maxdist = np.max(np.fabs(tds - meantd))
			if maxdist < minradius:
				tdr = minradius
			else:
				tdr = maxdist*1.2
			ax.set_xlim(meantd - tdr, meantd + tdr)
		


  			pos = list(ax.get_position().bounds)
   			x_text = pos[0] - 0.01
			y_text = pos[1] + pos[3]/2.
			fig.text(x_text, y_text, estid, va='center', ha='right', fontsize=14)
			ax.set_yticks([])

			if interactive:
			
				### Interactive plotting options : add clickable buttons

				hscale = 3.5
				wscale = 12.0
				
				bbox = ax.get_position()
				points = bbox.get_points()
				
				xright = points[1][0] 
				hspace = 0.02
				width  = points[1][0]-points[0][0]
				height = points[1][1]-points[0][1]
				

				axtod3cs = plt.axes([points[0][0], points[0][1], width/wscale, height/hscale])
				axtoshow = plt.axes([points[0][0], points[0][1]+height-height/hscale, width/wscale, height/hscale])

				buttonstod3cs.append(Button(axtod3cs, 'D3CS'))
				buttonstoshow.append(Button(axtoshow, 'Show'))
				
				
			if minibox:
			
				### OK, now fill the right box (ax2)

				# some inits...
				conflevelmin = 3
				maxtolerr = 8

				thisidests_disc = [est for est in estimates if est.id == estid and est.confidence <= conflevelmin]
				tds_disc = np.array([est.td for est in thisidests_disc])

				meantd_disc = np.mean(tds_disc)
				meantderr = np.std(tds_disc)/np.sqrt(len(tds_disc))

				if meantderr < maxtolerr:
					mcolor = 'black'
				else:	
					mcolor = 'red'			

				
				ax2.errorbar(meantd_disc,1,yerr=None, xerr=[meantderr], fmt='.', ecolor=mcolor, capsize=3)					
				ax2.scatter(meantd_disc,1, s=50, c=mcolor, linewidth=0, zorder=20)


				from matplotlib.ticker import MaxNLocator
				ax2.xaxis.set_major_locator(MaxNLocator(4))

				ax2.set_xlim(meantd_disc - maxtolerr, meantd_disc + maxtolerr)		
				ax2.set_yticks([])


		if interactive:
			for buttontoshow, buttontod3cs, estid in zip(buttonstoshow, buttonstod3cs, estids):


				# weird way of doing things... but didn't find a cleaner way to have everything working... 

				rung = int(estid[5]) # Done this way to avoid mix up if I select my estimates in a weird order...
				pair = int(estid[7])

				class Goto:
	    				myrung = rung
					mypair = pair
	    				def show(self, event):
						show(estimates,self.myrung,self.mypair)

					def d3cs(self, event):
						d3cs(self.myrung,self.mypair)	

				goto = Goto()				
				buttontoshow.on_clicked(goto.show)
				buttontod3cs.on_clicked(goto.d3cs)
		
		plt.show()


	
	
	# Control Panel
	
	if groupbyrung:	
		class GotoRung():
			ind = 0

			def rung0(self, event):		
				self.ind = 0
				print ' \t currently at rung %i' %self.ind			
				interactiveplot(groupestids[self.ind], figname = 'rung 0')

			def rung1(self, event):		
				self.ind = 1
				print ' \t currently at rung %i' %self.ind
				interactiveplot(groupestids[self.ind], figname = 'rung 1')			

			def rung2(self, event):		
				self.ind = 2
				print ' \t currently at rung %i' %self.ind
				interactiveplot(groupestids[self.ind], figname = 'rung 2')			

			def rung3(self, event):		
				self.ind = 3
				print ' \t currently at rung %i' %self.ind
				interactiveplot(groupestids[self.ind], figname = 'rung 3')

			def rung4(self, event):		
				self.ind = 4
				print ' \t currently at rung %i' %self.ind
				interactiveplot(groupestids[self.ind], figname = 'rung 4')

			def rung5(self, event):		
				self.ind = 5
				print ' \t currently at rung %i' %self.ind
				interactiveplot(groupestids[self.ind], figname = 'rung 5')

			def rung6(self, event):		
				self.ind = 6
				print ' \t currently at rung %i' %self.ind
				interactiveplot(groupestids[self.ind], figname = 'rung 6')	

			def next(self, event):
				if self.ind <6:
					self.ind += 1
				else:
					self.ind = 0 	
				print ' \t currently at rung %i' %self.ind
				figname = 'rung %i' % self.ind				
				interactiveplot(groupestids[self.ind], figname = figname)

			def prev(self, event):
				self.ind -= 1
				if self.ind>0:
					self.ind -= 1
				else:
					self.ind = 6	
				print ' \t currently at rung %i' %self.ind
				figname = 'rung %i' % self.ind		
				interactiveplot(groupestids[self.ind], figname = figname)	
	
				
		fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(4.5, 3),num='control center')		
		fig.subplots_adjust(top=0.95, bottom=0.05, hspace=0.32)



		buttontorung0 = Button(axes[0][0], 'Rung 0')
		buttontorung1 = Button(axes[0][1], 'Rung 1')	
		buttontorung2 = Button(axes[0][2], 'Rung 2')
		buttontorung3 = Button(axes[1][0], 'Rung 3')	
		buttontorung4 = Button(axes[1][1], 'Rung 4')
		buttontorung5 = Button(axes[1][2], 'Rung 5')	
		buttontorung6 = Button(axes[2][0], 'Rung 6')	
		buttontonext = Button(axes[2][1],'Next Rung')
		buttontoprev = Button(axes[2][2],'Prev. Rung')


		gotorung = GotoRung()

		buttontonext.on_clicked(gotorung.next)
		buttontoprev.on_clicked(gotorung.prev)
		buttontorung0.on_clicked(gotorung.rung0)
		buttontorung1.on_clicked(gotorung.rung1)
		buttontorung2.on_clicked(gotorung.rung2)
		buttontorung3.on_clicked(gotorung.rung3)	
		buttontorung4.on_clicked(gotorung.rung4)
		buttontorung5.on_clicked(gotorung.rung5)	
		buttontorung6.on_clicked(gotorung.rung6)			


		plt.show()
	else:
		if plotpath:			
			plt.savefig(plotpath)
			print "Wrote %s" % (plotpath)			
		else:	
			interactiveplot(estids)
	
