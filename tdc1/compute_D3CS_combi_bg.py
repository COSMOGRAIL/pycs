import pycs
import os,sys
import numpy as np
import matplotlib.pyplot as plt
"""
Writes lists of estimate ids into pkl files, corresponding to combi confidence levels.
Only for pairs which are in TDC1 !
"""
execfile("sampleconfig.py")

outputdir = './results_tdc1/combi_confidence_ids'		# Where .pkls will be stored

if 1:
	print 'You are going to compute the confidence level with combiconf2 and reroll on some estimates'
	pycs.tdc.util.goingon()
	
	# load the estimates from d3cs database (before the hand of god)
	tdc1pairs = pycs.tdc.util.listtdc1v2pairs()
	iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
	iniests = pycs.tdc.est.select(iniests, pairs=tdc1pairs)

	# group the estimates, and compute the combination with d3cscombi1 (do it only once
	
	groupests = pycs.tdc.est.group(iniests)
	combiests = pycs.tdc.est.multicombine(iniests,method='d3cscombi1')
	pycs.gen.util.writepickle((groupests,combiests),os.path.join(outputdir,'tempests.pkl'))
	
	(groupests,combiests) = pycs.gen.util.readpickle(os.path.join(outputdir,'tempests.pkl'))

	# compute the confidence level
	# code that need a reroll: 22, 32 42, 52, 54
	newests = []
	for combiest,groupest in zip(combiests,groupests):

		code = pycs.tdc.combiconf.combiconf2(groupest)["code"]
		combiest.confidence = code

		if code in [22, 32, 42, 52, 54]:
			# if a reroll is needed, we recompute the combination and the code with only Malte+Vivien estimates
			print 'I reroll on %s' % combiest.id
			print 'Previous code was %f' % combiest.confidence
			outreroll = pycs.tdc.combiconf.reroll(groupest)
			combiest = pycs.tdc.est.combine(outreroll["ests"],method='d3cscombi1')
			combiest.confidence = outreroll["code"]
			print 'New code is %i' % combiest.confidence
			print '='*80

		newests.append(combiest)
		
	#Write these combi estimates in a pkl, to explore them with another script (explore_ests.py)
	pycs.gen.util.writepickle(newests,os.path.join(outputdir,'combiests_bg.pkl'))

	confid = [est.confidence for est in newests]
	plt.hist(confid,bins=100)
	plt.grid(True)
	plt.show()
	
	sys.exit()








'''
# go through the new d3cs database (after the hand of god),
# and replace combiests_bg with god values if they exist

combiests = pycs.gen.util.readpickle(os.path.join(outputdir,'combiests_bg.pkl'))
godests = pycs.tdc.est.importfromd3cs(d3cslogpath_with_god)
godests = [est for est in godests if est.methodpar=="god"]
'''

	
	



'''
# If you really need words, use these... but we don't, I guess.
categories = ["none", 'doubtless','plausible','doubtless_to_multimodal','multimodal','doubtless_to_uninformative','uninformative']
cats = ["none", 'dou','pla','dtm','mul','dtu','uni']

ids = [[] for i in range(len(cats))] # We will store the ids in here.

tdc1pairs = pycs.tdc.util.listtdc1v2pairs()

for groupest in groupests:

	code = pycs.tdc.combiconf.combiconf1(groupest)["code"]
	pairid = groupest[0].id
	
	if groupest[0].pair in tdc1pairs:
		ids[code].append(pairid)
	

for i in range(1, len(cats)):
	
	print "Code %i:" % (i)
	print len(ids[i])
	
	pycs.gen.util.writepickle(ids[i], os.path.join(outputdir,'%i.pkl' % (i)))
'''


