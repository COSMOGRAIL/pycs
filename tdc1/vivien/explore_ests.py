import pycs
import matplotlib.pyplot as plt
import sys,os
execfile('config_vivien.py')

"""
Explore various categories of estimates from combiconf2
"""


pairs = pycs.tdc.util.listtdc1v2pairs()

# load pairs from d3cs:
	
iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
iniests = pycs.tdc.est.select(iniests, pairs= pairs)

'''
combiests = pycs.tdc.est.multicombine(iniests,method='d3cscombi1')
groupedests = pycs.tdc.est.group(iniests, verbose=True)
for groupedest,combiest in zip(groupedests,combiests):
	combiout = pycs.tdc.combiconf.combiconf2(groupedest)	
	combiest.confidence = combiout["code"]
pycs.gen.util.writepickle(combiests,'combiids.pkl')
'''

combiests = pycs.gen.util.readpickle('combiids.pkl')
combiests = [est for est in combiests if est.confidence == 56]
combiestids = [est.id for est in combiests]
selectests = pycs.tdc.est.select(iniests,idlist = combiestids)

pycs.tdc.est.interactivebigplot(selectests, shadedestimates = combiests, interactive=True, groupests = True)
sys.exit()

