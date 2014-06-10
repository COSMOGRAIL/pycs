"""
We combine info from:
	- D3CS results
	- PyCS results
	- "xtrastats"
	- stats resulting from the time delays (e.g., overlap)
into a single big pkl & FITS table


"""

execfile("config.py")

import pycs
import os
import numpy as np
import pyfits


db = {} # we'll use a dictionnary for building the big unique db, easier to index, and convert it to a list later.

# We initialize the db with empty dicts.
for rung in range(5):
	#for pair in pycs.tdc.util.listtdc1v2pairs():
	for pair in range(1, 1037):
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
		db[pairid] = {}
		



##############   D3CS    ##############


d3csests = pycs.tdc.est.importfromd3cs(d3cslogpath)

groupedd3csests = pycs.tdc.est.group(d3csests)
for group in groupedd3csests:
	db[group[0].id]["d3cs_n"] = len(group) # Number of D3CS estimates


combid3csests = pycs.tdc.est.multicombine(d3csests, method='d3cscombi1')

for est in combid3csests:
		
	db[est.id]["d3cs_td"] = est.td
	db[est.id]["d3cs_tderr"] = est.tderr
	db[est.id]["d3cs_ms"] = est.ms
	db[est.id]["d3cs_timetaken"] = est.timetaken
	
	
		
print "Done with D3CS..."
##############   xtrastats    ##############


for rung in range(5):
	for pair in pycs.tdc.util.listtdc1v2pairs():
		pairid = "%s_%i_%i" % ("tdc1", rung, pair)
	
		relfilepath = pycs.tdc.util.tdcfilepath(set="tdc1", rung=rung, pair=pair, skipset=False)
		pklpath = os.path.join(xtrastatsdir, relfilepath+".stats.pkl")
		if os.path.exists(pklpath):
			
			data = pycs.gen.util.readpickle(pklpath)
			db[pairid].update(data) # We add this dict content to the existing dict.



print "Done with xtrastats..."
##############   PyCS    ##############




##############   overlap etc    ##############




##############   FITS export    ##############



# Now we convert this dict to a list. Important as we will rely on the ordering !

db = db.values() # A plain list of dicts, as usual.

# Get a flat list of all the available keys, to be used as columns.
allkeys = []
for e in db:
	allkeys.extend(e.keys())
allkeys = sorted(list(set(allkeys)))

print "Columns: "
print allkeys

cols = [pyfits.Column(name=key, format="D", array=np.array([item.get(key) for item in db])) for key in allkeys]
	
coldefs = pyfits.ColDefs(cols)
tbhdu = pyfits.new_table(coldefs)

fitsfilepath = "test.fits"

tbhdu.writeto(fitsfilepath, clobber=True)
print "Wrote %s" % (fitsfilepath)


"""
d3csests = pycs.tdc.est.importfromd3cs("/Users/mtewes/Desktop/TDC/d3cs_logs/2014-06-06_danka_removed.txt")

datadir = "/Users/mtewes/Desktop/TDC/pycs_svn_tdc1/results_tdc1"
dousel = pycs.gen.util.readpickle(os.path.join(datadir, 'groupedestimates/doubtlesses.pkl'))

douests = pycs.tdc.est.select(d3csests,idlist=dousel)


combidouests = pycs.tdc.est.multicombine(douests, method='d3cscombi1')

pycs.gen.util.writepickle(combidouests, "combidouests.pkl")

combidouests = pycs.gen.util.readpickle("combidouests.pkl")
"""

