import pycs
import matplotlib.pyplot as plt
import sys,os
execfile('config_vivien.py')

"""
Script to identify which pairs are problematic, and plot some basic properties (td, tderr,...)
Now solved with combiconf2...?
"""



# read the not working ids

f = open('err.txt','r')
line = f.readlines()[0]
elts = line.split('on ')
newelts = []
for elt in elts:
	newelt = elt.split('error')[0]
	newelts.append(newelt)
ids = newelts[1:]	

pairs = pycs.tdc.util.listtdc1v2pairs()


# load them from d3cs:
	
iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
iniests = pycs.tdc.est.select(iniests, pairs= pairs)
'''
combiests = pycs.tdc.est.multicombine(iniests,method='d3cscombi1')
groupedests = pycs.tdc.est.group(iniests, verbose=True)


for groupedest,combiest in zip(groupedests,combiests):
	combiout = pycs.tdc.combiconf.combiconf1(groupedest)	
	combiest.confidence = combiout["code"]
pycs.gen.util.writepickle(combiests,'combiids.pkl')
'''
	
combiests = pycs.gen.util.readpickle('combiids.pkl')
badests = pycs.tdc.est.select(combiests,idlist=ids)
badconf = [est.confidence for est in badests]


pycs.tdc.est.interactivebigplot(badests,shadedestimates=iniests,interactive=False)
	


