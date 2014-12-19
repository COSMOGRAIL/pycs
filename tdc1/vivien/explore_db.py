import pycs
import matplotlib.pyplot as plt
import os,sys
import numpy as np


db = pycs.gen.util.readpickle('db.pkl').values()
db = [entry for entry in db if entry["in_tdc1"] == 1]

if 1:
	# plot fraction of catastrophic errors vs ncurves, sigma as colorbar
	fig = plt.figure(figsize=(8,6))
	ax1 = fig.add_subplot(111)
	plt.subplots_adjust(left=0.085, right=0.87, top=0.96, bottom=0.1)

	for tick in ax1.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax1.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	method = "all-7"
	sigmas = np.linspace(0,max([entry["%s_perseasons_sum_sigresid" %method] for entry in db]),500)


	errfrac_auto = []
	errfrac_d3cs = []
	dblengths = []
	for sigma in sigmas:
		diffsum = 0
		dbnew = [entry for entry in db if entry["%s_perseasons_sum_sigresid" %method] >= sigma] #and entry["%s_crude_nmin" %method] < 2 and entry["%s_perseasons_sum_stdmag" %method] < 0.01]
		for entry in dbnew:
			if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
				diffsum +=1

		errfrac_auto.append(float(float(diffsum)/(len(dbnew)+0.001)*100))
		dblengths.append(len(dbnew))
	ax1.plot(dblengths,errfrac_auto,color="black",linewidth=2.5,label='Crude-all',alpha=1)
	sc = ax1.scatter(dblengths,errfrac_auto,s=100,c=sigmas,lw=0)


	def addcurvetoplot(db,color,label):

		errfrac_auto = []
		dblengths = []
		for sigma in sigmas:
			diffsum = 0
			dbnew = [entry for entry in db if entry["%s_perseasons_sum_sigresid" %method] >= sigma] #and entry["%s_crude_nmin" %method] < 2 and entry["%s_perseasons_sum_stdmag" %method] < 0.01]
			for entry in dbnew:
				if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
					diffsum +=1

			errfrac_auto.append(float(float(diffsum)/(len(dbnew)+0.001)*100))
			dblengths.append(len(dbnew))
		ax1.plot(dblengths,errfrac_auto,color=color,linewidth=3,label=label,alpha=1)
		ax1.scatter(dblengths,errfrac_auto,s=150,c=sigmas,lw=0)


	dbmod = [entry for entry in db if len([minresid for minresid in entry["%s_perseasons_sum_minsigresids" %method] if minresid > 1 ]) < 2]
	addcurvetoplot(dbmod,color='crimson',label='Crude-nmin-2')

	dbmod = [entry for entry in db if entry["%s_perseasons_sum_sigmag" %method] < 1.5] #== min(entry["%s_perseasons_sum_minsigmags" %method])]
	addcurvetoplot(dbmod,color='gold',label='Crude-sigmag-1.5')




	# add d3cs values
	diffdou = 0
	dbdou = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-dou-full_td" in entry]
	for entry in dbdou:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-dou-full_td"])>20:
			diffdou += 1
	ax1.scatter((len(dbdou)),float(diffdou)/len(dbdou)*100,s=350,c='blue',marker='d',label='D3CS-dou(%i)' %len(dbdou))

	diffdoupla = 0
	dbdoupla = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]
	for entry in dbdoupla:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>20:
			diffdoupla += 1
	ax1.scatter((len(dbdoupla)),float(diffdoupla)/len(dbdoupla)*100,s=350,c='green',marker='d',label='D3CS-doupla(%i)' %len(dbdoupla))


	diffdouplamul = 0
	dbdouplamul = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry]
	for entry in dbdouplamul:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
			diffdouplamul += 1
	ax1.scatter((len(dbdouplamul)),float(diffdouplamul)/len(dbdouplamul)*100,s=350,c='yellow',marker='d',label='D3CS-douplamul(%i)' %len(dbdouplamul))

	diffall = 0
	for entry in db:
		if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
			if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
				diffall +=1
		else:
			diffall +=1
	ax1.scatter((len(db)),float(diffall)/len(db)*100,s=350,c='red',marker='d',label='D3CS-all(%i)' %len(db))


	ax1.set_xlabel("# of curves", fontsize=15)
	ax1.set_ylabel(r"fraction of catastrophic outliers [$\nu$]", fontsize=15)


	plt.legend(scatterpoints=1,loc=2)

	cbaxes = fig.add_axes([0.88, 0.1, 0.03, 0.86])
	cbar = plt.colorbar(sc,cax =cbaxes)
	cbar.set_label(r"depth of absolute minima [$\mu$]", fontsize=15)
	cbar.ax.tick_params(labelsize=15)

	plt.show()
	sys.exit()






