"""
We read in the database (from the pkl), and prepare a submission file.
"""

execfile("config.py")

import pycs
import os
import numpy as np


subname  = "pycs_tdc1_spl-vanilla-doupla-full"
filepath = os.path.join("results_tdc1",'submissions',subname,subname+'.dt')
dirpath = os.path.dirname(filepath)
commentlist = []

db = pycs.gen.util.readpickle("joined.pkl").values() # We want this as a list.


sel = []
dbintdc1 = [entry for entry in db if entry["in_tdc1"]]

for entry in dbintdc1:
	
	isin = False
	
	if entry["confidence"] in [1, 2]:	
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
		if entry["confidence"] == 2 and entry["d3cs_combi_tderr"] > 20.0:
			print "Pla D3CS error > 20: %i %i"% (entry["rung"], entry["pair"])
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


if not os.path.isdir(dirpath):
	print 'I create the new submission directory %s \n' %dirpath
	os.mkdir(dirpath)

pycs.tdc.metrics.maxPplot([estimates], N=5120, filepath = os.path.join(dirpath,"%s.maxPplot.png" %subname))

cleanestimates = pycs.tdc.util.godtweak(estimates)
pycs.tdc.util.writesubmission(cleanestimates, filepath, commentlist)

os.system('cp export_submission.py %s' %os.path.join(dirpath,'export_submission_%s.py' %subname))




