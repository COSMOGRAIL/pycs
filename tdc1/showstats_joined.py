import pycs
import numpy as np
import matplotlib.pyplot as plt

dbasdict = pycs.gen.util.readpickle("joined.pkl")

db = dbasdict.values() # Just transforming this as lits

db = [e for e in db if e["in_tdc1"]]

print "#"*40

for i in [1,2,3,4]:
	n = len([e for e in db if e["confidence"] == i])
	print "Confidence %i: %i entries." % (i, n)


print "#"*40

db12 = [e for e in db if e["confidence"] in [1, 2]]

relerrs = np.array([e["d3cs_combi_reltderr"] for e in db12])

plt.hist(relerrs, bins=np.logspace(-2, 3.0, 100), log=True)
plt.xlabel("Relative D3CS time delay error estimates")
plt.gca().set_xscale("log")
plt.show()


