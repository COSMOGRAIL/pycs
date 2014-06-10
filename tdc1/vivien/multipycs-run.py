import pycs
import numpy as np
import sys,time	
import multiprocessing


'''
Here, we assume that iniests contain for every pair ONE estimate of the delay. We use that estimate to feed PyCS
make it run on multi cpus in parallel...
'''

## Change the parameters of your run here (see README.txt for more details)

method = 'spl' 	# spl, sdi
select = 'dou'	# dou, pla, mul, dtm, dtu, uni 
ncopy  = 2 	# c
nsim   = 10   	# s
maxshift = 4	# m
rtype = 'uni'	# uni, ...
rung   = 2	# r

drawdir = '%s-%s-c%s-s%s-m%s-%s-r%s' %(method,select,ncopy,nsim,maxshift,rtype,rung)

print drawdir

# optfct choice

if method == 'spl':
	optfct = pycs.tdc.splopt.spl2

if method == 'sdi':
	optfct = pycs.tdc.optfct.spldiff  


# selection choice

if select == 'dou':
	selection = pycs.gen.util.readpickle('../../groupedestimates/doubtlesses.pkl')
if select == 'pla':
	selection = pycs.gen.util.readpickle('../../groupedestimates/plausibles.pkl')		
if select == 'mul':
	selection = pycs.gen.util.readpickle('../../groupedestimates/multimodals.pkl')
if select == 'dtm':
	selection = pycs.gen.util.readpickle('../../groupedestimates/doubtless_to_multimodals.pkl')	
if select == 'dtu':
	selection = pycs.gen.util.readpickle('../../groupedestimates/doubtless_to_uninformatives.pkl')	
if select == 'uni': # in principle not needed...
	selection = pycs.gen.util.readpickle('../../groupedestimates/uninformatives.pkl')		
	
	
	
def drawnrun(est):
	
	if 0: # No ML
		pycs.tdc.run2.drawcopy(est, drawdir, n=ncopy, maxrandomshift = maxshift) 
		pycs.tdc.run2.drawsim(est, drawdir, sploptfct=pycs.tdc.splopt.spl2, n=nsim, maxrandomshift = maxshift)	
		outest = pycs.tdc.run2.multirun(est, drawdir, optfct = optfct, ncopy=ncopy, nsim=nsim)
		return outest[0]

	if 1: # With ML (default behaviour...?)
		pycs.tdc.run2.drawcopy(est, drawdir, n=ncopy, maxrandomshift = maxshift, addmlfct=pycs.tdc.splopt.splml1) 
		pycs.tdc.run2.drawsim(est, drawdir, sploptfct=pycs.tdc.splopt.spl2, n=nsim, maxrandomshift = maxshift, addmlfct=pycs.tdc.splopt.splml1)	
		outest = pycs.tdc.run2.multirun(est, drawdir, optfct = optfct, ncopy=ncopy, nsim=nsim)
		return outest[0]		

def start_process():

	print "Starting ",multiprocessing.current_process().name


if __name__ == '__main__':
	
	iniests = pycs.tdc.est.importfromd3cs("../../web/d3cslog.txt") # where d3cslog is located	
		
	if 1: # whole sample - rungx
		allests = pycs.tdc.est.select(iniests,idlist=selection)	
		allests = [est for est in allests if est.rung==rung]
							
		
	if 0:  #doubtless - no ML sample
		#est0 = pycs.tdc.est.select(iniests, rungs=[0], pairs=[26,225,316,524,703])
		est0 = pycs.tdc.est.select(iniests, rungs=[0], pairs=[26])
		est1 = pycs.tdc.est.select(iniests, rungs=[1], pairs=[7,118,226,423,583])
		est2 = pycs.tdc.est.select(iniests, rungs=[2], pairs=[64,112,192,514,857])
		est3 = pycs.tdc.est.select(iniests, rungs=[3], pairs=[25,206,296,487,587])
		est4 = pycs.tdc.est.select(iniests, rungs=[4], pairs=[314,408,478,555,650])
		allests = est0


	if 0: #doubtless - with ML sample
		est0 = pycs.tdc.est.select(iniests, rungs=[0], pairs=[161,277,487,671,875])
		#est0 = pycs.tdc.est.select(iniests, rungs=[0], pairs=[487])
		est1 = pycs.tdc.est.select(iniests, rungs=[1], pairs=[52,520,245,376,875])
		est2 = pycs.tdc.est.select(iniests, rungs=[2], pairs=[160,460,483,666,875])
		est3 = pycs.tdc.est.select(iniests, rungs=[3], pairs=[150,317,472,838,875])
		est4 = pycs.tdc.est.select(iniests, rungs=[4], pairs=[293,365,594,838,875])	
		allests = est0+est1+est2+est3+est4

			
	combiests = pycs.tdc.est.multicombine(allests,method='d3cscombi1')	
	seqests   = [[est] for est in combiests]
	
	if 1:
		start=time.time()
		pool_size = multiprocessing.cpu_count()
		#pool_size = 1
		pool = multiprocessing.Pool(processes = pool_size,
						initializer=start_process,
						)
		
		pycs.tdc.run2.createdir(combiests,drawdir)
		pool_out = pool.map(drawnrun,seqests)
		pool.close()	
		pool.join()	

		stop = time.time()
		print 'time taken=',(stop-start)/60.0,' [min]'
		pycs.gen.util.writepickle(pool_out,drawdir+'.pkl')

	
	#sys.exit()	
	outests = pycs.gen.util.readpickle(drawdir+'.pkl')
	plotpath = drawdir+'.png'
	pycs.tdc.est.interactivebigplot(allests, shadedestimates=combiests+outests,interactive=False,plotpath=plotpath) # may crash if estlists are too long...
