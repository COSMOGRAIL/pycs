import pycs
import numpy as np
import os,sys

"""
Let's build a DB with:
	- True values of delay
	- Confidence levels
	- All our submissions
	
	
To add:
	- Submissions of other teams
	- Stats from joined.py (overlap ?)	
"""

##############	Initialization ##############

db = {} # we'll use a dictionnary for building the big unique db, easier to index, and convert it to a list later.

for rung in range(5):
	for pair in range(1, 1037):
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid] = {"rung":rung, "pair":pair, "in_tdc1":0} # By default, a pair is not in tdc1.
		
		db[pairid]["is_quad"] = 0
		if pair > 720:
			db[pairid]["is_quad"] = 1

			
##############   Some pairs where rejected, we mark this with a flag  ##############

for rung in range(5):
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid]["in_tdc1"] = 1



##############   Add the true time delay  ##############

# read the truthfile:
truth = open('truth.txt','r').readlines()

for rung in range(5):
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		
		# get the name of the pair in TDC standards
		name = pycs.tdc.util.tdcfilepath('tdc1', rung, pair).split('/')[-1]
	
		index = [line.split(' ')[0] for line in truth].index(name)
		

		db[pairid]["truetd"] = -1.0* float(truth[index].split(' ')[-1]) # Do NOT forget the "-" sign to match pycs standards


		
##############   Add pycs submissions values  ##############

def addsubmission(db, subpath):

	# read the submission	
	subinfos = pycs.tdc.util.readsubmission(subpath)
	subname = os.path.basename(subpath).split('.dt')[0]

	for info in subinfos:
		db[info[0]]["%s_td" % (subname)]  	= info[1]
		db[info[0]]["%s_tderr" % (subname)] 	= info[2]
		
		
# Now, add all pycs submissions

subdir = "pycs_submissions"
submissions = [entry.split('\n')[0] for entry in os.popen('ls %s' % subdir)]		

for submission in submissions:
	addsubmission(db,os.path.join(subdir,submission))
	
	
	
##############   pkl export    ##############

# We keep it as a dict of dicts, it's easier to "query" in this way:

pklfilepath = "db.pkl"
pycs.gen.util.writepickle(db, pklfilepath)
