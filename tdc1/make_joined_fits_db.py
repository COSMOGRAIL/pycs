"""
We combine info from:
	- D3CS results
	- "xtrastats"
	- PyCS results
	- stats resulting from the time delays (e.g., overlap)
into a single big pkl & FITS table


"""

execfile("config.py")

import pycs
import os
import numpy as np
import pyfits
import glob


##############	Initialization ##############

db = {} # we'll use a dictionnary for building the big unique db, easier to index, and convert it to a list later.

# We initialize the db with empty dicts.
for rung in range(5):
	#for pair in pycs.tdc.util.listtdc1v2pairs():
	for pair in range(1, 1037):
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid] = {"rung":rung, "pair":pair, "in_tdc1":0} # By default, a pair is not in tdc1.
		

##############   Some pairs where rejected, we mark this with a flag  ##############

for rung in range(5):
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid]["in_tdc1"] = 1


##############   D3CS + combiconf1, the old stuff   ##############


d3csests = pycs.tdc.est.importfromd3cs(d3cslogpath)

groupedd3csests = pycs.tdc.est.group(d3csests)
for group in groupedd3csests:
	db[group[0].id]["d3cs_n"] = len(group) # Number of D3CS estimates
	db[group[0].id]["d3cs_stdtd"] = np.std(np.array([est.td for est in group])) # plain std dev of D3CS estimates

	# We also get the combiconf
	db[group[0].id]["old_d3cs_combiconf1"] = pycs.tdc.combiconf.combiconf1(group)["code"]


combid3csests = pycs.tdc.est.multicombine(d3csests, method='d3cscombi1')

for est in combid3csests:
		
	db[est.id]["old_d3cs_combi_td"] = est.td
	db[est.id]["old_d3cs_combi_tderr"] = est.tderr	
	db[est.id]["old_d3cs_combi_abstd"] = abs(est.td)
	if est.td != 0.0:
		db[est.id]["old_d3cs_combi_reltderr"] = est.tderr / abs(est.td)
	else:
		db[est.id]["old_d3cs_combi_reltderr"] = 999.0


##############   Final D3CS confidence + estimate (based on combiconf2 and GOD stuff)   ##############


ag = pycs.gen.util.readpickle("results_tdc1/combi_confidence_ids/combiests_ag.pkl")

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

print "Done with overlap..."
##############   PyCS    ##############


# This part is kind of custom and preliminary for now...


def addpycs(db, estimates, methodname="none"):
	"""
	Adds the PyCS estimates into the db, and computes some related useful quantities.
	"""
	
	cleanestimates =  [e for e in estimates if e != None]
	pycs.tdc.est.checkunique(cleanestimates)
	
	for est in cleanestimates:
			
		# Normal fields
		db[est.id]["pycs_%s_td" % (methodname)] = est.td
		db[est.id]["pycs_%s_tderr" % (methodname)] = est.tderr
		db[est.id]["pycs_%s_ms" % (methodname)] = est.ms
		db[est.id]["pycs_%s_timetaken" % (methodname)] = est.timetaken
		db[est.id]["pycs_%s_confidence" % (methodname)] = est.confidence
	
		# Pirat fields, if available
		if hasattr(est, "tdvarint"):
			db[est.id]["pycs_%s_tdvarint" % (methodname)] = est.tdvarint
		if hasattr(est, "tdranerr"):
			db[est.id]["pycs_%s_tdranerr" % (methodname)] = est.tdranerr
		if hasattr(est, "tdsyserr"):
			db[est.id]["pycs_%s_tdsyserr" % (methodname)] = est.tdsyserr
	
		
		# The absolute delay, and the relative error:	
		db[est.id]["pycs_%s_abstd" % (methodname)] = abs(est.td)
		if est.td != 0.0:
			db[est.id]["pycs_%s_reltderr" % (methodname)] = est.tderr / abs(est.td)
		else:
			db[est.id]["pycs_%s_reltderr" % (methodname)] = 999.0
		
		# The separation between PyCS and D3CS delays:
		db[est.id]["pycs_%s_d3cs_tdsep" % (methodname)] = abs(est.td - db[est.id]["d3cs_combi_td"])
		
		# Same separation, expressed in terms of "sigma"
		if est.tderr != 0.0:
			db[est.id]["pycs_%s_d3cs_tdsep_in_pycs_errs" % (methodname)] = abs(est.td - db[est.id]["d3cs_combi_td"]) / est.tderr
		else:
			db[est.id]["pycs_%s_d3cs_tdsep_in_pycs_errs" % (methodname)] = 999.0
		if db[est.id]["d3cs_combi_tderr"] != 0.0:
			db[est.id]["pycs_%s_d3cs_tdsep_in_d3cs_errs" % (methodname)] = abs(est.td - db[est.id]["d3cs_combi_td"]) / db[est.id]["d3cs_combi_tderr"]
		else:
			db[est.id]["pycs_%s_d3cs_tdsep_in_d3cs_errs" % (methodname)] = 999.0
		
		# Ratio between pycs error and d3cs error
		db[est.id]["pycs_%s_to_d3cs_tderr_ratio" % (methodname)] = est.tderr / db[est.id]["d3cs_combi_tderr"]



