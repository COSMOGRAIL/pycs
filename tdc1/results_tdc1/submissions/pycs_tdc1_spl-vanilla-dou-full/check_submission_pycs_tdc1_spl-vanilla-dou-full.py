import numpy as np
import pycs
import os,sys
import matplotlib as mpt
import matplotlib.pyplot as plt

'''
takes path to a submission file as argrument

reads in the joined.pkl

makes a scatter plot of estimates vs D3CS combi, using colour to show distance from D3CS in terms of D3CS error bars.
'''

execfile('config.py')


subname = "pycs_tdc1_spl-vanilla-dou-full"
filepath = os.path.join(pycsresdir,'submissions',subname,subname+'.dt')
dirpath = os.path.dirname(filepath)



def readsubmission(filepath):

	subinfos = []

	# we read the submission file and remove the comments
	lines = open(filepath,'r').xreadlines()
	cleanlines = [line for line in lines if line[0] != '#']
	
	# now, we extract the values we are interested in (id, td, tderr)	
	# Typical line of a .dt submission file : 	tdc1_rung0_double_pair1.txt	  -70.45	   11.70
	#						tdc1_rung4_quad_pair142A.txt	   17.55	    5.70

	for line in cleanlines:
	
		infos = [info for info in line.split(' ') if info != '']
		
		# get the id
		filename = infos[0].split('\t')[0]
		
		rung	 = filename.split('rung')[1].split('_')[0]
		pair_tdc = filename.split('pair')[1].split('.txt')[0]
		
		
		if 'A' in pair_tdc or 'B' in pair_tdc: # then it's a quad
		
			quadcode  = pair_tdc[-1] # get the A or B
			quadadd	  = -1 if quadcode == 'A' else 0
			pair_tdc  = pair_tdc.split('A')[0].split('B')[0]
			pair_pycs = 2*int(pair_tdc) + 720 + quadadd
		
		else: # then it's a double
			pair_pycs = pair_tdc
		
		
		estid   = 'tdc1_%s_%s' % (rung,pair_pycs)
		
		
		# get the delay td and the error tderr
		
		td    = infos[1].split('\t')[0]
		tderr = infos[2].split('\n')[0]
		

		if td != '-99.00' and tderr != '-99.00':
			subinfos.append((estid,-float(td),float(tderr))) # The - sign is as conventions change between tdc and pycs 
	
	return subinfos		
		


subinfos = readsubmission(filepath)


# Now, load the database, and select the entries corresponding to the .dt submission

db = pycs.gen.util.readpickle('joined.pkl')
subids = [info[0] for info in subinfos]


sub_td = [info[1] for info in subinfos]
sub_tderr = [info[2] for info in subinfos]
sub_reltderr = [info[2]/abs(info[1]) for info in subinfos]
d3cs_td = [db[subid]["d3cs_combi_td"] for subid in subids]
d3cs_tderr = [db[subid]["d3cs_combi_tderr"] for subid in subids]
d3cs_reltderr = [db[subid]["d3cs_combi_reltderr"] for subid in subids]

cmap = [abs(info[1]-db[subid]["d3cs_combi_td"])/db[subid]["d3cs_combi_tderr"] for info,subid in zip(subinfos,subids)]



# Check plots
 
 
plt.figure('delay and error accordance',(8,9))
plt.subplot(3,1,1)
plt.scatter(sub_td,d3cs_td,c=cmap,norm=mpt.colors.LogNorm(),vmin=0.01,vmax=10)
plt.colorbar().set_label(r'pycs-d3cs_tdsep_in_d3cs_errs', labelpad=-55, y=0.5,fontsize=10)
plt.xlabel('submission_td')
plt.ylabel('d3cs_td')

plt.subplot(3,1,2)
plt.scatter(sub_reltderr,d3cs_reltderr,c=cmap,norm=mpt.colors.LogNorm(),vmin=0.01,vmax=10)
plt.colorbar().set_label(r'pycs-d3cs_tdsep_in_d3cs_errs', labelpad=-55, y=0.5,fontsize=10)
plt.xlabel('submission_reltderr')
plt.ylabel('d3cs_reltderr')

plt.subplot(3,1,3)
plt.hist(sub_reltderr,histtype='step',range=(0,2),bins=20,color='indigo',linewidth=1.5)
plt.axvline(np.median(sub_reltderr),color='indigo',linestyle='dashed',linewidth=2,label='median : %.2f'%np.median(sub_reltderr))
plt.legend()
plt.xlabel('d3cs_reltderr')
plt.ylabel('#')
plt.annotate('%s estimations' %len(sub_reltderr),xy=[0.7,0.5],xycoords='axes fraction')


# and save the plot
#plt.show()
plt.savefig(os.path.join(dirpath,'checksub_%s.png' %subname))
print "Saved", os.path.join(dirpath,'checksub_%s.png' %subname)
os.system('cp check_submission.py %s' %os.path.join(dirpath,'check_submission_%s.py' %subname))


