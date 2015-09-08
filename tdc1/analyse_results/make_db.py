import pycs
import numpy as np
import os,sys

"""
Let's build a DB with:
	- Pairs in TDC1 (ecxlude delay < 10 days)
	- True values of delay
	- Submissions td, tderr and metrics
	- Original D3CS confidence and estimations (td, tderr)
	- Extra statistices on the pairs (vratio, overlap)
	- Personnal D3CS user value, for fun...

"""

execfile('../config.py')


##############	Initialization ##############
db = {} # we'll use a dictionnary for building the big unique db, easier to index, and convert it to a list later.

for rung in range(5):
	for pair in range(0, 1038):
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid] = {"rung":rung, "pair":pair, "in_tdc1":0} # By default, a pair is not in tdc1.

		db[pairid]["id"] = pairid
		
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

		# Pairs such that truetd < 10 are discarded for the analysis
		if abs(db[pairid]["truetd"]) <10.0:
			db[pairid]["in_tdc1"] = 1
print "Done with truth..."


##############   Add pycs submissions values  ##############
### For each submission, we compute also its individual P, chi2, A for each curve

def addsubmission(db, subpath):

	print '='*5, subpath, '='*5
	# read the submission	
	subinfos = pycs.tdc.util.readsubmission(subpath)

	# rename if a bugfix version exists:
	subname = os.path.basename(subpath).split('.dt')[0].split('-bugfix')[0]

	# add values
	for info in subinfos:
	
		# td and tderr
		db[info[0]]["%s_td" % (subname)]  	= info[1]
		db[info[0]]["%s_tderr" % (subname)] 	= info[2]
	
		# P
		db[info[0]]["%s_P" % subname]		= abs(info[2]/db[info[0]]["truetd"])
		
		# A and Amod (remove absolute value in the denominator should be sufficient...)
		db[info[0]]["%s_Amod" % subname]		= (info[1]-db[info[0]]["truetd"])/abs(db[info[0]]["truetd"])
		db[info[0]]["%s_A" % subname]	= (info[1]-db[info[0]]["truetd"])/db[info[0]]["truetd"] 
		
		# chi2
		db[info[0]]["%s_chi2" % subname]	= ((info[1]-db[info[0]]["truetd"])/info[2])**2		
	
		
		
# Now, add all pycs submissions, BUGFIXED version

subdir = pycs_submissions
subdir_bugfix = pycs_submissions_bugfix

submissions = [entry.split('\n')[0] for entry in os.popen('ls %s' % subdir)]
submissions_bugfix = [entry.split('\n')[0] for entry in os.popen('ls %s' % subdir_bugfix) if 'bugfix' in entry]


finalsubs = []

for submission in submissions:
	switch = 0
	for submission_bugfix in submissions_bugfix:
		if submission.split('.dt')[0] in submission_bugfix.split('.dt')[0]:
			finalsubs.append([subdir_bugfix,submission_bugfix])
			switch = 1
	if switch == 0:
		finalsubs.append([subdir,submission])

for finalsub in finalsubs:
	print finalsub[1]


for finalsub in finalsubs:
	addsubmission(db,os.path.join(finalsub[0],finalsub[1]))

'''
subdir = '../results_tdc1/submissions/bugfix'
submissions = [entry.split('\n')[0] for entry in os.popen('ls %s' % subdir)]

for submission in submissions:
	addsubmission(db,os.path.join(subdir,submission))
'''
print "Done with submissions..."






##############   Final D3CS confidence + estimate (based on combiconf2 and GOD stuff)   ##############
ag = pycs.gen.util.readpickle(os.path.join(results_tdc1, "combi_confidence_ids/combiests_ag.pkl"))

for est in ag:
	db[est.id]["d3cs_combi_td"] = est.td
	db[est.id]["d3cs_combi_abstd"] = abs(est.td)
	db[est.id]["d3cs_combi_tderr"] = est.tderr
	if est.td != 0.0:
		db[est.id]["d3cs_combi_reltderr"] = est.tderr / abs(est.td)
	else:
		db[est.id]["d3cs_combi_reltderr"] = 999.0

	db[est.id]["d3cs_combi_ms"] = est.ms
	db[est.id]["confidence"] = est.confidence # That is the final GOD adjusted confidence.

	if "GOD" in est.methodpar:
		db[est.id]["god"] = 1
	else:
		db[est.id]["god"] = 0

	db[est.id]["d3cs_combiconf2_code"] = est.code # The "long" one, like 42...

