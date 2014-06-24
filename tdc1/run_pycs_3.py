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

#method = 'spl' 	# spl, sdi
#select = 'mul'	# dou, pla, mul, uni

ncopy  = 20 	# c
nsim   = 40   	# s
maxshift = 8	# m
pool_size = 10

#drawname = '%s-%s-c%s-s%s-m%s-r%s' %(method,select,ncopy,nsim,maxshift,rung)

drawname = "spl3-dou-run1"
drawdir = os.path.join(pycsresdir,drawname)
selectedconf = 1

def optfct(lcs):
	return pycs.tdc.splopt.spl3(lcs, knotstepfact=1.0, mlknotstep=365, maxit=7, minchange=1.0, verbose=False)


def drawnrun(est):
	"""
	Check if a .pkl with the results of the optimization already exists
	If not, draw copy and sim curves, and run the optimizer on them.
	Then, save the results in a .pkl
	"""
	resultpklpath = os.path.join(drawdir,'%s.pkl' % est.id)
	#print resultpklpath

	
	if not os.path.isfile(resultpklpath):	
	
		try:
			pycs.tdc.run3.drawcopy(est, drawdir, n=ncopy, maxrandomshift = maxshift,datadir=datadir) 
			pycs.tdc.run3.drawsim(est, drawdir, sploptfct=optfct, n=nsim, maxrandomshift = maxshift, datadir=datadir)	
			outest = pycs.tdc.run3.multirun(est, drawdir, optfct=optfct, ncopy=ncopy, nsim=nsim)		
			pycs.gen.util.writepickle(outest,resultpklpath)
			return outest
		except Exception as e:			
			errfile = open(os.path.join(drawdir,'err_%s' %est.niceid),'w')
			errfile.write(str(e))
			errfile.close()

	else:	
		print 'pycs estimate has already been computed for %s' %est.niceid 
		return pycs.gen.util.readpickle(resultpklpath)	


def start_process():

	print "Starting ",multiprocessing.current_process().name


#########   Here comes the actual selection of items and also keys that you want to use as PyCS input  #############

db = pycs.gen.util.readpickle("joined.pkl").values()

selection = [item for item in db if "confidence" in item and item["confidence"] == selectedconf]

#selection = selection[:5]

ests = []
for item in selection:
	newest = pycs.tdc.est.Estimate(set="tdc1", rung=item["rung"], pair=item["pair"])
	newest.td = item["d3cs_combi_td"]
	newest.tderr = item["d3cs_combi_tderr"]
	ests.append(newest)


print "I have selected %i estimates." % (len(ests))


########## And we run, and save the results into a summary pickle ##############

"""
pool_out = []

for est in ests:
	pycs.tdc.run3.createdir(est,drawdir)
	out = drawnrun(est)
	pool_out.append(out)

pycs.gen.util.writepickle(pool_out,drawdir+'.pkl')
"""


start=time.time()
#pool_size = multiprocessing.cpu_count()
pool = multiprocessing.Pool(processes = pool_size,
				initializer=start_process,
				)

for est in ests:
	pycs.tdc.run3.createdir(est,drawdir)
pool_out = pool.map(drawnrun,ests)
pool.close()	
pool.join()	

stop = time.time()
print 'time taken=',(stop-start)/60.0,' [min]'
pycs.gen.util.writepickle(pool_out,drawdir+'.pkl')

