#!/usr/bin/env python

import pycs
import matplotlib.pyplot as plt
import os,sys
import numpy as np


from matplotlib import rcParams
db = pycs.gen.util.readpickle('dbwithout10days.pkl').values()
db = [entry for entry in db if entry["in_tdc1"] == 1]



if 0:
	# plot fraction of catastrophic errors vs ncurves, sigma as colorbar
	fig = plt.figure(figsize=(15,6))
	ax1 = fig.add_subplot(121)
	ax2 = fig.add_subplot(122)
	plt.subplots_adjust(left=0.06, right=0.9, top=0.96, bottom=0.1, wspace=0.12)

	for tick in ax1.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax1.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	for tick in ax2.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax2.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	method = "all-7"
	maxsigma = 3.5
	sigmas = np.linspace(0,max([entry["%s_perseasons_sum_sigresid" %method] for entry in db]),500)

	# We cap the colorbar
	sigmas_caped = []
	for sigma in sigmas:
		if sigma < maxsigma:
			sigmas_caped.append(sigma)
		else:
			sigmas_caped.append(maxsigma)

	#sigmas = np.linspace(0,3,500)

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
	ax1.plot(dblengths,errfrac_auto,color="black",linewidth=3,label='Crude-all',alpha=1)
	ax2.plot(dblengths,errfrac_auto,color="black",linewidth=3,label='Crude-all',alpha=1)
	sc = ax1.scatter(dblengths,errfrac_auto,s=220,c=sigmas_caped,lw=0)
	ax2.scatter(dblengths,errfrac_auto,s=220,c=sigmas_caped,lw=0)

	def addcurvetoplot(db,color,marker,label):

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
		ax1.plot(dblengths,errfrac_auto,color=color, ls=marker, linewidth=3,label=label,alpha=1)
		ax1.scatter(dblengths,errfrac_auto,s=220,c=sigmas_caped,lw=0)
		ax2.plot(dblengths,errfrac_auto,color=color, ls=marker, linewidth=3,label=label,alpha=1)
		ax2.scatter(dblengths,errfrac_auto,s=220,c=sigmas_caped,lw=0)

	dbmod = [entry for entry in db if len([minresid for minresid in entry["%s_perseasons_sum_minsigresids" %method] if minresid > 1 ]) < 2]
	addcurvetoplot(dbmod,color='black', marker='--', label='Crude-nmin-2')

	dbmod = [entry for entry in db if entry["%s_perseasons_sum_sigmag" %method] < 1.5] #== min(entry["%s_perseasons_sum_minsigmags" %method])]
	addcurvetoplot(dbmod,color='black', marker='-.', label=r'Crude-$\xi$-1.5')




	# add d3cs values
	diffdou = 0
	dbdou = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-dou-full_td" in entry]
	for entry in dbdou:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-dou-full_td"])>20:
			diffdou += 1
	ax1.scatter((len(dbdou)),float(diffdou)/len(dbdou)*100,s=350,c='blue',marker='d',label='D3CS-dou(%i)' %len(dbdou))
	ax2.scatter((len(dbdou)),float(diffdou)/len(dbdou)*100,s=350,c='blue',marker='d',label='D3CS-dou(%i)' %len(dbdou))

	diffdoupla = 0
	dbdoupla = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]
	for entry in dbdoupla:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>20:
			diffdoupla += 1
	ax1.scatter((len(dbdoupla)),float(diffdoupla)/len(dbdoupla)*100,s=350,c='green',marker='d',label='D3CS-doupla(%i)' %len(dbdoupla))
	ax2.scatter((len(dbdoupla)),float(diffdoupla)/len(dbdoupla)*100,s=350,c='green',marker='d',label='D3CS-doupla(%i)' %len(dbdoupla))


	diffdouplamul = 0
	dbdouplamul = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry]
	for entry in dbdouplamul:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
			diffdouplamul += 1
	ax1.scatter((len(dbdouplamul)),float(diffdouplamul)/len(dbdouplamul)*100,s=350,c='yellow',marker='d',label='D3CS-douplamul(%i)' %len(dbdouplamul))
	ax2.scatter((len(dbdouplamul)),float(diffdouplamul)/len(dbdouplamul)*100,s=350,c='yellow',marker='d',label='D3CS-douplamul(%i)' %len(dbdouplamul))

	diffall = 0
	for entry in db:
		if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
			if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
				diffall +=1
		else:
			diffall +=1
	ax1.scatter((len(db)),float(diffall)/len(db)*100,s=350,c='red',marker='d',label='D3CS-all(%i)' %len(db))
	ax2.scatter((len(db)),float(diffall)/len(db)*100,s=350,c='red',marker='d',label='D3CS-all(%i)' %len(db))


	ax1.set_xlabel("# of estimations", fontsize=15)
	ax1.set_ylabel(r"fraction of catastrophic outliers [$\epsilon$]", fontsize=15)
	ax2.set_xlabel("# of estimations", fontsize=15)
	ax2.set_ylabel(r"fraction of catastrophic outliers [$\epsilon$]", fontsize=15)

	ax1.set_xlim([-20,1000])
	ax1.set_ylim([-0.05,2.5])

	ax2.set_xlim([0000,5000])
	ax2.set_ylim([-0.7,35])

	ax2.plot([0,1000],[2.5,2.5],'r',linewidth=3)
	ax2.plot([1000,1000],[-1,2.5],'r',linewidth=3)

	ax1.legend(scatterpoints=1,loc=2)

	cbaxes = fig.add_axes([0.91, 0.1, 0.03, 0.86])
	cbar = plt.colorbar(sc,cax=cbaxes)
	cbar.set_label(r"depth of absolute minima [$\mu$]", fontsize=15)
	cbar.ax.tick_params(labelsize=15)

	plt.show()
	sys.exit()




