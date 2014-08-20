import pycs
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm



db = pycs.gen.util.readpickle("../db.pkl").values()
db = [item for item in db if item["in_tdc1"] == 1] # No need for the other ones

alltruetds = np.array([item["truetd"] for item in db])

subdb = [item for item in db if abs(item["truetd"]) > 10.0]

truetds = np.array([item["truetd"] for item in subdb])

#print len(truetds), len(alltruetds)

submission = "pycs_tdc1_spl-vanilla-doupla-full"
#submission = "pycs_tdc1_d3cs-vanilla-dou-full"
#submission = "pycs_tdc1_sdi-vanilla-doupla-full"

print submission

seldb = [item for item in db if submission + "_td" in item]

print "f_all = ", float(len(seldb))/len(db)

seldb = [item for item in subdb if submission + "_td" in item]

print "f_above10 = ", float(len(seldb))/len(subdb)

print "Number of systems above 10", float(len(seldb))

# Now we sort this according to error

for item in seldb:
	item["error"] = abs(item[submission + "_td"] - item["truetd"])
	item["errorinsigma"] = item["error"]/item[submission + "_tderr"]


print "Worst, by absolute error:"
sortedseldb = sorted(seldb, key=lambda k: k['error'], reverse=True) 
for item in sortedseldb[:30]:
	print "%15s, %8.2f, %8.2f, %8.2f" % (item["id"], item["truetd"], item["errorinsigma"], item["error"])

print "Worst, by absolute error in sigma:"
sortedseldb = sorted(seldb, key=lambda k: k['errorinsigma'], reverse=True) 
for item in sortedseldb[:30]:
	print "%15s, %8.2f, %8.2f, %8.2f" % (item["id"], item["truetd"], item["errorinsigma"], item["error"])



exit()


#db = [item for item in db if item["rung"] == 0]

colors = ["red", "blue", "green"]

fig = plt.figure(figsize=(10, 10))
fig.subplots_adjust(bottom=0.15, top=0.95, left=0.15, right=0.95)

#"pycs_tdc1_d3cs-vanilla-dou-full"
subnames = ["pycs_tdc1_spl-vanilla-dou-full"]#, "pycs_tdc1_sdi-vanilla-dou-full"]
#subnames = ["pycs_tdc1_spl-vanilla-doupla-full", "pycs_tdc1_spl-median-doupla-splagree"]


for subi, subname in enumerate(subnames):

	seldb = [item for item in db if subname + "_td" in item] # We keep only the entries that have this submission
	print subname, len(seldb), len(seldb)/1024.0

	truetds = np.array([item["truetd"] for item in seldb])
	abstruetds = np.fabs(truetds)
	subtds = np.array([item[subname + "_td"] for item in seldb])
	subtderrs = np.array([item[subname + "_tderr"] for item in seldb])
	
	plt.errorbar(truetds, subtds - truetds, subtderrs, linestyle="none", color = colors[subi], label="%s (%i points)" % (subname, len(seldb)))
	
	#sel = np.fabs((truetds - subtds) / truetds) > 0.1
	#plt.errorbar(truetds[sel], (subtds - truetds)[sel], subtderrs[sel], linestyle="none", color = "black", label="%s (%i points)" % (subname, len(seldb)))
	
	

#exit()
#x = np.linspace(-range, range, 1000)
#plt.plot(x, norm.pdf(x, 0.0, 1.0), color="black", label="Standard normal distribution")

#plt.title("All rungs")
plt.xlabel(r"$\Delta t_i$", fontsize=26)
#plt.ylabel(r"$\frac{\widetilde{\Delta t_i} - \Delta t_i}{\sigma_i}$", fontsize=26)
plt.ylabel(r"$\widetilde{\Delta t_i} - \Delta t_i$", fontsize=26)


#plt.xlim(-range, range)
#plt.ylim(-4, 4)
plt.legend()
plt.show()
#plt.savefig("test.pdf")

