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

infos = pycs.tdc.vario.vario([myest])
print infos["vratio"]
sys.exit()


pycs.tdc.est.show(myests)