if 0:

	# plot fraction of catastrophic errors vs ncurves, sigma as colorbar, ONLY RIGHT PANEL !!
	fig = plt.figure(figsize=(8,6))
	ax2 = fig.add_subplot(111)
	plt.subplots_adjust(left=0.1, right=0.85, top=0.96, bottom=0.1, wspace=0.12)


	for tick in ax2.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax2.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	method = "all-7"
	maxsigma = 3.5
	sigmas = np.linspace(0,max([entry["%s_perseasons_sum_sigresid" %method] for entry in db]),500)

	# We cap the colorbar
	sigmas_caped = []
	for sigma in sigmas:
		if sigma < maxsigma:
			sigmas_caped.append(sigma)
		else:
			sigmas_caped.append(maxsigma)

	#sigmas = np.linspace(0,3,500)

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
	ax2.plot(dblengths,errfrac_auto,color="black",linewidth=3,label='Crude-all',alpha=1)
	sc = ax2.scatter(dblengths,errfrac_auto,s=220,c=sigmas_caped,lw=1, edgecolor="none")
	ax2.scatter(dblengths,errfrac_auto,s=220,c=sigmas_caped,lw=1, edgecolor='none')

	def addcurvetoplot(db,color,marker,label):

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
		ax2.plot(dblengths,errfrac_auto,color=color, ls=marker, linewidth=3,label=label,alpha=1)
		ax2.scatter(dblengths,errfrac_auto,s=220,c=sigmas_caped,lw=1, edgecolor='none')

	dbmod = [entry for entry in db if len([minresid for minresid in entry["%s_perseasons_sum_minsigresids" %method] if minresid > 1 ]) < 2]
	addcurvetoplot(dbmod,color='black', marker='--', label='Crude-1min')

	dbmod = [entry for entry in db if entry["%s_perseasons_sum_sigmag" %method] < 1.5] #== min(entry["%s_perseasons_sum_minsigmags" %method])]
	addcurvetoplot(dbmod,color='black', marker='-.', label=r'Crude-1.5$\xi$')




	# add d3cs values
	diffdou = 0
	dbdou = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-dou-full_td" in entry]
	for entry in dbdou:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-dou-full_td"])>20:
			diffdou += 1
	ax2.scatter((len(dbdou)),float(diffdou)/len(dbdou)*100,s=350,c='blue',marker='d',label='D3CS-sec (%i)' %len(dbdou))

	diffdoupla = 0
	dbdoupla = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]
	for entry in dbdoupla:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>20:
			diffdoupla += 1
	ax2.scatter((len(dbdoupla)),float(diffdoupla)/len(dbdoupla)*100,s=350,c='green',marker='d',label='D3CS-secpla (%i)' %len(dbdoupla))


	diffdouplamul = 0
	dbdouplamul = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry]
	for entry in dbdouplamul:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
			diffdouplamul += 1
	ax2.scatter((len(dbdouplamul)),float(diffdouplamul)/len(dbdouplamul)*100,s=350,c='yellow',marker='d',label='D3CS-secplamul (%i)' %len(dbdouplamul))

	diffall = 0
	for entry in db:
		if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
			if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
				diffall +=1
		else:
			diffall +=1
	ax2.scatter((len(db)),float(diffall)/len(db)*100,s=350,c='red',marker='d',label='D3CS-all (%i)' %len(db))

	ax2.set_xlim([0000,5200])
	ax2.set_ylim([-0.7,35])

	ax2.set_xlabel("Number Of Estimations", fontsize=15)
	ax2.legend(scatterpoints=1,loc=2)

	cbaxes = fig.add_axes([0.86, 0.1, 0.03, 0.86])
	cbar = plt.colorbar(sc,cax=cbaxes)
	cbar.ax.tick_params(labelsize=15)

	# Special mathtext behaviour
	rcParams['mathtext.default'] = 'regular'
	rcParams['text.usetex']=True
	ax2.set_ylabel(r"Fraction Of Catastrophic Outliers {\huge $\epsilon$}", fontsize=15)
	cbar.set_label(r"Depth Of Absolute Minima {\huge $\mu$}", fontsize=15)


	plt.show()
	sys.exit()