"""# plot fraction of catastrophic errors vs sigma
fig = plt.figure()
ax1 = fig.add_subplot(111)
for tick in ax1.xaxis.get_major_ticks():
	tick.label.set_fontsize(15)
for tick in ax1.yaxis.get_major_ticks():
	tick.label.set_fontsize(15)

method = "all-7"
sigmas = np.linspace(0,max([entry["%s_perseasons_sum_sigresid" %method] for entry in db]),500)

# No special selection
errfrac_auto = []
errfrac_d3cs = []
dblengths = []
for sigma in sigmas:
	diffsum = 0
	dbnew = [entry for entry in db if entry["%s_perseasons_sum_sigresid" %method] >= sigma] #and entry["%s_crude_nmin" %method] < 2 and entry["%s_perseasons_sum_stdmag" %method] < 0.01]
	for entry in dbnew:
		if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
			diffsum +=1

	errfrac_auto.append(float(float(diffsum)/(len(dbnew)+0.001)*100))
	dblengths.append(len(dbnew))
ax1.plot(sigmas,errfrac_auto,color="chartreuse",linewidth=4,label='Crude Estimator')


# Only one minimum
errfrac_auto = []
errfrac_d3cs = []
dblengths = []
for sigma in sigmas:
	diffsum = 0
	dbnew = [entry for entry in db if entry["%s_perseasons_sum_sigresid" %method] >= sigma ] #and entry["%s_crude_nmin" %method] < 2 and entry["%s_perseasons_sum_stdmag" %method] < 0.01]
	for entry in dbnew:
		if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20 and entry["%s_crude_nmin" %method] < 2:
			diffsum +=1

	errfrac_auto.append(float(float(diffsum)/(len(dbnew)+0.001)*100))
	dblengths.append(len(dbnew))
ax1.plot(sigmas,errfrac_auto,color="crimson",linewidth=4,label='Crude Estimator')


# add d3cs values

def getposonsigmaaxis(npairs):
	val =  min(dblengths, key=lambda dblength: abs(dblength-npairs))
	return sigmas[dblengths.index(val)]

diffdou = 0
dbdou = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-dou-full_td" in entry]
for entry in dbdou:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-dou-full_td"])>20:
		diffdou += 1
ax1.scatter(getposonsigmaaxis(len(dbdou)),float(diffdou)/len(dbdou)*100,s=350,c='blue',marker='d',label='D3CS-dou(%i)' %len(dbdou))

diffdoupla = 0
dbdoupla = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]
for entry in dbdoupla:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>20:
		diffdoupla += 1
ax1.scatter(getposonsigmaaxis(len(dbdoupla)),float(diffdoupla)/len(dbdoupla)*100,s=350,c='green',marker='d',label='D3CS-doupla(%i)' %len(dbdoupla))


diffdouplamul = 0
dbdouplamul = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry]
for entry in dbdouplamul:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
		diffdouplamul += 1
ax1.scatter(getposonsigmaaxis(len(dbdouplamul)),float(diffdouplamul)/len(dbdouplamul)*100,s=350,c='yellow',marker='d',label='D3CS-douplamul(%i)' %len(dbdouplamul))

diffall = 0
for entry in db:
	if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
			diffall +=1
	else:
		diffall +=1
ax1.scatter(getposonsigmaaxis(len(db)),float(diffall)/len(db)*100,s=350,c='red',marker='d',label='D3CS-all(%i)' %len(db))


for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
	label.set_fontname('Arial')
	label.set_fontsize(15)
ax1.set_xlabel("sigma", fontsize=15)
ax1.set_ylabel("critical failures [%]", fontsize=15)
ax1.legend(scatterpoints=1)
from matplotlib.ticker import MaxNLocator
ax1.xaxis.set_major_locator(MaxNLocator(8))

ax1xs = ax1.get_xticks()
ax2xs = []
for x in ax1xs:
	val = min(sigmas, key=lambda sigma:abs(sigma-x))
	ax2xs.append(dblengths[np.where(sigmas == val)[0]])
ax2 = ax1.twiny()
ax2.set_xticks(ax1.get_xticks())
ax2.set_xticklabels(ax2xs)
ax2.set_xlabel('number of pairs', fontsize=15)
for tick in ax2.xaxis.get_major_ticks():
	tick.label.set_fontsize(15)


plt.show()
sys.exit()
"""


