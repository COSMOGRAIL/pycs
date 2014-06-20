import pycs
import os,sys
import numpy as np
import matplotlib.pyplot as plt

execfile("config.py")

godests = pycs.tdc.est.importfromd3cs("d3cs_logs/2014-06-20_god_only.txt")
print "Imported %i god ests" % (len(godests))
pycs.tdc.est.checkunique(godests)

combiests = pycs.gen.util.readpickle(os.path.join("results_tdc1/combi_confidence_ids/combiests_bg.pkl"))
print "Imported %i combi ests" % (len(combiests))
pycs.tdc.est.checkunique(combiests)

godestids = [e.id for e in godests]

for combiest in combiests:

	combiest.code = combiest.confidence
	
	# Is there a GOD estimate ?
	try:
		godindex = godestids.index(combiest.id)
		
		print "I found a god est!"
		print godests[godindex]
		
		combiest.td = godests[godindex].td
		combiest.tderr = godests[godindex].tderr
		combiest.ms = godests[godindex].ms
		combiest.confidence = godests[godindex].confidence
		combiest.methodpar = godests[godindex].methodpar
		combiest.method = godests[godindex].methodpar
		
	except:
		
		print "No god estimate"
		
		if combiest.code in [10, 11, 12, 14]:
			combiest.confidence = 1
		if combiest.code in [13, 20, 21, 23, 24, 30, 31, 33, 50, 51]:
			combiest.confidence = 2
		if combiest.code in [40, 41, 43, 44]:
			combiest.confidence = 3
		if combiest.code in [54, 55, 56, 57, 60]:
			combiest.confidence = 4
	
		if combiest.confidence > 4 or combiest.confidence < 1:
			raise RuntimeError("Should not happen.")
		
	if combiest.confidence > 4 or combiest.confidence < 1:
			raise RuntimeError("Should also not happen.")
		

pycs.gen.util.writepickle(combiests, "results_tdc1/combi_confidence_ids/combiests_ag.pkl")

	
		
	
	
	

