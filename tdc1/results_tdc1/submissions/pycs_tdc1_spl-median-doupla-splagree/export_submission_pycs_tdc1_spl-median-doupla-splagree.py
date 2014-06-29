"""
We read in the database (from the pkl), and prepare a submission file.
"""

execfile("config.py")

import pycs
import os
import numpy as np


subname  = "pycs_tdc1_spl-median-doupla-splagree"
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
	
	if entry["confidence"] in [1, 2]:	
		isin = True
	
	# And we build our selection:
	if isin:
		sel.append(entry)

"""
####
# We compute the scaling factor
d3cserrs = np.array([entry["d3cs_combi_tderr"] for entry in sel])
spl3errs = np.array([entry["pycs_spl3_Bonn_tderr"] for entry in sel])
import matplotlib.pyplot as plt
plt.hist(d3cserrs, range=(0, 20), bins=50)
plt.hist(spl3errs, range=(0, 20), bins=50)
plt.show()
print "Scaling factor", np.median(d3cserrs), np.median(spl3errs), np.median(d3cserrs) / np.median(spl3errs) 
exit()
#####
"""

print "I have selected %i potential entries" % (len(sel))	

# Now we try to build estimates from this selection of entries.
# We might want to mix different fields to do this.
# Safest is to explicitly complain if one of those fields does not exist !

estimates = []

for entry in sel:
	
	try: # This time we might have some non-available estimates ! 
	
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

		########## Checking if methods mutually agree ###########
		isok = True
		tds = []
		tderrs = []
		for code in ["spl3_Bonn", "spl3_EPFL_ml183", "spl3_EPFL_k1.5", "spl3_EPFL_ms12", "spl3_EPFL_k1.5_ml183", "spl2"]:
			checktd = entry["pycs_%s_td" % (code)]
			checktderr = entry["pycs_%s_tderr" % (code)]
			tds.append(checktd)
			tderrs.append(checktderr)
		
		# We check if the individual estimates agree within f sigma:
		for i in range(len(tds)):
			for j in range(len(tds)):
				if abs(tds[i]-tds[j]) > 1.5*tderrs[i] or abs(tds[i]-tds[j]) > 1.5*tderrs[j]:
					isok = False
					#print "Kicking due to %s:" % (code)
					#print td, tderr, "not compatible with", checktd, checktderr
			
		# We check that the errorbars stay in a similar range:
		if np.max(np.array(tderrs)) > 3.0 * np.min(np.array(tderrs)):
			isok = False
			#print "Kicking due to error bars", tderrs
			
		if not isok:
			#print "kick"
			continue
		
		# Else, we take the median of the delays, and the median error bar.
		td = np.median(np.array(tds))
		tderr = np.median(np.array(tderrs))
			
	
		################################################
		
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
		#print entry # This time we do have some missing estimates...
		#exit()


print "I could build %i estimates" % (len(estimates))	


# The godtweak
cleanestimates = pycs.tdc.util.godtweak(estimates)

"""
# The clip in error bar:
mintderr = 1.0
for cleanest in cleanestimates:
	if cleanest.tderr < mintderr:
		cleanest.tderr = mintderr
"""

"""
# For the sortbyP:
for cleanest in cleanestimates:
	if cleanest.td == 0.0:
		print "got a td of 0.0"
		cleanest.td = 0.001
		print cleanest

# Now the XbestP selection, just before writing the submission:
sortedPestimates = pycs.tdc.metrics.sortbyP(cleanestimates)
n=800
#selectPestimates = sortedPestimates
selectPestimates = sortedPestimates[-n:]

"""
"""
sortedestimates = pycs.tdc.metrics.sortbyabstd(cleanestimates)
n=286
#selectPestimates = sortedestimates
selectPestimates = sortedestimates[-n:]
"""

selectPestimates = cleanestimates

"""
#selectPestimates = [e for e in cleanestimates if abs(e.td) > 81.0]
for e in selectPestimates:
	print e
#print len(selectPestimates)
"""


pycs.tdc.util.writesubmission(selectPestimates, filepath, commentlist)

pycs.tdc.metrics.maxPplot([selectPestimates], N=5120, filepath = os.path.join(dirpath,"%s.maxPplot.png" %subname))
os.system('cp export_submission.py %s' %os.path.join(dirpath,'export_submission_%s.py' %subname))


"""
# This tells you the n to select so to get 3% of average P

for n in range(1, len(sortedPestimates)):
	meanP = np.mean(np.array([abs(est.tderr / est.td) for est in sortedPestimates[-n:]]))
	#print n, meanP
	if meanP >= 0.03:
		print "P = 3%% would still be possible by selecting %i best curves" % (n)
		break
"""

