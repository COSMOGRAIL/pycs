import pycs
import matplotlib.pyplot as plt
import sys,os
execfile('config.py')

"""
Explore categories of estimates from combiconf2, in order to cast "GOD" judgements.
"""


# load pairs from d3cs:

d3csests = pycs.tdc.est.importfromd3cs(d3cslogpath)
#d3csests = pycs.tdc.est.select(pycs.tdc.est.importfromd3cs(d3cslogpath), pairs=pycs.tdc.util.listtdc1v2pairs())


# Load the combination estimates, with "long" confidence levels (like "42")
combiests_bg = pycs.gen.util.readpickle("./results_tdc1/combi_confidence_ids/combiests_bg.pkl")
pycs.tdc.est.checkunique(combiests_bg)
print "Read %i combiest_bg" % (len(combiests_bg))

combiests_bg_select = [est for est in combiests_bg if est.confidence == 40]

selectd3csests = pycs.tdc.est.select(d3csests, idlist = [est.id for est in combiests_bg_select])

pycs.tdc.est.interactivebigplot(selectd3csests, shadedestimates = combiests_bg_select, interactive=True, groupests = True)

