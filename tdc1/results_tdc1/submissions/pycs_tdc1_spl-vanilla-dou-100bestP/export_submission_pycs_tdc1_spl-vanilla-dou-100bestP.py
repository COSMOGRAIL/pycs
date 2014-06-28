"""
We read in the database (from the pkl), and prepare a submission file.
"""

execfile("config.py")

import pycs
import os
import numpy as np


subname  = "pycs_tdc1_spl-vanilla-dou-100bestP"
filepath = os.path.join("results_tdc1",'submissions',subname,subname+'.dt')
dirpath = os.path.dirname(filepath)
commentlist = []

if not os.path.isdir(dirpath):
	print 'I create the new submission directory %s \n' %dirpath
	os.mkdir(dirpath)

db = pycs.gen.util.readpickle("joined.pkl").values() # We want this as a list.


sel = []
dbintdc1 = [entry for entry in db if entry["in_tdc1"]]

for entry in dbintdc1:
	
	isin = False
	
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
	
	try: # We do not want to skip non-existing fields, but crash nicely. 
	
		td = entry["pycs_spl3_Bonn_td"]
		tderr = entry["pycs_spl3_Bonn_tderr"]
		
		
		# Checking if within 1.5 sigma
		if abs(td - entry["d3cs_combi_td"]) > 1.5 * entry["d3cs_combi_tderr"]:
			print "Not within D3CS: %i %i"% (entry["rung"], entry["pair"])
			continue
			
		# Default cut in D3CS error bar for plausibles
		if entry["confidence"] in [2,3] and entry["d3cs_combi_tderr"] > 30.0:
			print "D3CS error > 30: %i %i"% (entry["rung"], entry["pair"])
			continue
		
		est = pycs.tdc.est.Estimate(
			set = "tdc1",
			rung = entry["rung"],
			pair = entry["pair"],
			td = td,
			tderr = tderr			
		)
		estimates.append(est)
		
	except KeyError as message:
		print "Could not include %i %i"% (entry["rung"], entry["pair"])
		print "Missing field:", message
		print entry
		exit()


print "I could build %i estimates" % (len(estimates))	


# The godtweak
cleanestimates = pycs.tdc.util.godtweak(estimates)

# For the sortbyP:
for cleanest in cleanestimates: # because of sorted !
	if cleanest.td == 0.0:
		print "got a td of 0.0"
		cleanest.td = 0.001
		print cleanest

# Now the XbestP selection, just before writing the submission:


#selectPestimates = cleanestimates

sortedPestimates = pycs.tdc.metrics.sortbyP(cleanestimates)
n=100
selectPestimates = sortedPestimates[-n:]

pycs.tdc.util.writesubmission(selectPestimates, filepath, commentlist)

pycs.tdc.metrics.maxPplot([selectPestimates], N=5120, filepath = os.path.join(dirpath,"%s.maxPplot.png" %subname))
os.system('cp export_submission.py %s' %os.path.join(dirpath,'export_submission_%s.py' %subname))