print "Done with D3CS final values..."

##############   xtrastats    ##############
for rung in range(5):
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)

		relfilepath = pycs.tdc.util.tdcfilepath(set="tdc1", rung=rung, pair=pair, skipset=False)
		pklpath = os.path.join(xtrastatsdir, relfilepath+".stats.pkl")
		if os.path.exists(pklpath):

			data = pycs.gen.util.readpickle(pklpath, verbose=False)

			# We can add some extra calculations that are not yet in the pkl files here (instead of redoign all the pkls...)
			data["vratiomin"] = min(data["vratioA"], data["vratioB"])

			db[pairid].update(data) # We add this dict content to the existing dict.


print "Done with xtrastats..."

##############   Overlap    ##############
# We compute a few more stats, making use of the D3CS time delays.

for (key, item) in db.items(): # Loop over the full database

	if item["in_tdc1"] == 0:
		continue # We skip these ones

	# Computing the overlap.
	# Kind of tricky, the real equation should make use of modulos or some explicit computation I guess.
	# Here is a fast approx for short delays, "next-season-overlap" is not counted.

	try:
		item["d3cs_overlap_per_seas_days"] = np.clip(item["meanseaslen"] - abs(item["d3cs_combi_td"]), 0.0, item["meanseaslen"])
		item["d3cs_overlap_days"] = item["nseas"]*item["d3cs_overlap_per_seas_days"]
		item["d3cs_overlap_epochs"] = item["d3cs_overlap_days"]/item["meansampling"]
	except:
		print item
		sys.exit()


	try:
		item["truth_overlap_per_seas_days"] = np.clip(item["meanseaslen"] - abs(item["truetd"]), 0.0, item["meanseaslen"])
		item["truth_overlap_days"] = item["nseas"]*item["truth_overlap_per_seas_days"]
		item["truth_overlap_epochs"] = item["truth_overlap_days"]/item["meansampling"]
	except:
		print item
		sys.exit()

print "Done with overlap..."


##############   Add d3cs users values (td, tderr, conf, timetaken)  ##############
def addusers(db, username):

	# read the d3cs database:
	
	pairs = pycs.tdc.util.listtdc1v2pairs()
	iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
	iniests = pycs.tdc.est.select(iniests, pairs= pairs)
	
	estimates = [est for est in iniests if est.methodpar == username]
	estimates = pycs.tdc.est.multicombine(estimates,method='d3cscombi1-keepbestconf') # to remove doublons
	
	pairids = [est.id for est in estimates]
	
	for pairid,est in zip(pairids,estimates):
	
		db[pairid]["%s_td" % username]	= est.td
		db[pairid]["%s_tderr" % username]	= est.tderr
		db[pairid]["%s_confidence" % username]	= est.confidence
		db[pairid]["%s_timetaken" % username]	= est.timetaken

		# compute the individual metric values

		# P
		db[pairid]["%s_P" % username]		= abs(est.tderr/db[pairid]["truetd"])

		# A and Amod (remove absolute value in the denominator should be sufficient...)
		db[pairid]["%s_Amod" % username]		= (est.td-db[pairid]["truetd"])/abs(db[pairid]["truetd"])
		db[pairid]["%s_A" % username]	= (est.td-db[pairid]["truetd"])/db[pairid]["truetd"]

		# chi2
		db[pairid]["%s_chi2" % username]	= ((est.td-db[pairid]["truetd"])/est.tderr)**2
# Now, add various users: (add all of them?)

users_to_add = ["Vivien","mtewes","Fred","Thibault"]

for user in users_to_add:
	addusers(db,user)
print "Done with D3CS individual users..."
	
##############   pkl export    ##############

# We keep it as a dict of dicts, it's easier to "query" in this way:

pklfilepath = "dbwithout10days_bugfix.pkl"
pycs.gen.util.writepickle(db, pklfilepath)

#print "="*50
#print "List of available keywords"
#for kw in db["tdc1_0_1"]:
#	print kw