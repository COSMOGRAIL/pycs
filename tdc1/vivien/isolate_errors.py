import pycs
import matplotlib.pyplot as plt
import sys,os
execfile('config_vivien.py')

# read the not working ids

f = open('err.txt','r')
line = f.readlines()[0]
elts = line.split('on ')
newelts = []
for elt in elts:
	newelt = elt.split('error')[0]
	newelts.append(newelt)
ids = newelts[1:]	


# load them from d3cs:
'''	
iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
combiests = pycs.tdc.est.multicombine(iniests,method='d3cscombi1')
groupedests = pycs.tdc.est.group(iniests, verbose=True)
for groupedest,combiest in zip(groupedests,combiests):
	combiout = pycs.tdc.combiconf.combiconf1(groupedest)	
	combiest.confidence = combiout["code"]
pycs.gen.util.writepickle(combiests,'combiids.pkl')
'''	
combiests = pycs.gen.util.readpickle('combiids.pkl')
print len(combiests)
print len([est for est in combiests if est.confidence==1])
badests = pycs.tdc.est.select(combiests,idlist=ids)
badconf = [est.confidence for est in badests]

selection = pycs.gen.util.readpickle(os.path.join(groupedestimatespath,'1.pkl'))

print len(selection)
sys.exit()
plt.hist(badconf)
plt.show()
