"""
General purpose functions related to the TDC.
"""

import os
import numpy as np
import math
import pycs.gen.lc




def tdcfilepath(set, rung, pair, skipset=False):
	"""
	
	For tdc1 :
	rung is in [0, 4]
	pair is in [1, 1036]
	
	"""
	
	if set=='tdc0':
		return "%s/rung%i/%s_rung%i_pair%i.txt" % (set, rung, set, rung, pair)


	if set=='tdc1':
	
		if pair<=720:
			if skipset == False:	
				return "%s/rung%i/%s_rung%i_double_pair%i.txt" % (set, rung, set, rung, pair)
			else:
				return "rung%i/%s_rung%i_double_pair%i.txt" % (rung, set, rung, pair)
		else:
			modpair  = int(pair-720) 		# 1, 2, 3, 4
			quadpair = (modpair+1) // 2 	# 1, 1, 2, 2, ...
			quadcode = "A" if modpair % 2 == 1 else "B"
			 
			"""
			intdiv   = modpair/2    # gives the integer portion
			floatdiv = modpair/2.0  # gives the float value
			
			if abs(intdiv-floatdiv)> 1e-5:
				quadpair = str(intdiv+1)+str('A')
			else:
				quadpair = str(intdiv)+str('B')	
			"""
			
			if skipset == False:
				return "%s/rung%i/%s_rung%i_quad_pair%s%s.txt" % (set, rung, set, rung, quadpair, quadcode)	
			else:
				return "rung%i/%s_rung%i_quad_pair%s%s.txt" % (rung, set, rung, quadpair, quadcode)



def pogmag(flux, fluxerr, m0 = 22.5):
	"""
	Computes a "normal" Pogson magnitude from TDC info.
	Used for TDC0

	flux and fluxerr are two numpy arrays
	
	"""
	# This is the code used for TDC0 :
# 	# First we compute the error bars :
# 	l.magerrs = 2.5 * np.log10(1.0 + (l.magerrs / l.mags))
# 	# Then the magnitudes, assumging nanomaggies :
# 	l.mags = 22.5 - 2.5 * np.log10(l.mags)
	
	mag = m0 - 2.5 * np.log10(flux)
	magerr = 2.5 * np.log10(1.0 + (fluxerr / flux))

	return (mag, magerr)
	
	
	
def asinhmag(flux, fluxerr,  m0 = 22.5, f0=1.0, b=0.01):
	"""
	Implements
	http://ssg.astro.washington.edu/elsst/opsim.shtml?lightcurve_mags
	"""

	mag = m0 -(2.5/np.log(10.)) * ( np.arcsinh( flux / (f0 * 2.0 * b)) + np.log(b) )
	
	magplu = m0 -(2.5/np.log(10.)) * ( np.arcsinh( (flux+fluxerr) / (f0 * 2.0 * b)) + np.log(b) )
	magmin = m0 -(2.5/np.log(10.)) * ( np.arcsinh( (flux-fluxerr) / (f0 * 2.0 * b)) + np.log(b) )
	magerr = 0.5*(magmin - magplu)
	
	return (mag, magerr)


def read(filepath, mag="asinh", verbose=True, shortlabel=True):
	"""
	Imports TDC light curves, WITH ASINH MAGNITUDES 
	So far we expect exactly 2 curves in each file, as TDC simulates only doubles.
	Can be generalized later ...
	"""
	
	tdcid = os.path.splitext(os.path.basename(filepath))[0]
	
	if shortlabel == False:
		lc1 = pycs.gen.lc.flexibleimport(filepath, magcol=2, errcol=3, telescopename="TDC", object=tdcid+"_A", plotcolour="red", verbose = verbose)
		lc2 = pycs.gen.lc.flexibleimport(filepath, magcol=4, errcol=5, telescopename="TDC", object=tdcid+"_B", plotcolour="blue", verbose = verbose)
	else:
		lc1 = pycs.gen.lc.flexibleimport(filepath, magcol=2, errcol=3, telescopename="TDC", object="A", plotcolour="red", verbose = verbose)
		lc2 = pycs.gen.lc.flexibleimport(filepath, magcol=4, errcol=5, telescopename="TDC", object="B", plotcolour="blue", verbose = verbose)			

	lcs = [lc1, lc2]

	for l in lcs:
		#l.jds += 56586.0 # Starts on 21 October 2013 :)
		
		if mag == "pog":
			(l.mags, l.magerrs) = pogmag(l.mags, l.magerrs, m0 = 22.5)
		if mag == "asinh":
			(l.mags, l.magerrs) = asinhmag(l.mags, l.magerrs, m0 = 22.5, b=0.01)
			
	return lcs



