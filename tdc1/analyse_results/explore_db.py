import numpy as np
import os,sys
import matplotlib.pyplot as plt
import pycs



# load database...

db = pycs.gen.util.readpickle('db.pkl').values()
db = [item for item in db if item["in_tdc1"] == 1]


"""
### Check the distribution of individuals chi2,P,... ###

method = "pycs_tdc1_spl-vanilla-doupla-800bestP"
dbmeth = [item for item in db if "%s_td" % method in item]
chi2s = [item["%s_chi2" % method] for item in dbmeth]
As = [item["%s_A" % method] for item in dbmeth]
Ps = [item["%s_P" % method] for item in dbmeth]


for item in dbmeth:
	if item["id"] in ['tdc1_4_273','tdc1_4_598','tdc1_4_296','tdc1_4_647'] :
		print 'HUEHUEHUE'
		sys.exit()

	if item["%s_chi2" % method] > 500:
		print '='*80
		print 'id=',item["id"]
		print 'chi2=',item["%s_chi2" % method]
		print 'P=',item["%s_P" % method]
		print 'A=',item["%s_A" % method]				 
		print 'true delay=',item["truetd"]
		print 'guessed delay=',item["%s_td" % method]
		print 'error bars=',item["%s_tderr" % method]		



sys.exit()

plt.figure('blah',(15,4))
plt.subplot(1,3,1)
plt.hist(chi2s,bins=100)
plt.subplot(1,3,2)
plt.hist(As,bins=100)
plt.subplot(1,3,3)
plt.hist(Ps,bins=100)
plt.show()
sys.exit()

### Check if we agree with evil team submission file... ###

method = 'pycs_tdc1_d3cs-vanilla-dou-full'

db_r0 = [item for item in db if item["rung"] == 0]
print len(db_r0)


print 'f=',pycs.tdc.metrics.getf(db_r0,method,N=len(db_r0))
print 'chi2=',pycs.tdc.metrics.getchi2(db_r0,method)
print 'P=',pycs.tdc.metrics.getP(db_r0,method)
print 'A=',pycs.tdc.metrics.getA(db_r0,method)
print 'Amod=',pycs.tdc.metrics.getAmod(db_r0,method)
"""

### Play with db values ###

#methods = ["pycs_tdc1_spl-vanilla-doupla-full","pycs_tdc1_sdi-vanilla-doupla-full","pycs_tdc1_d3cs-vanilla-doupla-full"]
#methods = ["pycs_tdc1_spl-vanilla-dou-full","pycs_tdc1_spl-vanilla-dou-P3percent","pycs_tdc1_spl-vanilla-dou-800bestP","pycs_tdc1_spl-vanilla-dou-100bestP"]
#methods = ["pycs_tdc1_spl-vanilla-doupla-full","pycs_tdc1_spl-vanilla-doupla-P3percent","pycs_tdc1_spl-vanilla-doupla-1600bestP","pycs_tdc1_spl-vanilla-doupla-800bestP","pycs_tdc1_spl-vanilla-doupla-100bestP"]
#methods = ["pycs_tdc1_spl-vanilla-doupla-1600bestP","pycs_tdc1_spl-vanilla-doupla-800bestP"]

methods = ["pycs_tdc1_spl-vanilla-dou-full","pycs_tdc1_sdi-vanilla-dou-full","pycs_tdc1_d3cs-vanilla-dou-full"]
#pycs.tdc.metrics.Pplotall(db,methods=methods,N=len(db))
pycs.tdc.metrics.Pplotcombi(db,methods=methods,N=len(db),lensmodelsigma=0.0)

