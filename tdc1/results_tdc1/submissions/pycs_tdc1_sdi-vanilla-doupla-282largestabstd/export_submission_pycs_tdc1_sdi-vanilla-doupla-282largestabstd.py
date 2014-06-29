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
commentlist = []

print ''
print 'You are going to run on %s' % subname
pycs.tdc.util.goingon()

db = pycs.gen.util.readpickle("joined.pkl").values() # We want this as a list.

# Typically we first select some of the pairs according to some generic criteria
# This can be done in several ways. Here is an example:

sel = []
dbintdc1 = [entry for entry in db if entry["in_tdc1"]]

for entry in dbintdc1:
	
	
	isin = False
	# Add your own criteria here...
	
	# doubtless, plausible...
	if entry["confidence"] in [1,2]:	
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
	
		# select the sdi outputs 
		td = entry["pycs_sdi1_td"]
		tderr = entry["pycs_sdi1_tderr"]
		
		'''
		# small check on tderr size, to kill  monstruous outliers...
		if tderr > 9999:
			print "tderr > 9999 (oh god!) : %i %i"% (entry["rung"], entry["pair"])
			continue
		'''
			
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
		print "Could not include %i %i"% (entry["rung"], enstry["pair"])
		print "Missing field:", message
		#print entry


print "I could build %i estimates" % (len(estimates))	


# Build the directory
if not os.path.isdir(dirpath):
	print 'I create the new submission directory %s \n' %dirpath
	os.mkdir(dirpath)


# Gott als Putzfrau
cleanestimates = pycs.tdc.util.godtweak(estimates)


for cleanest in cleanestimates: # because of sorted !
	if cleanest.td == 0.0:
		print " I tweak %s td value to 0.001" %cleanest.id
		cleanest.td = 0.001


# Here, we select only the best n curves for the P metric
sortedPestimates = pycs.tdc.metrics.sortbyabstd(cleanestimates)
#n=int(len(cleanestimates)*0.98)
n=282

selectPestimates = sortedPestimates # do nothing
selectPestimates = sortedPestimates[-n:] # select
print "I select %i percent of the total sample !" %(float(n)/len(cleanestimates)*100.0)


pycs.tdc.metrics.maxPplot([selectPestimates], N=5120, filepath = os.path.join(dirpath,"%s.maxPplot.png" %subname))
pycs.tdc.util.writesubmission(selectPestimates, filepath, commentlist)

os.system('cp export_submission.py %s' %os.path.join(dirpath,'export_submission_%s.py' %subname))


# This looks nice. I take. (read it out loud with a russian accent)
#####
# This tells you the n to select so to get 3% of average P

for n in range(1, len(sortedPestimates)):
	meanP = np.mean(np.array([abs(est.tderr / est.td) for est in sortedPestimates[-n:]]))
	#print n, meanP
	if meanP >= 0.03:
		print "P = 3%% would be reached by selecting %i best curves" % (n)
		break
#####

