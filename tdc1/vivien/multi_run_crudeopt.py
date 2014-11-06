import pycs
import numpy as np
import sys,time,os	
import multiprocessing
from crudeopt_multi import *

"""
run on multicpus...
"""


#### Main function : takes rung and pair indices, and return the crude optimisation of it
#### Put every variable into a single arg, thus multiprocessing does not complain... 

def crudeopt_singleshift(arg):
	
	(myrung,mypair,myworkdirbase) = arg
	
	myworkdir = '%s/tdc1_%i_%i' %(myworkdirbase,myrung,mypair)
	if not os.path.isdir(myworkdir):
		os.mkdir(myworkdir)

	# check if residual computation has already been made
	if os.path.isfile(os.path.join(myworkdir,'plot_res.png')):
		print '%s already treated' % os.path.basename(myworkdir)
		return
	
	# get the spline and lcs
	mylcs,myspline = fitsplinesinglecurve(rung=myrung,pair=mypair,workdir=myworkdir)


	# get the grid
	mymagsteps,mytimesteps = getgrid(lcs=mylcs)

	# get the residuals
	myresiduals = getresiduals(lcs=mylcs,spline=myspline,magsteps=mymagsteps,mytimesteps=mytimesteps,resmode='singleshift',
					minoverlap=3,workdir=myworkdir,display=False)
	
	# plot the residuals
	displaycrudeopt(rung=myrung,pair=mypair,residuals=myresiduals,timesteps=mytimesteps,magsteps=mymagsteps,
					resmode='singleshift',workdir=myworkdir,savefig=True)

def crudeopt_perseasons(arg):

	(myrung,mypair,myworkdirbase) = arg
	
	myworkdir = '%s/tdc1_%i_%i' %(myworkdirbase,myrung,mypair)
	if not os.path.isdir(myworkdir):
		os.mkdir(myworkdir)

	# check if residual computation has already been made
	if os.path.isfile(os.path.join(myworkdir,'plot_mlres.png')):
		print '%s already treated' % os.path.basename(myworkdir)
		return

	# get the spline and lcs
	mylcs,myspline = fitsplinesinglecurve(rung=myrung,pair=mypair,workdir=myworkdir)

	# get the grid
	mymagsteps,mytimesteps = getgrid(lcs=mylcs,nmagsteps=40,ntimesteps=200)
	
	# get the residuals
	myresiduals = getresiduals(lcs=mylcs,spline=myspline,magsteps=mymagsteps,mytimesteps=mytimesteps,resmode='perseasons',
					minoverlap=6,workdir=myworkdir,display=False)
					
	# plot the residuals					
	displaycrudeopt(rung=myrung,pair=mypair,residuals=myresiduals,timesteps=mytimesteps,magsteps=mymagsteps,
					resmode='perseasons',workdir=myworkdir,savefig=True)					
	
	
#### Get the pairs I want to run on...
wkb = 'dou-2'

db = pycs.gen.util.readpickle("../joined.pkl").values()
items = [item for item in db if "confidence" in item]
items = [item for item in items if item["confidence"] == 1]
args=[]
for item in items:
	args.append((item["rung"],item["pair"],wkb)) 



def start_process():
	print "Starting ",multiprocessing.current_process().name

# Run with multiprocessing


pool_size = multiprocessing.cpu_count()
pool = multiprocessing.Pool(processes = pool_size, initializer=start_process)
pool_out = pool.map(crudeopt_perseasons,args)
pool.close()	
pool.join()	








