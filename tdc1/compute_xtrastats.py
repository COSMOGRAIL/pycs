"""
Save some time-delay-indpendant stats about the light curves into pkl files, one per pair.
"""

execfile("config.py")

import pycs
import os
import numpy as np

def variostats(lcs):
	"""
	Collect some time-delay-independant statistics about the light curves.
	"""
	
	
	samplingstats = lcs[0].samplingstats()
	varioa = pycs.tdc.vario.vario(lcs[0], nsamp=1000000)
	variob = pycs.tdc.vario.vario(lcs[1], nsamp=1000000)
	
	knotstep = pycs.tdc.splopt.calcknotstep([varioa, variob])
	
	magsa = lcs[0].getmags()
	magsb = lcs[1].getmags()
	magerrsa = lcs[0].getmagerrs()
	magerrsb = lcs[1].getmagerrs()
	
	return {
		"nepochs":len(lcs[0]),
		"nseas":samplingstats["nseas"],
		"meanseasgap":samplingstats["meansg"],
		"stdseasgap":samplingstats["stdsg"],
		"meanseaslen": 365.0 - samplingstats["meansg"],
		"meansampling":samplingstats["mean"],
		"stdsampling":samplingstats["std"],
		"medmagA":np.median(magsa),
		"medmagB":np.median(magsb),
		"medmagerrA":np.median(magerrsa),
		"medmagerrB":np.median(magerrsb),
		"vratioA":varioa["vratio"],
		"vratioB":variob["vratio"],
		"variofirstvalA":varioa["firstval"],
		"variofirstvalB":variob["firstval"],
		"variozonevalA":varioa["zoneval"],
		"variozonevalB":variob["zoneval"],
		"vratiomax":max(varioa["vratio"], variob["vratio"]),
		"vratiomin":min(varioa["vratio"], variob["vratio"]),
		"knotstep":knotstep
		
	}
	


#for rung in [4]:
#	for pair in pycs.tdc.util.listtdc1v2pairs():
	
for rung in [0, 1, 2, 3, 4]:
	for pair in pycs.tdc.util.listtdc1v2pairs():


		relfilepath = pycs.tdc.util.tdcfilepath(set="tdc1", rung=rung, pair=pair, skipset=False)
		outpath = os.path.join(xtrastatsdir, relfilepath+".stats.pkl")
		if os.path.exists(outpath):
			print "Skipping %s, already done." % (outpath)
			continue
		
		
		lcs = pycs.tdc.util.read(os.path.join(datadir, relfilepath), mag="asinh", verbose=True, shortlabel=False)

		res = variostats(lcs)
		
		#res["rung"] = rung
		#res["pair"] = pair
		#print res
		
			
		if not os.path.exists(os.path.dirname(outpath)):
			os.makedirs(os.path.dirname(outpath))
		pycs.gen.util.writepickle(res, outpath)		
		
		
		
