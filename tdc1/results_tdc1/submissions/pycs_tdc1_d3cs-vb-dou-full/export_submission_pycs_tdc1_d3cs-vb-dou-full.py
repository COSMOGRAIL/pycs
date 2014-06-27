"""
We read in the database (from the pkl), and prepare a submission file.
"""

execfile("config.py")

import pycs
import os
import numpy as np


subname  = subname
filepath = os.path.join("results_tdc1",'submissions',subname,subname+'.dt')
dirpath = os.path.dirname(filepath)
commentlist = ["D3CS combi", "vanilla parameters", "doubtless and plausible estimates", "full range"]

print ''
print 'You are going to run on %s' % subname
pycs.tdc.util.goingon()
'''
db = pycs.gen.util.readpickle("joined.pkl").values() # We want this as a list.

# Typically we first select some of the pairs according to some generic criteria
# This can be done in several ways. Here is an example:

sel = []
dbintdc1 = [entry for entry in db if entry["in_tdc1"]]

for entry in dbintdc1:
	
	
	isin = False
	# Add your own criteria here...
	
	# doubtless, plausible...
	if entry["confidence"] in [1]:	
		isin = True
	
	# D3CS only, reject tderr >30 for plausibles and multimodal
	if entry["confidence"] in [2,3] and entry["d3cs_combi_tderr"] > 30:
		isin = False
		

	
	
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
'''

# We select the estimates from the d3cs database, good old way of doing things...


pairs = pycs.tdc.util.listtdc1v2pairs()
iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
iniests = pycs.tdc.est.select(iniests, pairs= pairs)

# Select Vivien only

estimates = [est for est in iniests if est.methodpar == "Vivien"]


# Select the confidence level
estimates = pycs.tdc.est.multicombine(estimates,method='d3cscombi1-keepbestconf') # to remove doublons...
estimates = [est for est in estimates if est.confidence in [1]] #doubtless only


# Standard D3CS rejection:
estimates = [est for est in estimates if est.tderr < 30.0]


if not os.path.isdir(dirpath):
	print 'I create the new submission directory %s \n' %dirpath
	os.mkdir(dirpath)

cleanestimates = pycs.tdc.util.godtweak(estimates)



for cleanest in cleanestimates: # because of sorted !
	if cleanest.td == 0.0:
		print " I tweak %s td value to 0.001" %cleanest.id
		cleanest.td = 0.001

# Here, we select only the best n curves for the P metricyes

sortedPestimates = pycs.tdc.metrics.sortbyP(cleanestimates)
n=100

selectPestimates = sortedPestimates # do nothing
#selectPestimates = sortedPestimates[-n:] # select



pycs.tdc.metrics.maxPplot([selectPestimates], N=5120, filepath = os.path.join(dirpath,"%s.maxPplot.png" %subname))
pycs.tdc.util.writesubmission(selectPestimates, filepath, commentlist)

os.system('cp export_submission.py %s' %os.path.join(dirpath,'export_submission_%s.py' %subname))




