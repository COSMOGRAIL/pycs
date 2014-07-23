import pycs
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

db = pycs.gen.util.readpickle("../db.pkl").values()
db = [item for item in db if item["in_tdc1"] == 1]
db = [item for item in db if abs(item["truetd"]) > 10.0]


fig = plt.figure(figsize=(10, 6))
fig.subplots_adjust(bottom=0.12, top=0.95, left=0.1, right=0.95)

#subnames = ["pycs_tdc1_d3cs-vanilla-dou-full", "pycs_tdc1_spl-vanilla-dou-full", "pycs_tdc1_sdi-vanilla-dou-full",
#	"pycs_tdc1_d3cs-vanilla-dou-100bestP", "pycs_tdc1_spl-vanilla-dou-100bestP", "pycs_tdc1_sdi-vanilla-dou-100bestP"]

subnames = ["pycs_tdc1_spl-vanilla-dou-full",
	"pycs_tdc1_spl-vanilla-dou-800bestP",
	"pycs_tdc1_spl-vanilla-dou-100bestP",
	"pycs_tdc1_spl-vanilla-doupla-full",
	"pycs_tdc1_spl-vanilla-doupla-1600bestP",
	"pycs_tdc1_spl-vanilla-doupla-800bestP"
]


r = 0.05 # radius over which you want me to evaluate the posteriors.
#r = 0.2
# Choose it large enough so that the combined posteriors fit within it !
samples = 1000 # Number of evaluations
x = np.linspace(-r, r, samples)

lensmodelsigma = 0.1 # 0.1 means a 10% error on time delay distance 

for subi, subname in enumerate(subnames):

	seldb = [item for item in db if subname + "_td" in item] # We keep only the entries that have this submission
	print subname, len(seldb)

	truetds = np.array([item["truetd"] for item in seldb])
	subtds = np.array([item[subname + "_td"] for item in seldb])
	subtderrs = np.array([item[subname + "_tderr"] for item in seldb])

	subtdoffs = subtds - truetds
	centers = subtdoffs/truetds
	sigmas = subtderrs/np.fabs(truetds)
	
	sigmas = np.sqrt(sigmas**2 + lensmodelsigma**2)

	ytot = np.zeros(samples) # the log-posterior.
	N = len(seldb)
	#N=5
	for i in range(N):
	
		#y = norm.pdf(x, centers[i], sigmas[i])
		# No, we need to do this in log scale: 
		y =  - ((x - centers[i])**2)/(2.0*sigmas[i]**2)# - np.log(sigmas[i]*np.sqrt(2.0*np.pi)) # No need for the "normalization" here.
		ytot += y
	
	ytot -= np.max(ytot) # a shift so that the max is 0.0, to avoid the explosion of exp.
	
	# We get back to pdf:
	pdf = np.exp(ytot)
	
	# And we normalize the pdf (for this to be fair, make sure that r is large enough)
	pdf = pdf / (np.sum(pdf)*(x[1] - x[0])) 
	
	plt.plot(x, pdf, label=subname)
	
	# Try to reproduce this by direct computation:
	
	(center_combi, sigma_combi) = pycs.tdc.metrics.combigauss(subtds, subtderrs, truetds, lensmodelsigma)
	# That's what it does:
	#sigma_combi = 1.0 / np.sqrt(np.sum(1.0 / (sigmas**2)))
	#center_combi = sigma_combi**2 * np.sum( centers/sigmas**2 )
	
	plt.plot(x, norm.pdf(x, center_combi, sigma_combi), ls="--", color="black")
	
	

ax = plt.gca()
plt.axvline(0.0, ls="--", color="gray")
plt.text(0.1, 0.9, r"$\sigma_{\mathrm{lens \, model}} = %.2f$" % (lensmodelsigma), transform=ax.transAxes, fontsize=20)
plt.xlabel(r"Fractional error on time delay distance", fontsize=20)
plt.ylabel("PDF", fontsize=20)

#ax.set_yscale('log', nonposy='clip')
plt.xlim(-r, r)
plt.ylim(0, 350)
plt.legend()
plt.show()
#plt.savefig("0.pdf")

