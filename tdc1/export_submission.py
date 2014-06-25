"""
We read in the database (from the pkl), and prepare a submission file.
"""

execfile("config.py")

import pycs
import os
import numpy as np


subname  = "pycs_tdc1_test"
filepath = os.path.join(pycsresdir,'submissions',subname,subname+'.dt')
dirpath = os.path.dirname(filepath)
commentlist = ["D3CS combi", "confidence 1"]



db = pycs.gen.util.readpickle("joined.pkl").values() # We want this as a list.

# Typically we first select some of the pairs according to some generic criteria
# This can be done in several ways. Here is an example:

sel = []
dbintdc1 = [entry for entry in db if entry["in_tdc1"]]

for entry in dbintdc1:
	
	isin = False
	# Add your own criteria here...
	
	if entry["confidence"] in [1]:	
		isin = True
	
	# And we build our selection:
	if isin:
		sel.append(entry)


print "I have selected %i potential entries" % (len(sel))	



# Now we try to build estimates from this selection of entries.
# We might want to mix different fields to do this.
# Safest is to explicitly complain if one of those fields does not exist !

estimates = []

for entry in sel:
	
	try:
		est = pycs.tdc.est.Estimate(
			set = "tdc1",
			rung = entry["rung"],
			pair = entry["pair"],
			td = entry["d3cs_combi_td"],
			tderr = entry["d3cs_combi_tderr"]			
		)
		estimates.append(est)
		
	except KeyError as message:
		print "Could not include %i %i"% (entry["rung"], enstry["pair"])
		print "Missing field:", message
		#print entry


print "I could build %i estimates" % (len(estimates))	


if not os.path.isdir(dirpath):
	print 'I create the new submission directory %s \n' %dirpath
	os.mkdir(dirpath)



pycs.tdc.metrics.maxPplot([estimates], N=5120, filepath = os.path.join(dirpath,"%s.maxPplot.png" %subname))

pycs.tdc.util.writesubmission(estimates, filepath, commentlist)

os.system('cp export_submission.py %s' %os.path.join(dirpath,'export_submission_%s.py' %subname))




