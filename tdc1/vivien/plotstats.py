import pycs
import numpy as np
import sys,time	
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


'''
plot some statistics on pycs results

Add this to PyCS once it is finalized.
'''

# Import results from the rungs


#spline methode

est0 = pycs.gen.util.readpickle('results/spl-dou-c20-s100-m8-uni-r0.pkl')
est1 = pycs.gen.util.readpickle('results/spl-dou-c20-s100-m8-uni-r1.pkl')
est2 = pycs.gen.util.readpickle('results/spl-dou-c20-s100-m8-uni-r2.pkl')
est3 = pycs.gen.util.readpickle('results/spl-dou-c20-s100-m8-uni-r3.pkl')
est4 = pycs.gen.util.readpickle('results/spl-dou-c20-s100-m8-uni-r4.pkl')

est0p = pycs.gen.util.readpickle('results/spl-pla-c20-s100-m8-uni-r0.pkl')
est1p = pycs.gen.util.readpickle('results/spl-pla-c20-s100-m8-uni-r1.pkl')
est2p = pycs.gen.util.readpickle('results/spl-pla-c20-s100-m8-uni-r2.pkl')
est3p = pycs.gen.util.readpickle('results/spl-pla-c20-s100-m8-uni-r3.pkl')
est4p = pycs.gen.util.readpickle('results/spl-pla-c20-s100-m8-uni-r4.pkl')

outests_spl = est0+est1+est2+est3+est4+est0p+est1p+est2p+est3p+est4p


#spline diff method
est0_sdi = pycs.gen.util.readpickle('results/sdi-dou-c20-s100-m8-uni-r0.pkl')
est1_sdi = pycs.gen.util.readpickle('results/sdi-dou-c20-s100-m8-uni-r1.pkl')
est2_sdi = pycs.gen.util.readpickle('results/sdi-dou-c20-s100-m8-uni-r2.pkl')
est3_sdi = pycs.gen.util.readpickle('results/sdi-dou-c20-s100-m8-uni-r3.pkl')
est4_sdi = pycs.gen.util.readpickle('results/sdi-dou-c20-s100-m8-uni-r4.pkl')

est0p_sdi = pycs.gen.util.readpickle('results/sdi-pla-c20-s100-m8-uni-r0.pkl')
est1p_sdi = pycs.gen.util.readpickle('results/sdi-pla-c20-s100-m8-uni-r1.pkl')
est2p_sdi = pycs.gen.util.readpickle('results/sdi-pla-c20-s100-m8-uni-r2.pkl')
est3p_sdi = pycs.gen.util.readpickle('results/sdi-pla-c20-s100-m8-uni-r3.pkl')
est4p_sdi = pycs.gen.util.readpickle('results/sdi-pla-c20-s100-m8-uni-r4.pkl')

outests_sdi = est0_sdi+est1_sdi+est2_sdi+est3_sdi+est4_sdi+est0p_sdi+est1p_sdi+est2p_sdi+est3p_sdi+est4p_sdi



# Import original estimates, for comparison:

iniests = pycs.tdc.est.importfromd3cs("../../web/d3cslog.txt") # where d3cslog is located 
selection_doubtless = pycs.gen.util.readpickle('../../groupedestimates/doubtlesses.pkl') # list of IDs, according to selection criteria
selection_plausible = pycs.gen.util.readpickle('../../groupedestimates/plausibles.pkl')
selection = selection_doubtless + selection_plausible
allests = pycs.tdc.est.select(iniests,idlist=selection)	 
combiests = pycs.tdc.est.multicombine(allests,method='d3cscombi1')


	

# Now, some statistics...

tds_spl     = [est.td for est in outests_spl]
tderrs_spl  = [abs(est.tderr) for est in outests_spl]
tdfracs_spl = [abs(est.tderr*1.0 / est.td) *100.0 for est in outests_spl]


