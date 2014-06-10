import sys, os, glob
import pycs
import numpy as np


outdir = "/vol/fohlen11/fohlen11_1/mtewes/TDC/New_TDC1_13Dec2013_stats"

db = []


pklpaths = glob.glob(os.path.join(outdir, "*_*.pkl"))

for pklpath in pklpaths:
	line = pycs.gen.util.readpickle(pklpath)
	db.append(line)
	
pycs.gen.util.writepickle(db, "/vol/fohlen11/fohlen11_1/mtewes/TDC/New_TDC1_13Dec2013_stats.pkl")
		
