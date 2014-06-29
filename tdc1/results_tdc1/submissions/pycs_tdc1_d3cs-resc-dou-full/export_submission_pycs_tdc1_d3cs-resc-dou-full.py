"""
We read in the database (from the pkl), and prepare a submission file.
"""

execfile("config.py")

import pycs
import os
import numpy as np


subname  = "pycs_tdc1_d3cs-resc-dou-full"
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

d3cserrs = []
d3csseps = []

for entry in sel:
	
	try:
	
		td = entry["d3cs_combi_td"]
		
		# dou
		tderr = entry["d3cs_combi_tderr"] / 5.67887111831 
		
		# doupla
		#tderr = entry["d3cs_combi_tderr"] / 5.2323768897 
		
		
		d3cserrs.append(tderr)
		d3csseps.append(abs(td - entry["pycs_spl3_Bonn_td"]))
		
		#td = entry["pycs_spl3_Bonn_td"]
		#tderr = entry["pycs_spl3_Bonn_tderr"]
		
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


medd3cssep = np.median(np.array(d3csseps))
medd3cserr = np.median(np.array(d3cserrs))
print medd3cserr, medd3cssep, medd3cserr/medd3cssep

"""
import matplotlib.pyplot as plt
plt.hist(np.array(d3csseps), label="D3CS-spl3 separations", range=(0, 12), bins=50, alpha=0.5)
plt.hist(np.array(d3cserrs), label="D3CS tderrs", range=(0, 12), bins=50, alpha = 0.5)
plt.legend()
plt.title("doupla")
plt.show()
exit()
"""

print "I could build %i estimates" % (len(estimates))	

# The godtweak
cleanestimates = pycs.tdc.util.godtweak(estimates)


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