if 0:
	# compute how many catastrophic failures
	method= "all-7"
	#db = [entry for entry in db if entry["%s_crude_sigmabestmin" % method] >= 2]
	db = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]


	print "length of database:", len(db)


	diffalld3cs = 0
	for entry in db:
		if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry:
			if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>50 and abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>50:
				if abs(entry["%s_perseasons_sum_td" %method]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"]) < 20:
					diffalld3cs += 1
		else:
			if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
				diffalld3cs += 0

	print "combined failure: ", diffalld3cs/float(len(db))*100
	print "number", diffalld3cs
	sys.exit()


	diffd3cs = 0
	diffsingleshift = 0
	diffsum = 0
	diffmedian = 0

	d3cs_id = []
	singleshift_id = []
	sum_id =[]
	median_id = []
	allfail_id = []
	for entry in db:
		#print '='*10,entry["id"],'='*10
		#print 'true delay = ',entry["truetd"]
		#print 'singleshift delay = ',entry["singleshift"]
		#print 'perseasons sum delay = ',entry["perseasons_sum"]
		#print 'perseasons median delay = ',entry["perseasons_median"]
		#plt.suptitle("sum")
		#plt.scatter(entry["perseasons_sum_td"],np.log10(entry["perseasons_sum_res"]),c='blue')

		#allfail = 0
		if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
			if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
				diffd3cs +=1
				d3cs_id.append(entry["id"])
		else:
			diffd3cs +=1
		#if abs(entry["truetd"]-entry["%s_singleshift_td" %method])>20:
			#diffsingleshift +=1
			#singleshift_id.append(entry["id"])
			#allfail+=1
		if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
			diffsum +=1
			sum_id.append(entry["id"])
			#allfail+=1
		#if abs(entry["truetd"]-entry["%s_perseasons_median_td" %method])>20:
			#diffmedian +=1
			#median_id.append(entry["id"])
			#allfail+=1

		#if allfail == 3:
			#allfail_id.append(entry["id"])


	print 'd3cs: %.2f'%float(float(diffd3cs)/len(db)*100),"%"
	#print 'singleshift: %.2f'%float(float(diffsingleshift)/len(db)*100),"%"
	print 'sum: %.2f'%float(float(diffsum)/len(db)*100),"%"
	#print 'median: %.2f'%float(float(diffmedian)/len(db)*100),"%"
	#print 'allfail: %.2f' %float(float(len(allfail_id))/len(db)*100),"%"
	#print '='*80
	#print 'MEDIAN',median_id
	#print '='*80
	#print 'SUM',sum_id
	sys.exit()

	### Now, displaying troublemakers:
	todisplay = 'display'
	for pairid in d3cs_id:
		#print pairid
		todisplay +=' %s/%s/plot_res_perseasons_sum.png' %(method, pairid)
		#residuals  = pycs.gen.util.readpickle(os.path.join(workdir,"%s/resids_perseasons_sum.pkl" %pairid))
		#imgpath = os.path.join(workdir, "%s/plot_res_perseasons_sum.png" %pairid)
		#os.system("display %s" %imgpath)
	#pycs.gen.util.writepickle(sum_id,"tempid.pkl")
	os.system(todisplay)