# We explicitly include the key runs

sdi1 = pycs.gen.util.readpickle("results_tdc1/sdi-dou-c20-s100-m8-rall.pkl")\
		+ pycs.gen.util.readpickle("results_tdc1/sdi-pla-c20-s100-m8-rall.pkl")\
		+ pycs.gen.util.readpickle("results_tdc1/sdi-mul-c20-s100-m8-rall.pkl")
addpycs(db, sdi1, methodname="sdi1")


spl2 = pycs.gen.util.readpickle("results_tdc1/spl-dou-c20-s100-m8-rall.pkl") + pycs.gen.util.readpickle("results_tdc1/spl-pla-c20-s100-m8-rall.pkl")
addpycs(db, spl2, methodname="spl2")


spl3_Bonn = pycs.gen.util.readpickle("results_tdc1/spl3-dou-run1-Bonn.pkl") + pycs.gen.util.readpickle("results_tdc1/spl3-pla-run1-Bonn.pkl")
addpycs(db, spl3_Bonn, methodname="spl3_Bonn")


# Add your own...


# And we also include those in auto_include_in_db, for quick tests...

pycsresultspkls = sorted(glob.glob("results_tdc1/auto_include_in_db/*.pkl"))

for pkl in pycsresultspkls:
	print "Autoincluding", pkl
	estimates = pycs.gen.util.readpickle(pkl) 
	methodname = os.path.splitext(os.path.basename(pkl))[0]
	addpycs(db, estimates, methodname=methodname)




print "Done with PyCS..."
##############   pkl export    ##############

# We keep it as a dict of dicts, it's easier to "query" in this way:

pklfilepath = "joined.pkl"
pycs.gen.util.writepickle(db, pklfilepath)


##############   FITS export    ##############



# Now we convert this dict to a list. Important as we will rely on the ordering to form the colums !

db = db.values() # list of dicts -- we throw away the keys.

# Get a flat list of all the available entry keys, to be used as columns.
allkeys = []
for e in db:
	allkeys.extend(e.keys())
allkeys = sorted(list(set(allkeys)))

# we move a few items in first position
putfirst = ["in_tdc1", "rung", "pair", "confidence"]
for e in putfirst:
	allkeys.remove(e)
	allkeys.insert(0, e)

print "Columns: "
print allkeys

cols = [pyfits.Column(name=key, format="D", array=np.array([item.get(key) for item in db])) for key in allkeys]
# "get" returns None by default, if the key is not found. Seems fine for what we want to do.
	
coldefs = pyfits.ColDefs(cols)
tbhdu = pyfits.new_table(coldefs)

fitsfilepath = "joined.fits"

tbhdu.writeto(fitsfilepath, clobber=True)
print "Wrote %s" % (fitsfilepath)