if 0:
	# plot NUMBER of catastrophic errors vs ncurves, sigma as colorbar
	fig = plt.figure(figsize=(15,6))
	ax1 = fig.add_subplot(121)
	ax2 = fig.add_subplot(122)
	plt.subplots_adjust(left=0.06, right=0.9, top=0.96, bottom=0.1, wspace=0.12)

	for tick in ax1.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax1.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	for tick in ax2.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax2.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	method = "all-7"
	maxsigma = 3.5
	sigmas = np.linspace(0,max([entry["%s_perseasons_sum_sigresid" %method] for entry in db]),500)

	# We cap the colorbar
	sigmas_caped = []
	for sigma in sigmas:
		if sigma < maxsigma:
			sigmas_caped.append(sigma)
		else:
			sigmas_caped.append(maxsigma)

	#sigmas = np.linspace(0,3,500)

	errnb_auto = []
	errnb_d3cs = []
	dblengths = []
	for sigma in sigmas:
		diffsum = 0
		dbnew = [entry for entry in db if entry["%s_perseasons_sum_sigresid" %method] >= sigma] #and entry["%s_crude_nmin" %method] < 2 and entry["%s_perseasons_sum_stdmag" %method] < 0.01]
		for entry in dbnew:
			if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
				diffsum +=1

		errnb_auto.append(float(diffsum))
		dblengths.append(len(dbnew))
	ax1.plot(dblengths,errnb_auto,color="black",linewidth=3,label='Crude-all',alpha=1)
	ax2.plot(dblengths,errnb_auto,color="black",linewidth=3,label='Crude-all',alpha=1)
	sc = ax1.scatter(dblengths,errnb_auto,s=220,c=sigmas_caped,lw=0)
	ax2.scatter(dblengths,errnb_auto,s=220,c=sigmas_caped,lw=0)

	def addcurvetoplot(db,color,marker,label):

		errnb_auto = []
		dblengths = []
		for sigma in sigmas:
			diffsum = 0
			dbnew = [entry for entry in db if entry["%s_perseasons_sum_sigresid" %method] >= sigma] #and entry["%s_crude_nmin" %method] < 2 and entry["%s_perseasons_sum_stdmag" %method] < 0.01]
			for entry in dbnew:
				if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
					diffsum +=1

			errnb_auto.append(float(float(diffsum)))
			dblengths.append(len(dbnew))
		ax1.plot(dblengths,errnb_auto,color=color, ls=marker, linewidth=3,label=label,alpha=1)
		ax1.scatter(dblengths,errnb_auto,s=220,c=sigmas_caped,lw=0)
		ax2.plot(dblengths,errnb_auto,color=color, ls=marker, linewidth=3,label=label,alpha=1)
		ax2.scatter(dblengths,errnb_auto,s=220,c=sigmas_caped,lw=0)

	dbmod = [entry for entry in db if len([minresid for minresid in entry["%s_perseasons_sum_minsigresids" %method] if minresid > 1 ]) < 2]
	addcurvetoplot(dbmod,color='black', marker='--', label='Crude-nmin-2')

	dbmod = [entry for entry in db if entry["%s_perseasons_sum_sigmag" %method] < 1.5] #== min(entry["%s_perseasons_sum_minsigmags" %method])]
	addcurvetoplot(dbmod,color='black', marker='-.', label='Crude-sigmag-1.5')




	# add d3cs values
	diffdou = 0
	dbdou = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-dou-full_td" in entry]
	for entry in dbdou:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-dou-full_td"])>20:
			diffdou += 1
	ax1.scatter((len(dbdou)),float(diffdou),s=350,c='blue',marker='d',label='D3CS-dou(%i)' %len(dbdou))
	ax2.scatter((len(dbdou)),float(diffdou),s=350,c='blue',marker='d',label='D3CS-dou(%i)' %len(dbdou))

	diffdoupla = 0
	dbdoupla = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]
	for entry in dbdoupla:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>20:
			diffdoupla += 1
	ax1.scatter((len(dbdoupla)),float(diffdoupla),s=350,c='green',marker='d',label='D3CS-doupla(%i)' %len(dbdoupla))
	ax2.scatter((len(dbdoupla)),float(diffdoupla),s=350,c='green',marker='d',label='D3CS-doupla(%i)' %len(dbdoupla))


	diffdouplamul = 0
	dbdouplamul = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry]
	for entry in dbdouplamul:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
			diffdouplamul += 1
	ax1.scatter((len(dbdouplamul)),float(diffdouplamul),s=350,c='yellow',marker='d',label='D3CS-douplamul(%i)' %len(dbdouplamul))
	ax2.scatter((len(dbdouplamul)),float(diffdouplamul),s=350,c='yellow',marker='d',label='D3CS-douplamul(%i)' %len(dbdouplamul))

	diffall = 0
	for entry in db:
		if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
			if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
				diffall +=1
		else:
			diffall +=1
	ax1.scatter((len(db)),float(diffall),s=350,c='red',marker='d',label='D3CS-all(%i)' %len(db))
	ax2.scatter((len(db)),float(diffall),s=350,c='red',marker='d',label='D3CS-all(%i)' %len(db))


	ax1.set_xlabel("# of curves", fontsize=15)
	ax1.set_ylabel(r"fraction of catastrophic outliers [$\epsilon$]", fontsize=15)
	ax2.set_xlabel("# of curves", fontsize=15)
	ax2.set_ylabel(r"fraction of catastrophic outliers [$\epsilon$]", fontsize=15)

	ax1.set_xlim([-20,1000])
	ax1.set_ylim([-0.1,15])

	ax2.set_xlim([1000,5000])
	ax2.set_ylim([0,1300])

	ax2.legend(scatterpoints=1,loc=2)

	cbaxes = fig.add_axes([0.91, 0.1, 0.03, 0.86])
	cbar = plt.colorbar(sc,cax=cbaxes)
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
