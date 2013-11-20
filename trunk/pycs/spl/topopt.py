"""
Higher level wrappers around the multiopt optimizers

We do not define the microlensing inside of the optimizer, we really just optimize it.

The functions must return a final optimal spline. This spline object also contains its final r2, saved into the pkl, and used for plots etc.

"""

import sys
sys.path.append("../")			

import pycs.gen.util
import pycs.gen.lc
import pycs.gen.splml
import pycs.gen.spl
import pycs.spl.multiopt


def opt_rough(lcs, nit = 5, shifttime=True, crit="r2", 
	knotstep=100, stabext=300.0, stabgap=20.0, stabstep=4.0, stabmagerr=-2.0,
	verbose=True):
	"""
	Getting close to the good delays, as fast as possible : no BOK (i.e. knot positions are not free), only brute force without optml.
	Indeed with optml this tends to be unstable.
	
	.. note:: This function is here to correct for shift errors in the order of 20 days, hence its name.
	
	:param nit: a number of iterations (ok to leave default : 5)
	:param splstep: the step (in days) between the knots of the spline.
		100 is default. Lower this to eg 50 if your curve has very short term intrinsic variations, increase it if your curve is very noisy.	
	
	"""
	if verbose:
		print "Starting opt_rough on initial delays :"
		print pycs.gen.lc.getnicetimedelays(lcs, separator=" | ")
	
	pycs.spl.multiopt.opt_magshift(lcs)
	
	# If there is a curve without ML, we aim at this one first
	nomllcs = [l for l in lcs if l.ml == None]
	if len(nomllcs) == 0:
		# Spline though the first curve :
		if verbose:
			print "Aiming at first curve."
		spline = pycs.gen.spl.fit([lcs[0]], knotstep = knotstep, stab=True, stabext=stabext, 
			stabgap=stabgap, stabstep=stabstep, stabmagerr=stabmagerr, bokit = 0, verbose=False)
	else:
		# Spline through the fixed curves :
		if verbose:
			print "Aiming at curves %s." % (", ".join([l.object for l in nomllcs]))
		spline = pycs.gen.spl.fit(nomllcs, knotstep = knotstep, stab=True, stabext=stabext, 
			stabgap=stabgap, stabstep=stabstep, stabmagerr=stabmagerr, bokit = 0, verbose=False)

	pycs.spl.multiopt.opt_ml(lcs, spline, bokit=0, splflat=True, verbose=False)
	
	# Spline to go through all curves :
	spline = pycs.gen.spl.fit(lcs, knotstep = knotstep, stab=True, stabext=stabext, 
			stabgap=stabgap, stabstep=stabstep, stabmagerr=stabmagerr, bokit = 0, verbose=False)
	pycs.spl.multiopt.opt_ml(lcs, spline, bokit=0, splflat=True, verbose=False)
	pycs.spl.multiopt.opt_source(lcs, spline, dpmethod="extadj", bokit = 0, verbose=False, trace=False)
	
	if verbose:
		print "First spline and ML opt done."
	
	for it in range(nit):
		if shifttime:
			pycs.spl.multiopt.opt_ts_indi(lcs, spline, optml=False, method="brute", crit=crit, brutestep=1.0, bruter=20, verbose = False, trace=False)
		pycs.spl.multiopt.opt_source(lcs, spline, dpmethod="extadj", bokit = 0, verbose=False, trace=False)
		pycs.spl.multiopt.opt_ml(lcs, spline, bokit=0, splflat=True, verbose=False)
		pycs.spl.multiopt.opt_source(lcs, spline, dpmethod="extadj", bokit = 0, verbose=False, trace=False)
	
		if verbose:
			print "%s    (Iteration %2i, r2 = %8.1f)" % (pycs.gen.lc.getnicetimedelays(lcs, separator=" | "), it+1, spline.lastr2nostab)	
		
	if verbose:
		print "Rough time shifts done :"
		print "%s" % (pycs.gen.lc.getnicetimedelays(lcs, separator=" | "))	
	
	
	return spline
	
	



