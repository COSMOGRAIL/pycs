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

ncopy  = 3 	# c
nsim   = 3   	# s
maxshift = 8	# m
pool_size = 5

#drawname = '%s-%s-c%s-s%s-m%s-r%s' %(method,select,ncopy,nsim,maxshift,rung)

drawname = "spl3-dou-run1"
drawdir = os.path.join(pycsresdir,drawname)
selectedconf = 1

def optfct(lcs):
	return pycs.tdc.splopt.spl3(lcs, knotstepfact=1.0, mlknotstep=365, maxit=7, minchange=1.0, verbose=False)


def drawnrun(est):
		
	try:
		pycs.tdc.run3.drawcopy(est, drawdir, n=ncopy, maxrandomshift = maxshift,datadir=datadir) 
		pycs.tdc.run3.drawsim(est, drawdir, sploptfct=optfct, n=nsim, maxrandomshift = maxshift, datadir=datadir)	
		pycs.tdc.run3.multirun(est, drawdir, optfct=optfct, ncopy=ncopy, nsim=nsim)		
		
	except Exception as e:			
		print "Error !", e
		errfile = open(os.path.join(drawdir,'err_%s' %est.niceid),'w')
		errfile.write(str(e))
		errfile.close()
	
def start_process():
	print "Starting ",multiprocessing.current_process().name



#########   Here comes the actual selection of items and also keys that you want to use as PyCS input  #############

db = pycs.gen.util.readpickle("joined.pkl").values()

selection = [item for item in db if "confidence" in item and item["confidence"] == selectedconf]

#selection = selection[:5]
selection = selection[:3]

ests = []
for item in selection:
	newest = pycs.tdc.est.Estimate(set="tdc1", rung=item["rung"], pair=item["pair"])
	newest.td = item["d3cs_combi_td"]
	newest.tderr = item["d3cs_combi_tderr"]
	ests.append(newest)


print "I have selected %i estimates." % (len(ests))

for est in ests:
	pycs.tdc.run3.createdir(est,drawdir)

########## And we run, and save the results into a summary pickle ##############


# Run without  multiprocessing
"""
for est in ests:
	drawnrun(est)
"""

# Run with multiprocessing
"""
start=time.time()
#pool_size = multiprocessing.cpu_count()
pool = multiprocessing.Pool(processes = pool_size, initializer=start_process)
pool_out = pool.map(drawnrun,ests)
pool.close()	
pool.join()	

stop = time.time()
print 'time taken=',(stop-start)/60.0,' [min]'
"""

"""
est = ests[0]
pycs.tdc.run3.viz(est, drawdir, datadir=datadir)
"""



for est in ests:
	pycs.tdc.run3.summarize(est, drawdir, makefig=True)



# Collect the results
"""
outests = collect(estimates, drawdir)
pycs.gen.util.writepickle(outests,drawdir+'.pkl')

"""