def setnicemagshift(lcs):
	"""
	Sets a "nice" magshift to the n-1 last curves of lcs, so that they appear
	nicely below each other when displayed.
	Also works if you curves contain ML models or are alredy shifted.
	"""
	
	bottom = np.max(lcs[0].getmags())
	for l in lcs[1:]:
		top = np.min(l.getmags())
		l.shiftmag(bottom-top)
		bottom = np.max(l.getmags())

def cutlcs(lcs, nseasons=3.0,overlapfrac=0.2):

	# APPARENTLY UNUSED, TO BE DELETED...? (10.01.2014)

	"""
	From a given set of lcs, return cutted lcs, only part of the original lcs
	The goal is then to run the optimisation on these cutted lcs to estimate the error
	by taking the scatter between these estimations (not very smart, but fast)
	Generalised to n lightcurves in lcs, but only 3 cutted lcs returned (should be generalised later)
	
	This function return 3 cutted lcs for each lc 
	
	"""
	import sys
	
	
	# some inits...
	
	n = len(lcs)
	
	jds=[]
	for j in lcs[0].jds:
		jds.append(j)
		
	lseason = len(jds)/nseasons
	noverlap = int(overlapfrac*lseason)

	# we define the jds range...
			
	sinit  = [int(0) , int(lseason+noverlap)]
	smid   = [int(lseason-noverlap/2) , int(2*lseason+noverlap/2)]
	sfinal = [int(len(jds)-lseason-noverlap) , int(len(jds))] 
	
	# now, let's create the truncated lightcurves

	cuts=[]
	
	for l in lcs:
	
		jd1 = jds[sinit[0]:sinit[1]]
		jd2 = jds[smid[0]:smid[1]]
		jd3 = jds[sfinal[0]:sfinal[1]]
		
		mags = l.getmags()
		mag1 = mags[sinit[0]: sinit[1]]
		mag2 = mags[smid[0]: smid[1]]
		mag3 = mags[sfinal[0]:sfinal[1]]		
		
		magerrs = l.getmagerrs()
		magerr1 = magerrs[sinit[0]: sinit[1]]
		magerr2 = magerrs[smid[0]: smid[1]]
		magerr3 = magerrs[sfinal[0]:sfinal[1]]		
		
		lc1 = pycs.gen.lc.factory(jd1,mag1,magerr1)
		lc1.plotcolour='blue'
		lc2 = pycs.gen.lc.factory(jd2,mag2,magerr2)
		lc2.plotcolour='black'
		lc3 = pycs.gen.lc.factory(jd3,mag3,magerr3)
		lc3.plotcolour='red'		
		
		cuts.append([lc1,lc2,lc3])

	# Ok, now the cutted lcs are created. We want to return something like
	# [lcA_1, lcB_1] (first season),[lcA_2, lcB_2] (second season)... 
		
	return map(None,*cuts)



def cutdb(filepath,newpath,season):

	import sys	
	"""
	small hand-tuned function to cut the d3cs database in two
	"""

	db=open(filepath,'r')
	newdb=open(newpath,'w')
	
	
	lines = db.readlines()

	#for ind,line in enumerate(lines):
		#print ind,line
		
	if season == 2:
		cut = 7518 
	
	for line in lines[cut:]:
		newdb.write(line)	
	 	 
	db.close()
	newdb.close()
		
		
	