def opt_fine(lcs, spline=None, nit=10, shifttime=True, crit="r2", 
	knotstep=20, stabext=300.0, stabgap=20.0, stabstep=4.0, stabmagerr=-2.0,
	bokeps=10, boktests=10, bokwindow=None,
	redistribflux=False, splflat=True, verbose=True, trace=False, tracedir = "opt4"):
	"""
	Fine approach, we assume that the timeshifts are within 2 days, and ML is optimized.
	
	Watch out for splflat, a bit dangerous all this ...
	Default is True for the iterations, and we release the splines only at the end.
	If you put it to False, spline are left free at any stage. This should be fine if you leave one curve without ML.
	
	:param spline: If this is None, I will fit my own spline, but then I expect that your lcs already overlap (i.e., ML is set) !
		If you give me a spline, I will use it (in this case I disregard your splstep setting !)
	
	"""
	
	if verbose:
		print "Starting opt_fine on initial delays :"
		print pycs.gen.lc.getnicetimedelays(lcs, separator=" | ")
	
	
	if spline == None:
		spline = pycs.gen.spl.fit(lcs, knotstep = knotstep,
			stab=True, stabext=stabext, stabgap=stabgap, stabstep=stabstep, stabmagerr=stabmagerr,
			bokit=2, boktests=boktests, bokwindow=bokwindow, bokeps=bokeps, verbose=False)
	pycs.spl.multiopt.opt_ml(lcs, spline, bokit=2, splflat=splflat, verbose=False)
	
	
	if verbose:
		print "Iterations :"
			
	for it in range(nit):
		#if trace:
		#	pycs.gen.util.trace(lcs, [spline], tracedir = tracedir)
		if verbose:
			print "Start"
		
		if shifttime:
			pycs.spl.multiopt.opt_ts_indi(lcs, spline, optml=True, mlsplflat=splflat, method="brute", crit=crit, brutestep=0.2, bruter=10, verbose = False, trace=False)
			if verbose:
				print "opt_ts_indi brute done"
		
		pycs.spl.multiopt.opt_source(lcs, spline, dpmethod="extadj", bokit = 0, verbose=False, trace=False)
		
		if shifttime:
			pycs.spl.multiopt.opt_ts_indi(lcs, spline, optml=True, mlsplflat=splflat, method="fmin", crit=crit, verbose = False, trace=False)
			if verbose:
				print "opt_ts_indi fine done"
			
		
		pycs.spl.multiopt.opt_source(lcs, spline, dpmethod="extadj", bokit = 0, verbose=False, trace=False)
		pycs.spl.multiopt.opt_ml(lcs, spline, bokit=1, splflat=splflat, verbose=False)
		if verbose:
			print "opt_ml done"
			
		if redistribflux == True:
			# This works only for doubles
			if len(lcs) != 2:
				raise RuntimeError("I can only run redistribflux on double lenses !")
		
			pycs.spl.multiopt.redistribflux(lcs[0], lcs[1], spline, verbose=True)
		
		
		pycs.spl.multiopt.opt_source(lcs, spline, dpmethod="extadj", bokit = 1, verbose=False, trace=False)
		if verbose:
			print "opt_source BOK done"
		
		#print spline.knotstats()
		
		if verbose:
			print "%s    (Iteration %2i, r2 = %8.1f)" % (pycs.gen.lc.getnicetimedelays(lcs, separator=" | "), it+1, spline.lastr2nostab)	
		
	
	if verbose:
		print "Timeshift stabilization and releasing of splflat :"

	for it in range(5):
		
		if shifttime:
			pycs.spl.multiopt.opt_ts_indi(lcs, spline, optml=True, mlsplflat=False, method="fmin", crit=crit, verbose = False, trace=False)
		pycs.spl.multiopt.opt_source(lcs, spline, dpmethod="extadj", bokit = 0, verbose=False, trace=False)
		if verbose:
			print "%s    (Iteration %2i, r2 = %8.1f)" % (pycs.gen.lc.getnicetimedelays(lcs, separator=" | "), it+1, spline.lastr2nostab)	
	
	
	
	#if trace:
	#	pycs.gen.util.trace(lcs, [spline], tracedir = tracedir)
	return spline

