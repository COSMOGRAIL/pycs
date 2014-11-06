import pycs
import matplotlib.pyplot as plt
import sys,os
execfile('config_vivien.py')

pairs = pycs.tdc.util.listtdc1v2pairs()

# load pairs from d3cs:
	
iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)
iniests = pycs.tdc.est.select(iniests, pairs= pairs)



myests = pycs.tdc.est.select(iniests, rungs=[0], pairs=[497])

myest = myests[0]

filepath = pycs.tdc.util.tdcfilepath(myest.set,myest.rung,myest.pair)
mylc = pycs.tdc.util.read(filepath)
print len(mylc)

infos = pycs.tdc.vario.vario(mylc[0])
print infos["vratio"]
sys.exit()


pycs.tdc.est.show(myests)
