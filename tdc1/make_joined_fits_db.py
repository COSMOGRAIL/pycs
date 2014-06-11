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


##############   D3CS + combiconf   ##############


d3csests = pycs.tdc.est.importfromd3cs(d3cslogpath)

groupedd3csests = pycs.tdc.est.group(d3csests)
for group in groupedd3csests:
	db[group[0].id]["d3cs_n"] = len(group) # Number of D3CS estimates
	db[group[0].id]["d3cs_stdtd"] = np.std(np.array([est.td for est in group])) # plain std dev of D3CS estimates

	# We also get the combiconf
	db[group[0].id]["combiconf1"] = pycs.tdc.combiconf.combiconf1(group)["code"]


combid3csests = pycs.tdc.est.multicombine(d3csests, method='d3cscombi1')

for est in combid3csests:
		
	db[est.id]["d3cs_combitd"] = est.td
	db[est.id]["d3cs_combitderr"] = est.tderr
	db[est.id]["d3cs_combims"] = est.ms
	db[est.id]["d3cs_combitimetaken"] = est.timetaken
	db[est.id]["d3cs_oldcombiconfidence"] = est.confidence
	
	
print "Done with D3CS..."
##############   xtrastats    ##############


for rung in range(5):
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
	
		relfilepath = pycs.tdc.util.tdcfilepath(set="tdc1", rung=rung, pair=pair, skipset=False)
		pklpath = os.path.join(xtrastatsdir, relfilepath+".stats.pkl")
		if os.path.exists(pklpath):
			
			data = pycs.gen.util.readpickle(pklpath, verbose=False)
			
			db[pairid].update(data) # We add this dict content to the existing dict.


print "Done with xtrastats..."

##############   Overlap etc    ##############

# We compute a few more stats, making use of the D3CS time delays.







##############   PyCS    ##############


# This part is very custom and preliminary for now...

splpkls = ["spl-dou-c20-s100-m8-uni-r0.pkl",
"spl-dou-c20-s100-m8-uni-r1.pkl",
"spl-dou-c20-s100-m8-uni-r2.pkl",
"spl-dou-c20-s100-m8-uni-r3.pkl",
"spl-dou-c20-s100-m8-uni-r4.pkl",
"spl-pla-c20-s100-m8-uni-r0.pkl",
"spl-pla-c20-s100-m8-uni-r1.pkl",
"spl-pla-c20-s100-m8-uni-r2.pkl",
"spl-pla-c20-s100-m8-uni-r3.pkl",
"spl-pla-c20-s100-m8-uni-r4.pkl"]

for pkl in splpkls:
	estimates = pycs.gen.util.readpickle(os.path.join(pycsresdir, pkl))
	for est in estimates:
		db[est.id].update({"pycs_spl_td":est.td, "pycs_spl_tderr":est.tderr, "pycs_spl_ms":est.ms, "pycs_spl_timetaken":est.timetaken, "pycs_spl_timetaken":est.timetaken})


sdipkls = ["sdi-dou-c20-s100-m8-uni-r0.pkl",
"sdi-dou-c20-s100-m8-uni-r1.pkl",
"sdi-dou-c20-s100-m8-uni-r2.pkl",
"sdi-dou-c20-s100-m8-uni-r3.pkl",
"sdi-dou-c20-s100-m8-uni-r4.pkl",
"sdi-pla-c20-s100-m8-uni-r0.pkl",
"sdi-pla-c20-s100-m8-uni-r1.pkl",
"sdi-pla-c20-s100-m8-uni-r2.pkl",
"sdi-pla-c20-s100-m8-uni-r3.pkl",
"sdi-pla-c20-s100-m8-uni-r4.pkl"]

for pkl in sdipkls:
	estimates = pycs.gen.util.readpickle(os.path.join(pycsresdir, pkl))
	for est in estimates:
		db[est.id].update({"pycs_sdi_td":est.td, "pycs_sdi_tderr":est.tderr, "pycs_sdi_ms":est.ms, "pycs_sdi_timetaken":est.timetaken, "pycs_sdi_timetaken":est.timetaken})




print "Done with reading PyCS results..."


##############   pkl export    ##############

# We keep it as a dict of dicts, it's easier to "query" in this way:

pklfilepath = "test.pkl"
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
putfirst = ["in_tdc1", "rung", "pair", "combiconf1"]
for e in putfirst:
	allkeys.remove(e)
	allkeys.insert(0, e)

print "Columns: "
print allkeys

cols = [pyfits.Column(name=key, format="D", array=np.array([item.get(key) for item in db])) for key in allkeys]
# "get" returns None by default, if the key is not found. Seems fine for what we want to do.
	
coldefs = pyfits.ColDefs(cols)
tbhdu = pyfits.new_table(coldefs)

fitsfilepath = "test.fits"

tbhdu.writeto(fitsfilepath, clobber=True)
print "Wrote %s" % (fitsfilepath)




