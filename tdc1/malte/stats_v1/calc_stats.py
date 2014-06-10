import sys, os
import pycs
import numpy as np



datadir = "/vol/fohlen11/fohlen11_1/mtewes/TDC/New_TDC1_13Dec2013_zip"

outdir = "/vol/fohlen11/fohlen11_1/mtewes/TDC/New_TDC1_13Dec2013_stats"

db = []

for rung in range(5):
	for pair in range(1,1036+1):

		inpath = os.path.join(datadir, pycs.tdc.util.tdcfilepath("tdc1", rung, pair, skipset=True))
		#print inpath
		
		lcs = pycs.tdc.util.read(inpath, mag="asinh")
		for l in lcs:
			l.validate()
		lcs[0].object = "A"
		lcs[1].object = "B"	
		
		line = {"rung":rung, "pair":pair}
		
		samplingstats = lcs[0].samplingstats() # Is the same for A and B !
		line["nseas"] = samplingstats["nseas"]
		
		line["meansampling"] = samplingstats["mean"]
		line["medsampling"] = samplingstats["med"]
		line["stdsampling"] = samplingstats["std"]
		
		line["meansg"] = samplingstats["meansg"]
		line["stdsg"] = samplingstats["stdsg"]
		
		vario0 = pycs.tdc.vario.vario(lcs[0], nsamp=1000000)
		vario1 = pycs.tdc.vario.vario(lcs[1], nsamp=1000000)
		
		line["vratioA"] = vario0["vratio"]
		line["vratioB"] = vario1["vratio"]
		line["seasonlength"] = vario0["seasonlength"]
		
		line["len"] = len(lcs[0])
		
		magsA = lcs[0].getmags()
		magsB = lcs[1].getmags()
		
		line["meanmagA"] = np.mean(magsA)
		line["meanmagB"] = np.mean(magsB)
		
		line["magrangeA"] = np.max(magsA) - np.min(magsA)
		line["magrangeB"] = np.max(magsB) - np.min(magsB)
		
		magerrsA = lcs[0].getmagerrs()
		magerrsB = lcs[1].getmagerrs()
		
		line["meanmagerrA"] = np.mean(magerrsA)
		line["meanmagerrB"] = np.mean(magerrsB)
		
		
		outfile = os.path.join(outdir, "%i_%i.pkl" % (rung, pair))
		
		print line
		
		pycs.gen.util.writepickle(line, outfile)
		
		
		#db.append(line)
		#exit()
		
		
