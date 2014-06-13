"""
We read in the database (from the pkl), and prepare a submission file.
"""

execfile("config.py")

import pycs
import os
import numpy as np


db = pycs.gen.util.readpickle("joined.pkl")


sel = []
for entry in db.values():
	
	isin = False
	
	#print entry["combiconf1"]
	if entry["combiconf1"] == 1:	
		isin = True
		
	if isin:
		est = pycs.tdc.est.Estimate(
			set = "tdc1",
			rung = entry["rung"],
			pair = entry["pair"],
			td = entry["d3cs_combi_td"],
			tderr = entry["d3cs_combi_tderr"]			
		)
		sel.append(est)

pycs.tdc.util.writesubmission(sel, "pycs_tdc1_test.dt", ["D3CS combid3cs1", "keeping only combiconf == 1"])