tds_sdi     = [est.td for est in outests_sdi]
tderrs_sdi  = [abs(est.tderr) for est in outests_sdi]
tdfracs_sdi = [abs(est.tderr*1.0 / est.td) *100.0 for est in outests_sdi]  


d3tds	  = [est.td for est in combiests] 
d3tderrs  = [abs(est.tderr) for est in combiests]
d3tdfracs = [abs(est.tderr*1.0 / est.td) *100.0 for est in combiests]



tds_spl_sdi     = [spl.td - sdi.td for spl,sdi in zip(outests_spl,outests_sdi)]
tderrs_spl_sdi  = [spl.tderr - sdi.tderr for spl,sdi in zip(outests_spl,outests_sdi)]
tdfracs_spl_sdi = [abs(spl.tderr*1.0/spl.td) - abs(sdi.tderr*1.0/sdi.td) for spl,sdi in zip(outests_spl,outests_sdi)]

print len(d3tds),len(tds_sdi),len(tds_spl)
sys.exit()

# difference between eye estimation and pycs estimation histogram :

tdcomps_spl = []
tdcomps_sdi = []
tderrcomps_spl = []
tderrcomps_sdi = []


for outest_spl,outest_sdi,combiest in zip(outests_spl,outests_sdi,combiests):
	tdcomps_spl.append(outest_spl.td-combiest.td)
	tderrcomps_spl.append((outest_spl.tderr-combiest.tderr))
	tdcomps_sdi.append(outest_sdi.td-combiest.td)
	tderrcomps_sdi.append((outest_sdi.tderr-combiest.tderr))
	

plt.figure('delays and errors repartition')

plt.subplot(4,1,1)
plt.hist(tds_spl,histtype='step',range=(-100,100),bins=200,color='chartreuse',linewidth=1.5,label='PyCS-spl / median : %.2f'%np.median(tds_spl))
plt.hist(tds_sdi,histtype='step',range=(-100,100),bins=200,color='indigo',linewidth=1.5,label='PyCS-sdi / median : %.2f'%np.median(tds_sdi))
plt.hist(d3tds,histtype='step',range=(-100,100),bins=200,color='crimson',linewidth=1.5,label='D3CS / median : %.2f'%np.median(d3tds))
plt.axvline(np.median(tds_spl),color='chartreuse',linestyle='dashed',linewidth=2)
plt.axvline(np.median(tds_sdi),color='indigo',linestyle='dashed',linewidth=2)
plt.axvline(np.median(d3tds),color='crimson',linestyle='dashed',linewidth=2)
plt.legend()
plt.xlabel('estimated delays [days]')
plt.ylabel('#')
plt.annotate('%s estimates' %len(tds_spl),xy=[0.05,0.85],xycoords='axes fraction')

plt.subplot(4,1,2)
plt.hist(tderrs_spl,histtype='step',range=(0,20),bins=50,color='chartreuse',linewidth=1.5)
plt.hist(tderrs_sdi,histtype='step',range=(0,20),bins=50,color='indigo',linewidth=1.5)
plt.hist(d3tderrs,histtype='step',range=(0,20),bins=50,color='crimson',linewidth=1.5)
plt.axvline(np.median(tderrs_spl),color='chartreuse',linestyle='dashed',linewidth=2,label='median : %.2f'%np.median(tderrs_spl))
plt.axvline(np.median(tderrs_sdi),color='indigo',linestyle='dashed',linewidth=2,label='median : %.2f'%np.median(tderrs_sdi))
plt.axvline(np.median(d3tderrs),color='crimson',linestyle='dashed',linewidth=2,label='median : %.2f'%np.median(d3tderrs))
plt.legend(loc=7)
plt.xlabel('estimated errors [days]')
plt.ylabel('#')

