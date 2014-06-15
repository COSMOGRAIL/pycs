import pycs
import numpy as np
import sys,time,os	
import multiprocessing

execfile('config.py')

'''
This script draw copy and sim curves, and run pycs on them
The script run on multi cpus in parallel...(on all the available cpus !)
The output directory can be changed in config.py
'''


## Change the parameters of your run here (see README.txt for more details)

method = 'spl' 	# spl, sdi
select = 'dou'	# dou, pla, mul, dtm, dtu, uni 
ncopy  = 2 	# c
nsim   = 2   	# s
maxshift = 4	# m
rung   = 0	# r

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
	selection = pycs.gen.util.readpickle(os.path.join(groupedestimatespath,'1.pkl'))
if select == 'pla':
	selection = pycs.gen.util.readpickle(os.path.join(groupedestimatespath,'2.pkl'))		
if select == 'mul':
	selection = pycs.gen.util.readpickle(os.path.join(groupedestimatespath,'3.pkl'))
if select == 'dtm':
	selection = pycs.gen.util.readpickle(os.path.join(groupedestimatespath,'4.pkl'))	
if select == 'dtu':
	selection = pycs.gen.util.readpickle(os.path.join(groupedestimatespath,'5.pkl'))	
if select == 'uni': # in principle not needed...
	selection = pycs.gen.util.readpickle(os.path.join(groupedestimatespath,'6.pkl'))		
	
	
	
def drawnrun(est):
	"""
	Check if a .pkl with the results of the optimization already exists
	If not, draw copy and sim curves, and run the optimizer on them.
	Then, save the results in a .pkl
	"""
	resultpklpath = os.path.join(drawdir,'%s.pkl' % est.id)
	print resultpklpath
	
	
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

	# Import the estimates from d3cs, and select the ones we are interested in
	
	iniests = pycs.tdc.est.importfromd3cs(d3cslogpath)			
	allests = pycs.tdc.est.select(iniests,idlist=selection)	
	allests = [est for est in allests if est.rung==rung]										
	combiests = pycs.tdc.est.multicombine(allests,method='d3cscombi1') # we combine the d3cs estimates into one single estimate per pair
		
	

	start=time.time()
	pool_size = multiprocessing.cpu_count()
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

