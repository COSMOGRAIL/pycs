import pycs
import os
import numpy as np

"""
d3csests = pycs.tdc.est.importfromd3cs("/Users/mtewes/Desktop/TDC/d3cs_logs/2014-06-06_danka_removed.txt")

datadir = "/Users/mtewes/Desktop/TDC/pycs_svn_tdc1/results_tdc1"
dousel = pycs.gen.util.readpickle(os.path.join(datadir, 'groupedestimates/doubtlesses.pkl'))

douests = pycs.tdc.est.select(d3csests,idlist=dousel)


combidouests = pycs.tdc.est.multicombine(douests, method='d3cscombi1')

pycs.gen.util.writepickle(combidouests, "combidouests.pkl")
"""


combidouests = pycs.gen.util.readpickle("combidouests.pkl")


def export(estimates, filepath):
	"""
	Saves the estimates into a FITS table for interactive inspection with tools like topcat
	"""
	
	try:
		import pyfits
	except:
		print "pyfits could not be imported, no problem if you don't need it."
	
	fields = ["rung", "pair", "td", "tderr", "ms", "confidence", "timetaken"]
	
	cols = [pyfits.Column(name=a, format="D", array=np.array([getattr(e, a) for e in estimates])) for a in fields]
	
	coldefs = pyfits.ColDefs(cols)
	tbhdu = pyfits.new_table(coldefs)
	tbhdu.writeto(filepath, clobber=True)
	print "Wrote %s" % (filepath)
	



export(combidouests, "test.fits")