plt.subplot(4,1,3)
plt.hist(tdfracs_spl,histtype='step',range=(0,50),bins=50,color='chartreuse',linewidth=1.5)
plt.hist(tdfracs_sdi,histtype='step',range=(0,50),bins=50,color='indigo',linewidth=1.5)
plt.hist(d3tdfracs,histtype='step',range=(0,50),bins=50,color='crimson',linewidth=1.5)
plt.axvline(np.median(tdfracs_spl),color='chartreuse',linestyle='dashed',linewidth=2,label='median : %.2f'%np.median(tdfracs_spl))
plt.axvline(np.median(tdfracs_sdi),color='indigo',linestyle='dashed',linewidth=2,label='median : %.2f'%np.median(tdfracs_sdi))
plt.axvline(np.median(d3tdfracs),color='crimson',linestyle='dashed',linewidth=2,label='median : %.2f'%np.median(d3tdfracs))
plt.legend(loc=7)
plt.xlabel('realtive estimated error [%]')
plt.ylabel('#')

plt.subplot(4,1,4)
plt.hist(tdcomps_spl,histtype='step',range=(-10,10),bins=50,color='dodgerblue',linewidth=1.5,label='delays-spl / median : %.2f'%np.median(tdcomps_spl))
plt.hist(tderrcomps_spl,histtype='step',range=(-10,10),bins=50,color='lightsteelblue',linewidth=1.5,label='errors-spl / median : %.2f'%np.median(tderrcomps_spl))
plt.hist(tdcomps_sdi,histtype='step',range=(-10,10),bins=50,color='darkorange',linewidth=1.5,label='delays-sdi / median : %.2f'%np.median(tdcomps_sdi))
plt.hist(tderrcomps_sdi,histtype='step',range=(-10,10),bins=50,color='goldenrod',linewidth=1.5,label='errors-sdi / median : %.2f'%np.median(tderrcomps_sdi))
plt.axvline(np.median(tdcomps_spl),color='dodgerblue',linestyle='dashed',linewidth=2)
plt.axvline(np.median(tderrcomps_spl),color='lightsteelblue',linestyle='dashed',linewidth=2)
plt.axvline(np.median(tdcomps_sdi),color='darkorange',linestyle='dashed',linewidth=2)
plt.axvline(np.median(tderrcomps_sdi),color='goldenrod',linestyle='dashed',linewidth=2)

plt.legend(loc=1)
plt.xlabel('PyCS - D3CS [days]')
plt.ylabel('#')



plt.figure('comparison between methods')

ax1=plt.subplot(3,1,1)
ax1.hist(tds_spl_sdi,histtype='step',range=(-5,5),bins=50,color='chartreuse',linewidth=1.5,label='time delay / median : %.2f'%np.median(tds_spl_sdi))
ax1.axvline(np.median(tds_spl_sdi),color='chartreuse',linestyle='dashed',linewidth=2)
ax1.set_ylabel('#')
ax1.yaxis.set_major_locator(MaxNLocator(3))
ax1.legend()

ax2 = plt.subplot(3,1,2)
ax2.hist(tderrs_spl_sdi,histtype='step',range=(-5,5),bins=50,color='indigo',linewidth=1.5,label='error on delay / median : %.2f'%np.median(tderrs_spl_sdi))
ax2.axvline(np.median(tderrs_spl_sdi),color='indigo',linestyle='dashed',linewidth=2)
ax2.set_ylabel('#')
ax2.yaxis.set_major_locator(MaxNLocator(3))
ax2.legend()

ax3 = plt.subplot(3,1,3)
ax3.hist(tdfracs_spl_sdi,histtype='step',range=(-0.4,0.4),bins=50,color='crimson',linewidth=1.5,label='relative error / median : %.2f'%np.median(tdfracs_spl_sdi))
ax3.axvline(np.median(tdfracs_spl_sdi),color='crimson',linestyle='dashed',linewidth=2)
ax3.legend()
ax3.set_xlabel('Spline - Splinedifference [days]')
ax3.set_ylabel('#')
ax3.yaxis.set_major_locator(MaxNLocator(3))
plt.show()
