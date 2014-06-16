import pycs
import numpy as np
import sys,time,os	
import multiprocessing

execfile('config_vivien.py')

'''
Check if we can open every copycurve and create a copy of it.
'''

## Change the parameters of your run here (see README.txt for more details)

method = 'spl' 	# spl, sdi
select = 'dou'	# dou, pla, mul, dtm, dtu, uni 
ncopy  = 1 	# c
nsim   = 1   	# s
maxshift = 8	# m
rung   = 0	# r

drawname = 'TEST_open_and_draw_2' 
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


# selection choice

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
	
	
	
def draw(est):
	"""
	Check if a .pkl with the results of the optimization already exists
	If not, draw copy and sim curves, and run the optimizer on them.
	Then, save the results in a .pkl
	"""
	resultpklpath = os.path.join(drawdir,'%s.pkl' % est.id)
	print resultpklpath
	
	
	if not os.path.isfile(resultpklpath):	
	
		try:
			pycs.tdc.run2.drawcopy([est], drawdir, n=ncopy, maxrandomshift = maxshift, addmlfct=pycs.tdc.splopt.splml1,datadir=datadir) 
			pycs.tdc.run2.drawsim([est], drawdir, sploptfct=pycs.tdc.splopt.spl2, n=nsim, maxrandomshift = maxshift, addmlfct=pycs.tdc.splopt.splml1,datadir=datadir)	
				
		except:
			errfile = open('err_2.txt','a')
			errfile.write('error on %s' %est.id)
			errfile.close()
		
	else:	
		print 'pycs estimate has already been computed for %s' %est.niceid 
		return pycs.gen.util.readpickle(resultpklpath)			

def start_process():

	print "Starting ",multiprocessing.current_process().name


if __name__ == '__main__':

	# Import the estimates from d3cs, and select the ones we are interested in
	
	iniests = pycs.tdc.est.importfromd3cs(d3cslogpath) # where d3cslog is located									
	combiests = pycs.tdc.est.multicombine(iniests,method='d3cscombi1')
	
	

	start=time.time()
	pool_size = multiprocessing.cpu_count()
	pool = multiprocessing.Pool(processes = pool_size,
					initializer=start_process,
					)

	pycs.tdc.run2.createdir(combiests,drawdir)
	pool_out = pool.map(draw,combiests)
	pool.close()	
	pool.join()	

	stop = time.time()
	print 'time taken=',(stop-start)/60.0,' [min]'
	pycs.gen.util.writepickle(pool_out,drawdir+'.pkl')

	
	'''	
	outests = pycs.gen.util.readpickle(drawdir+'.pkl')
	plotpath = drawdir+'.png'
	pycs.tdc.est.interactivebigplot(allests, shadedestimates=combiests+outests,interactive=False,plotpath=plotpath) # may crash if estlists are too long...
	'''
