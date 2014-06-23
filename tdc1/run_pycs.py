import pycs
import numpy as np
import sys,time,os	
import multiprocessing

execfile('config_vivien.py')

'''
This script draw copy and sim curves, and run pycs on them
The script run on multi cpus in parallel...(on all the available cpus !)
The output directory can be changed in config.py
'''


## Change the parameters of your run here (see README.txt for more details)

method = 'sdi' 	# spl, sdi
select = 'mul'	# dou, pla, mul, uni
ncopy  = 20 	# c
nsim   = 100   	# s
maxshift = 8	# m
rung   = 'all'	# r

drawname = '%s-%s-c%s-s%s-m%s-r%s' %(method,select,ncopy,nsim,maxshift,rung)
drawdir = os.path.join(pycsresdir,drawname)

print '='*80
print 'I will draw the copycurves in \n%s' % drawdir
pycs.tdc.util.goingon()
print '='*80



# optfct choice

if method == 'spl':
	optfct = pycs.tdc.splopt.spl2

if method == 'sdi':
	optfct = pycs.tdc.optfct.spldiff  


# selection of the estimates (according to confidence defined in make_confidence_id_pkls)

if select == 'dou':
	selectedconf = 1
if select == 'pla':
	selectedconf = 2		
if select == 'mul':
	selectedconf = 3	
if select == 'uni': # in principle not needed...
	selectedconf = 4		
	
	
	
def drawnrun(est,lock):
	"""
	Check if a .pkl with the results of the optimization already exists
	If not, draw copy and sim curves, and run the optimizer on them.
	Then, save the results in a .pkl
	"""
	resultpklpath = os.path.join(drawdir,'%s.pkl' % est.id)
	#print resultpklpath

	
	if not os.path.isfile(resultpklpath):	
	

		pycs.tdc.run2.drawcopy([est], drawdir, n=ncopy, maxrandomshift = maxshift, addmlfct=pycs.tdc.splopt.splml1,datadir=datadir) 
		pycs.tdc.run2.drawsim([est], drawdir, sploptfct=pycs.tdc.splopt.spl2, n=nsim, maxrandomshift = maxshift, addmlfct=pycs.tdc.splopt.splml1,datadir=datadir)	
		outests = pycs.tdc.run2.multirun([est], drawdir, optfct = optfct, ncopy=ncopy, nsim=nsim)		
		pycs.gen.util.writepickle(outests[0],resultpklpath)
		return outests[0]

	else:	
		print 'pycs estimate has already been computed for %s' %est.niceid 
		return pycs.gen.util.readpickle(resultpklpath)			

def start_process():

	print "Starting ",multiprocessing.current_process().name


if __name__ == '__main__':

	# Import the estimates from combiests_bg
	
										
	combiests = pycs.gen.util.readpickle("../results_tdc1/combi_confidence_ids/combiests_ag.pkl") 
	combiests = [est for est in combiests if est.confidence == selectedconf]
	print len(combiests)
	

	start=time.time()
	pool_size = multiprocessing.cpu_count()
	#pool_size = 8
	pool = multiprocessing.Pool(processes = pool_size,
					initializer=start_process,
					)

	pycs.tdc.run2.createdir(combiests,drawdir)
	pool_out = pool.map(drawnrun,combiests)
	pool.close()	
	pool.join()	

	stop = time.time()
	print 'time taken=',(stop-start)/60.0,' [min]'
	pycs.gen.util.writepickle(pool_out,drawdir+'.pkl')

