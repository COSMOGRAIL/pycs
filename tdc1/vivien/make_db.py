import pycs
import numpy as np
import os,sys
import glob

"""
Let's build a DB with:
	- True values of delay
	- d3cs Confidence levels
	- d3cs output values 
	- Crudeopt Values ! 	
"""


datadir = "/home/vivien/modules/python/pycs-2/tdc1/vivien/"
d3cslogpath = "../d3cs_logs/2014-06-07.txt"

##############	Initialization ##############

db = {} # we'll use a dictionnary for building the big unique db, easier to index, and convert it to a list later.

for rung in range(5):
	for pair in range(1, 1037):
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
truth = open('../analyse_results/truth.txt','r').readlines()

for rung in range(5):
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		
		# get the name of the pair in TDC standards
		name = pycs.tdc.util.tdcfilepath('tdc1', rung, pair).split('/')[-1]
	
		index = [line.split(' ')[0] for line in truth].index(name)
		
		db[pairid]["truetd"] = -1.0* float(truth[index].split(' ')[-1]) # Do NOT forget the "-" sign to match pycs standards

		# Pairs such that truetd < 10 are discarded for the analysis
		if abs(db[pairid]["truetd"]) <10.0:
			db[pairid]["in_tdc1"] = 0
		
##############   Add pycs submissions values  ##############

### For each submission, we compute also its individual P, chi2, A for each curve


def addsubmission(db, subpath):

	# read the submission	
	subinfos = pycs.tdc.util.readsubmission(subpath)
	subname = os.path.basename(subpath).split('.dt')[0]

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
	
		
		
# Now, add all pycs submissions

subdir = "../analyse_results/pycs_submissions"
submissions = [entry.split('\n')[0] for entry in os.popen('ls %s' % subdir)]		

for submission in submissions:
	addsubmission(db,os.path.join(subdir,submission))





	
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
	
		db[pairid]["d3cs_%s_td" % username]	= est.td
		db[pairid]["d3cs_%s_tderr" % username]	= est.tderr		
		db[pairid]["d3cs_%s_confidence" % username]	= est.confidence		
		db[pairid]["d3cs_%s_timetaken" % username]	= est.timetaken		


# Now, add various users: (add all of them?)

users_to_add = ["Vivien","mtewes","Fred","Thibault"]

for user in users_to_add:
	addusers(db,user)



##############   Add crudeopt values  ##############

