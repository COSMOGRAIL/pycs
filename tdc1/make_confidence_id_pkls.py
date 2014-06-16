import pycs
import os,sys
import numpy as np

"""
Writes lists of estimate ids into pkl files, corresponding to combi confidence levels.
Only for pairs which are in TDC1 !
Not sure if we need this...

"""

execfile("config.py")
outputdir = './results_tdc1/combi_confidence_ids' # Where do you want the .pkl files grouping the estimates to be written...

iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
groupests = pycs.tdc.est.group(iniests)

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


"""

import matplotlib.pyplot as plt

# Now, plot these values

plt.figure('counts')
counts = [doubtless,plausible,doubtless_to_multimodal,multimodal,doubtless_to_uninformative,uninformative]
percents = [count/5180.0*100 for count in counts]
labels=[]
for count,name in zip(percents,selections):
	labels.append(name+': '+'%.0f' %count +'%')
 
y_pos = np.arange(len(labels))
plt.barh(y_pos, counts, align='center', alpha=0.4)
plt.yticks(y_pos, labels)
plt.xlabel('Number of pairs')



plt.show()
"""