def addcrudeopt(db, methodpath):
	
	dirpaths = sorted(glob.glob(os.path.join(methodpath,'tdc1_*_*')))

	for dirpath in dirpaths:
		# get rung and pair from path
		rung = dirpath.split('_')[-2]
		pair = dirpath.split('_')[-1]
		
		pairid = "%s_%i_%i" % ("tdc1", int(rung), int(pair))

		# get residuals from pkl
		#resids_perseasons_individual = pycs.gen.util.readpickle(os.path.join(dirpath,'resids_perseasons_individual.pkl')) # save it for later...
		#resids_perseasons_median = pycs.gen.util.readpickle(os.path.join(dirpath,'resids_perseasons_median.pkl'))
		#resids_perseasons_sum = pycs.gen.util.readpickle(os.path.join(dirpath,'resids_perseasons_sum.pkl'))
		#resids_singleshift = pycs.gen.util.readpickle(os.path.join(dirpath,'resids_singleshift.pkl'))

		# add them to the database

		
		# sort by medres, and take the first one and the timeshift associated

		# db[pairid]["%s_singleshift_td" %methodpath] = sorted(resids_singleshift,key=lambda resid: resid["medres"])[0]["timeshift"]
		# db[pairid]["%s_singleshift_res" %methodpath] = sorted(resids_singleshift,key=lambda resid: resid["medres"])[0]["medres"]

		# db[pairid]["%s_perseasons_median_td" %methodpath] = sorted(resids_perseasons_median,key=lambda resid: resid["medres"])[0]["timeshift"]
		# db[pairid]["%s_perseasons_median_res" %methodpath] = sorted(resids_perseasons_median,key=lambda resid: resid["medres"])[0]["medres"]

		""" # Here I take the absolute minimum
		db[pairid]["%s_perseasons_sum_td" %methodpath] = sorted(resids_perseasons_sum,key=lambda resid: resid["medres"])[0]["timeshift"]
		db[pairid]["%s_perseasons_sum_res" %methodpath] = sorted(resids_perseasons_sum,key=lambda resid: resid["medres"])[0]["medres"]

		(resids,stdmags,minparams,conflevel)= pycs.gen.util.readpickle(os.path.join(dirpath,'sums_mins.pkl'))

		meanstdmag = np.mean([resid["stdmag"] for resid in resids_perseasons_sum])
		stdstdmag = float(np.std([resid["stdmag"] for resid in resids_perseasons_sum]))
		db[pairid]["%s_perseasons_sum_stdmag" %methodpath] = abs(sorted(resids_perseasons_sum,key=lambda resid: resid["medres"])[0]["stdmag"] - meanstdmag)/stdstdmag
		"""
		# build db using minimas
		(resids,stdmags,minparams,conflevel)= pycs.gen.util.readpickle(os.path.join(dirpath,'sum_mins.pkl'))

		if len(minparams) > 0:
			minparams = sorted(minparams, key=lambda minparam: minparam["resid"]) # sort minimas by residual value

			# smallest minima parameters
			db[pairid]["%s_perseasons_sum_td" %methodpath] = minparams[0]["time"]
			db[pairid]["%s_perseasons_sum_resid" %methodpath] = minparams[0]["resid"]
			db[pairid]["%s_perseasons_sum_sigresid" %methodpath] = minparams[0]["sigres"]
			db[pairid]["%s_perseasons_sum_sigmag" %methodpath] = minparams[0]["sigmag"]

			# all minimas parameters (redundancy for the smallest minima, but who cares...)
			db[pairid]["%s_perseasons_sum_mintds" %methodpath] = [minparam["time"] for minparam in minparams]
			db[pairid]["%s_perseasons_sum_minresids" %methodpath] = [minparam["resid"] for minparam in minparams]
			db[pairid]["%s_perseasons_sum_minsigresids" %methodpath] = [minparam["sigres"] for minparam in minparams]
			db[pairid]["%s_perseasons_sum_minsigmags" %methodpath] = [minparam["sigmag"] for minparam in minparams]

		else:
			db[pairid]["%s_perseasons_sum_td" %methodpath] = 999
			db[pairid]["%s_perseasons_sum_resid" %methodpath] = 999
			db[pairid]["%s_perseasons_sum_sigresid" %methodpath] = 999
			db[pairid]["%s_perseasons_sum_sigmag" %methodpath] = 999

			db[pairid]["%s_perseasons_sum_mintds" %methodpath] = []
			db[pairid]["%s_perseasons_sum_minresids" %methodpath] = []
			db[pairid]["%s_perseasons_sum_minsigresids" %methodpath] = []
			db[pairid]["%s_perseasons_sum_minsigmags" %methodpath] = []


		# add new confidence estimation

		db[pairid]["%s_crude_conflevel" %methodpath] = conflevel # this one is stupid
		db[pairid]["%s_crude_nmin" %methodpath] = len(minparams)

		"""
		if len(minparams) > 0:
			db[pairid]["%s_crude_sigmabestmin" %methodpath] = sorted(minparams,key=lambda minparam: -1.0*minparam["scatter"])[0]["scatter"]
		else:
			db[pairid]["%s_crude_sigmabestmin" %methodpath] = 0
		"""


for methodpath in ["all-7"]:
	addcrudeopt(db,methodpath)
	
##############   pkl export    ##############

# We keep it as a dict of dicts, it's easier to "query" in this way:

pklfilepath = "db.pkl"
pycs.gen.util.writepickle(db, pklfilepath)
