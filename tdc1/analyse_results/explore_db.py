import pycs
import matplotlib.pyplot as plt
import matplotlib
import os,sys
import numpy as np

"""
Explore the big database built with make_db

Activate/Deactivate blocks using 0 and 1. All block are independent plots.
Do NOT activate multiple plots at the same time !!

"""

# Load database
db = pycs.gen.util.readpickle('db.pkl').values()

# Submissions to analyse
#methods = ['pycs_tdc1_spl-vanilla-dou-full','pycs_tdc1_spl-ml0.5-dou-full','pycs_tdc1_spl-k1.5-dou-full']
#methods = ['pycs_tdc1_spl-vanilla-dou-full','pycs_tdc1_spl-vanilla-dou-P3percent','pycs_tdc1_spl-vanilla-dou-800bestP', 'pycs_tdc1_spl-vanilla-dou-100bestP']
#methods = ['pycs_tdc1_spl-vanilla-dou-full','pycs_tdc1_sdi-vanilla-dou-full','pycs_tdc1_d3cs-vanilla-dou-full']
#methods = ['pycs_tdc1_d3cs-vanilla-douplamul-full','pycs_tdc1_d3cs-vanilla-doupla-full','pycs_tdc1_d3cs-vanilla-dou-full']
methods = ['pycs_tdc1_spl-vanilla-doupla-full',('pycs_tdc1_spl-vanilla-doupla-full',20),'pycs_tdc1_spl-vanilla-dou-full']
#methods = ['Vivien','mtewes','Fred','Thibault','pycs_tdc1_d3cs-vanilla-dou-full']
#methods = ['pycs_tdc1_spl-vanilla-dou-full','pycs_tdc1_sdi-vanilla-dou-full','pycs_tdc1_spl-vanilla-doupla-full','pycs_tdc1_sdi-vanilla-doupla-full']
#methods = ['pycs_tdc1_spl-vanilla-doupla-full','pycs_tdc1_sdi-vanilla-doupla-full','pycs_tdc1_spl-vanilla-dou-full','pycs_tdc1_sdi-vanilla-dou-full']

# Special selection
print "I select items in tdc1 only"
db = [item for item in db if item["in_tdc1"] == 1]


#print "I select items in rung 0 only"
#db = [item for item in db if item["rung"] == 0]

lendb = len(db)


def importmetrics():
	# import metrics values
	metrics = open('metrics.txt').readlines()
	results = []
	for line in metrics:
		if line[0] == '#' or len(line) < 10:
			#print 'I skip the following line:'
			#print line
			#print '='*50
			pwet=0 # woohoo !!
		else:
			try:
				result = {}

				reduced = line.split(' ')
				reduced[-1] = reduced[-1].split('\n')[0]
				reduced = [elt for elt in reduced if elt != '']

				result["team"] = reduced[0]
				result["algorithm"] = reduced[1].split('-bugfix')[0]
				result["rung"] = reduced[2]
				result["f"] = reduced[3]
				result["chi2"] = reduced[4]
				result["chi2err"] = reduced[5]
				result["P"] = reduced[6]
				result["Perr"] = reduced[7]
				result["A"] = reduced[8]
				result["Aerr"] = reduced[9]
				result["X"] = reduced[10]
				result["f-nc"] = reduced[11]
				result["chi2-nc"] = reduced[12]
				result["chi2-ncerr"] = reduced[13]
				result["P-nc"] = reduced[14]
				result["P-ncerr"] = reduced[15]
				result["A-nc"] = reduced[16]
				result["A-ncerr"] = reduced[17]

				results.append(result)

			except:
				print 'Something is wrong with this line:'
				print line
				sys.exit()
	return results




# Plots
if 0:
	# additionnal stuff: sort by XXX
	"""
	possible keywords for sorting:

	vratiomin  / vratiomax
	truth_overlap_epochs
	medmagerrA
	medmagerrB

	"""
	kw = 'vratiomax'

	results = importmetrics()

	print 'I sort everything accorded to %s' %kw
	sorted_db = sorted(db, key=lambda item: item["%s" % kw])

	for method in methods:
		reduced_db = [item for item in sorted_db if "%s_td" %method in item]
		print "I shoot the outliers"
		reduced_db = [item for item in reduced_db if abs(item["%s_td"%method]-item["truetd"]) < 20]


		if 0:
			# display the spline fitting for a given set of curves
			display_ids = [item["id"] for item in reduced_db[:10]]
			todisplay = 'display '
			for id in display_ids:
				todisplay += '../vivien/all-7/%s/spline.png ' %id
			print todisplay
			os.system(todisplay)
			sys.exit()




		#idea: we average over 10 points and plot it in a bin-linear scale --> better visualisation of the behaviour

		npts = len(reduced_db)
		binlen = 10
		nbins = npts/binlen
		xs=[]
		Ps=[]
		As=[]
		chi2s=[]
		tds=[]
		tderrs=[]
		for nbin in np.arange(nbins+1):
			items = reduced_db[nbin*10:(nbin*10)+10]
			xs.append(np.mean([item["%s" %kw] for item in items]))
			Ps.append(np.mean([item["%s_P" %method] for item in items]))
			As.append(np.mean([item["%s_A" %method] for item in items]))
			chi2s.append(np.mean([item["%s_chi2" %method] for item in items]))
			tds.append(np.mean([abs(float(item["%s_td" %method])-float(item["truetd"])) for item in items]))
			tderrs.append(np.mean([item["%s_tderr" %method] for item in items]))

		plt.figure('%s' %method)
		plt.suptitle('evolution with %s' %kw)
		plt.subplot(611)
		plt.plot(Ps)
		plt.axhline(np.median(Ps),color='black', linewidth=3, alpha=0.5)
		plt.axhline(pycs.tdc.metrics.getP(reduced_db,method),color='red', linewidth=3, alpha=0.5)
		plt.ylabel('P')
		plt.subplot(612)
		plt.plot(As)
		plt.axhline(np.median(As),color='black', linewidth=3, alpha=0.5)
		plt.axhline(pycs.tdc.metrics.getA(reduced_db,method),color='red', linewidth=3, alpha=0.5)
		plt.ylabel('A')
		plt.subplot(613)
		plt.plot(chi2s)
		plt.axhline(np.median(chi2s),color='black', linewidth=3, alpha=0.5)
		plt.axhline(pycs.tdc.metrics.getchi2(reduced_db,method),color='red', linewidth=3, alpha=0.5)
		plt.ylabel('chi2')
		plt.subplot(614)
		plt.plot(tds)
		plt.axhline(np.median(tds),color='black', linewidth=3, alpha=0.5)
		plt.ylabel('Time delay error')
		plt.subplot(615)
		plt.plot(tderrs)
		plt.axhline(np.median(tderrs),color='black', linewidth=3, alpha=0.5)
		plt.ylabel('errorbar')
		plt.subplot(616)
		plt.plot(xs)
		plt.ylabel('%s' %kw)

	plt.show()




if 0:
	"""
	Print/Plot submissions final values, from metrics.txt, version 2
	"""

	import matplotlib.gridspec as gridspec

	fig = plt.figure(figsize=(15,10))
	gs1 = gridspec.GridSpec(3, 3)
	gs1.update(left=0.07, right=0.98, top=0.95, bottom=0.45, wspace=0.2,hspace=0.01)

	gs2 = gridspec.GridSpec(1,3)
	gs2.update(left=0.07, right=0.98, top=0.37, bottom=0.09, wspace=0.2,hspace=0.03)

	matplotlib.rcParams.update({'font.size': 15})

	ax1 = fig.add_subplot(gs1[0:3,0])
	ax2 = fig.add_subplot(gs1[1,1])
	ax2s = fig.add_subplot(gs1[2,1])
	ax2t = fig.add_subplot(gs1[0,1])
	ax3 = fig.add_subplot(gs1[1,2])
	ax3s = fig.add_subplot(gs1[2,2])
	ax3t = fig.add_subplot(gs1[0,2])

	ax1b = fig.add_subplot(gs2[0,0])
	ax2b = fig.add_subplot(gs2[0,1])
	ax3b = fig.add_subplot(gs2[0,2])

	rungs = [0, 1, 2, 3, 4]
	colors = ['blue', 'green','crimson','gold']
	markers = ['o', '*', 'd', '^', '<']

	# import metrics values
	metrics = open('metrics.txt').readlines()
	results = []
	for line in metrics:
		if line[0] == '#' or len(line) < 10:
			#print 'I skip the following line:'
			#print line
			#print '='*50
			pwet=0 # woohoo !!
		else:
			try:
				result = {}

				reduced = line.split(' ')
				reduced[-1] = reduced[-1].split('\n')[0]
				reduced = [elt for elt in reduced if elt != '']

				result["team"] = reduced[0]
				result["algorithm"] = reduced[1].split('-bugfix')[0]
				result["rung"] = reduced[2]
				result["f"] = reduced[3]
				result["chi2"] = reduced[4]
				result["chi2err"] = reduced[5]
				result["P"] = reduced[6]
				result["Perr"] = reduced[7]
				result["A"] = reduced[8]
				result["Aerr"] = reduced[9]
				result["X"] = reduced[10]
				result["f-nc"] = reduced[11]
				result["chi2-nc"] = reduced[12]
				result["chi2-ncerr"] = reduced[13]
				result["P-nc"] = reduced[14]
				result["P-ncerr"] = reduced[15]
				result["A-nc"] = reduced[16]
				result["A-ncerr"] = reduced[17]

				results.append(result)

			except:
				print 'Something is wrong with this line:'
				print line
				sys.exit()


	for method, color in zip(methods, colors):
		for rung, marker in zip(rungs[::-1], markers[::-1]):

			dbnew = [item for item in db if item["rung"] == rung]
			#dbnew = db
			result = [result for result in results if result["algorithm"] == str(method) and result["rung"] == str(rung)][0]

			f = pycs.tdc.metrics.getf(dbnew, method, len(dbnew))
			P = pycs.tdc.metrics.getP(dbnew, method)
			Pm, Pmerr = (float(result["P"]), float(result["Perr"]))
			A = pycs.tdc.metrics.getA(dbnew, method)
			Am, Amerr = (float(result["A"]), float(result["Aerr"]))
			chi2 = pycs.tdc.metrics.getchi2(dbnew, method)
			chi2m, chi2merr = (float(result["chi2"]), float(result["chi2err"]))

			# print section, check we got more or less the same than metrics.txt

			print "*"*4, method, 'rung', rung, '*'*4
			"""
			print 'f: ', f
			print 'P: ', P,
			print 'A: ', A
			print 'chi2: ', chi2
			"""
			print '*'*10
			print 'Pm: ', Pm,Pmerr
			print 'Am: ', Am,Amerr
			print 'chi2m: ', chi2m,chi2merr

			#print 'Pdiff: ', Pm-P
			#print 'Adiff: ', Am-A
			#print 'chi2diff: ', chi2m-chi2


			# plot it !

			skwargs = {'color': 'black', 'marker': marker, 's': 200, 'lw':1.5, 'facecolor': color, 'alpha':0.8}
			lkwargs = {'color': 'black', 'lw': 2.5, 'alpha': 0.5}
			ekwargs = {'color': color, 'linewidth': 2}

			Pmin = 0
			Pmax = 0.03
			Amin = -0.03
			Amax = 0.03
			chi2min = 0.5
			chi2max = 1.5

			if method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-dou-full':
				ax1.errorbar(Pm,Am,xerr=Pmerr, yerr=Amerr, **ekwargs)
			ax1.scatter(Pm, Am, **skwargs)
			ax1.set_xlabel(r'$P$',fontsize=20)
			ax1.set_ylabel(r'$A$',fontsize=20)
			ax1.set_xlim(0,0.18)
			ax1.axhspan(Amin, Amax, facecolor='grey', alpha=0.01)
			ax1.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
			ax1.set_ylim(-0.02,0.02)

			if not method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full':
				ax1b.errorbar(Pm,Am,xerr=Pmerr, yerr=Amerr, **ekwargs)
				ax1b.scatter(Pm, Am, **skwargs)
				ax1b.set_xlabel(r'$P$',fontsize=20)
				ax1b.set_ylabel(r'$A$',fontsize=20, labelpad=-8)
				ax1b.set_xlim(0.025, 0.0483)
				ax1b.axhspan(Amin, Amax, facecolor='grey', alpha=0.01)
				ax1b.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
				ax1b.set_ylim(-0.0063,0.0042)


			# middle panel
			if method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full':
				ax2.errorbar(Pm,chi2m,xerr=Pmerr, yerr=chi2merr, **ekwargs)
			ax2.scatter(Pm, chi2m, **skwargs)
			ax2.set_xlabel(r'$P$',fontsize=20)
			ax2.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax2.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
			ax2.set_xlim(0,0.18)
			ax2.set_ylim(2.5,10)
			ax2.get_xaxis().set_visible(False)

			# bottom panel
			if method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-dou-full':
				ax2s.errorbar(Pm,chi2m,xerr=Pmerr, yerr=chi2merr, **ekwargs)
			ax2s.scatter(Pm, chi2m, **skwargs)
			ax2s.set_xlabel(r'$P$',fontsize=20)
			ax2s.set_ylabel(r'$\chi^2$', fontsize=20, y=1.5)
			ax2s.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax2s.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
			ax2s.set_xlim(0,0.18)
			ax2s.set_ylim(0,2)

			# top panel
			if method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full':
				ax2t.errorbar(Pm,chi2m,xerr=Pmerr, yerr=chi2merr, **ekwargs)
			ax2t.scatter(Pm, chi2m, **skwargs)
			ax2t.set_xlabel(r'$P$', fontsize=20)
			ax2t.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax2t.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
			ax2t.set_xlim(0, 0.18)
			ax2t.set_ylim(10, 45)
			ax2t.get_xaxis().set_visible(False)
			ax2t.set_yticks([20, 30, 40])

			if not method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full':
				ax2b.errorbar(Pm,chi2m,xerr=Pmerr, yerr=chi2merr, **ekwargs)
				ax2b.scatter(Pm, chi2m, **skwargs)
				ax2b.set_xlabel(r'$P$',fontsize=20)
				ax2b.set_ylabel(r'$\chi^2$', fontsize=20)
				ax2b.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
				ax2b.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
				ax2b.set_xlim(0.025, 0.0483)
				ax2b.set_ylim(0.385, 0.74)




			# middle panel
			if method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full':
				ax3.errorbar(Am,chi2m,xerr=Amerr, yerr=chi2merr, **ekwargs)
			ax3.scatter(Am, chi2m, **skwargs)
			ax3.set_xlabel(r'$A$',fontsize=20)
			ax3.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax3.axvspan(Amin, Amax, facecolor='grey', alpha=0.01)
			ax3.set_xlim(-0.02, 0.02)
			ax3.set_ylim(2.5, 10)
			ax3.get_xaxis().set_visible(False)

			# bottom panel
			if method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-dou-full':
				ax3s.errorbar(Am,chi2m,xerr=Amerr, yerr=chi2merr, **ekwargs)
			ax3s.scatter(Am, chi2m, **skwargs)
			ax3s.set_xlabel(r'$A$',fontsize=20)
			ax3s.set_ylabel(r'$\chi^2$', fontsize=20, y=1.5)
			ax3s.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax3s.axvspan(Amin, Amax, facecolor='grey', alpha=0.01)
			ax3s.set_ylim(0, 2)
			ax3s.set_xlim(-0.02, 0.02)
			ax3t.set_yticks([20, 30, 40])

			# top panel
			if method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full':
				ax3t.errorbar(Am,chi2m,xerr=Amerr, yerr=chi2merr, **ekwargs)
			ax3t.scatter(Am, chi2m, **skwargs)
			ax3t.set_xlabel(r'$A$',fontsize=20)
			ax3t.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax3t.axvspan(Amin, Amax, facecolor='grey', alpha=0.01)
			ax3t.set_ylim(10, 45)
			ax3t.set_xlim(-0.02, 0.02)
			ax3t.get_xaxis().set_visible(False)


			if not method == 'pycs_tdc1_spl-vanilla-doupla-full' or method == 'pycs_tdc1_sdi-vanilla-doupla-full':
				ax3b.errorbar(Am,chi2m,xerr=Amerr, yerr=chi2merr, **ekwargs)
				ax3b.scatter(Am, chi2m, **skwargs)
				ax3b.set_xlabel(r'$A$',fontsize=20)
				ax3b.set_ylabel(r'$\chi^2$', fontsize=20)
				ax3b.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
				ax3b.axvspan(Amin, Amax, facecolor='grey', alpha=0.01)
				ax3b.set_ylim(0.385, 0.74)
				ax3b.set_xlim(-0.0063, 0.0042)


			from matplotlib.ticker import MaxNLocator
			for ax in [ax1,ax2,ax3,ax2s,ax3s,ax1b,ax2b,ax3b]:
				ax.xaxis.set_major_locator(MaxNLocator(4))
				ax.yaxis.set_major_locator(MaxNLocator(4))

	for method, color in zip(methods, colors):
		methodreduc = method.split('_')[-1].split('-')[0]+'-'+method.split('_')[-1].split('-')[2]
		ax3t.plot([],[],lw=10,label=methodreduc,color=color,alpha=0.8)

	#for rung, marker in zip(rungs, markers)[0:0]:
		#ax2.scatter([],[],label='rung'+str(rung),color='grey',marker=marker,s=200,lw=1)
	for rung, marker in zip(rungs, markers)[0:]:
		ax1.scatter([],[],label='rung'+str(rung),color='grey',marker=marker,s=200,lw=1)

	ax1.legend(scatterpoints=1, framealpha=0)
	#ax2.legend(scatterpoints=1)
	ax3t.legend(scatterpoints=1, framealpha=0)
	#ax1.plot([1,2],[1,2])
	plt.show()


if 0:
	"""
	plot outliers values
	"""

	db = [item for item in db if "%s_P" %methods[0] in item and abs(item["%s_td" %methods[0]]-item["truetd"]) > 20]
	db = sorted(db, key = lambda item: item["%s_chi2" % methods[0]] )[::-1]
	print len(db)
	for item in db:
		print item["rung"],item["pair"],'    ',item["%s_td" %methods[0]],item["truetd"]
		print '          ',item["%s_td" %methods[0]]-item["truetd"],item["%s_chi2" %methods[0]]



if 0:
	"""
	histogramm of metrics distribution
	"""
	UserMs = []
	for method in methods:
		Ms = [item['%s_chi2'%method] for item in db if '%s_chi2' %method in item]
		UserMs.append(Ms)
		plt.figure()
		print '%s '%method,sum(Ms)/len(Ms)
		print 'Mean: ', np.mean(Ms)
		print 'Median: ',np.median(Ms)
		plt.hist(Ms,bins=100)
		plt.show()




if 1:
	"""
	metrics versus f plot
	Note : tweak pycs.tdc.metrics.py for plot parameters !
	"""
	#db = [item for item in db if '%s_td' %methods[0] in item]
	#dbnew = [item for item in db if item['%s_chi2' %method[0]] < 100]
	#print "I shoot the catastrophic failures"
	#db = [item for item in db if abs(item['%s_td' %methods[0]]-item['truetd']) < 20 ]
	#print "I select items with positive value of the true delay"
	#db = [item for item in db if item["truetd"] < 0]
	pycs.tdc.metrics.Pplotall(db,methods,lendb,zoomchi2=False,zoomA=False, errorbar=False)




if 0:
	"""
	histogram of d3cs scatter distribution
	"""

	import matplotlib.gridspec as gridspec
	import matplotlib




	fig = plt.figure()

	gs1 = gridspec.GridSpec(10, 6)
	gs1.update(left=0.1, right=0.89, top=0.95, bottom = 0.02, hspace=0.05, wspace = 0.1)

	ax1 = plt.subplot(gs1[:9, :4])
	ax2 = plt.subplot(gs1[:8, 4:])

	ax2.tick_params(left="on")
	#plt.subplots_adjust(left=0.1, right=0.97, top=0.96, bottom=0.13)
	#ax1 = fig.add_subplot(121)
	for tick in ax2.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax1.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax1.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	for tick in ax2.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	ax2.yaxis.tick_right()
	ax2.yaxis.set_label_position('right')
	matplotlib.rcParams.update({'font.size': 15}) # force fontsize for moved yticks...brute way

	from matplotlib.ticker import MaxNLocator
	ax2.set_xticks([-2, 0, 2])
	#ax2.xaxis.set_major_locator(MaxNLocator(4))

	diffdous = []
	diffplas = []

	for item in db:
		if "pycs_tdc1_d3cs-vanilla-dou-full_td" in item:
			diffdous.append(item["pycs_tdc1_d3cs-vanilla-dou-full_td"]-item["truetd"])
			ax2.scatter(np.log10(abs(item["pycs_tdc1_d3cs-vanilla-dou-full_td"]-item["truetd"])),item["truetd"],c="blue",alpha=0.4,s=30)

		elif "pycs_tdc1_d3cs-vanilla-doupla-full_td" in item:
			diffplas.append(item["pycs_tdc1_d3cs-vanilla-doupla-full_td"]-item["truetd"])
			ax2.scatter(np.log10(abs(item["pycs_tdc1_d3cs-vanilla-doupla-full_td"]-item["truetd"])),item["truetd"], c="green", alpha=0.5,s=30, marker='*')

	ax1.set_xlabel(r'$\tilde{\Delta t}_{D3CS} - \Delta t$',fontsize =18,labelpad=-2)
	ax1.set_ylabel(r'# of pairs',fontsize = 15, labelpad=-5)
	ax1.hist([diffdous,diffplas], histtype='bar',range=[-20,20], bins=25, alpha=0.8, lw=2, normed=False, color=['blue','green'],stacked=True)
	ax1.plot([],[],lw=8,label='D3CS doubtless',alpha=0.8,color='blue')
	ax1.plot([],[],lw=8,label='D3CS plausible',alpha=0.8,color='green')
	ax1.legend(fontsize=15,framealpha=0.5)
	ax1.set_ylim(0,1000)


	print " % doubtless out of histogram:",float(len([diffdou for diffdou in diffdous if abs(diffdou)>20]))/len(diffdous)*100
	print " % plausible out of histogram:",float(len([diffpla for diffpla in diffplas if abs(diffpla)>20]))/len(diffplas)*100
	print " % doupla out of histogram:",float(len([diffpla for diffpla in diffplas+diffdous if abs(diffpla)>20]))/len(diffplas+diffdous)*100

	#ax2.axvline(np.log10(np.mean(diffdous)), color="blue",linestyle='dashed',linewidth=4,alpha=0.5)
	#ax2.axvline(np.log10(np.mean(diffplas)), color="green",linestyle='dashed',linewidth=4,alpha=0.5)

	ax2.set_xlabel(r'$log_{10}\left(\tilde{\Delta t}_{D3CS} - \Delta t \right)$',fontsize =18,labelpad=-5)
	ax2.set_ylabel('True delay [days]',fontsize =15,labelpad=-5)

	plt.show()


########################################## OLD ########################################

if 0:
	"""
	d3cs guessed delay versus true delay
	"""
	fig = plt.figure()

	plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
	ax = fig.add_subplot(111)
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(15)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(15)

	diffdous = []
	diffdouplas = []

	for item in db:
		if "pycs_tdc1_d3cs-vanilla-dou-full_td" in item:

			plt.scatter(item["truetd"],np.log10(abs(item["pycs_tdc1_d3cs-vanilla-dou-full_td"]-item["truetd"])),c="blue",alpha=0.4,s=30)
			#diffdous.append(np.log10(abs(item["pycs_tdc1_d3cs-vanilla-dou-full_td"]-item["truetd"])))

		elif "pycs_tdc1_d3cs-vanilla-doupla-full_td" in item:

			plt.scatter(item["truetd"],np.log10(abs(item["pycs_tdc1_d3cs-vanilla-doupla-full_td"]-item["truetd"])), c="green", alpha=0.5,s=30)
			#diffdouplas.append(np.log10(abs(item["pycs_tdc1_d3cs-vanilla-doupla-full_td"]-item["truetd"])))

	plt.scatter([],[], c="blue", alpha=0.3, label="doubtless")
	plt.scatter([],[], c="green", alpha=0.5, label="plausible")
	plt.legend(loc=9,scatterpoints=1,fontsize=15)
	plt.xlabel('True delay [days]',fontsize =15)
	plt.ylabel(r'$log_{10}$(|D3CS guessed delay - True delay|) [days]',fontsize = 15)
	plt.savefig('blah_nr.pdf')
	#plt.show()


if 0:
	"""
	Print/Plot submissions final values, from metrics.txt, version 1, outdated
	"""
	import matplotlib.gridspec as gridspec

	fig = plt.figure(figsize=(15,5))
	gs1 = gridspec.GridSpec(2, 3)
	gs1.update(left=0.07, right=0.98, top=0.95, bottom=0.13, wspace=0.2,hspace=0.03)

	matplotlib.rcParams.update({'font.size': 15})

	ax1 = fig.add_subplot(gs1[0:2,0])
	ax2 = fig.add_subplot(gs1[0,1])
	ax2s = fig.add_subplot(gs1[1,1])
	ax3 = fig.add_subplot(gs1[0,2])
	ax3s = fig.add_subplot(gs1[1,2])


	rungs = [0, 1, 2, 3, 4]
	colors = ['blue', 'green','cyan','chartreuse']
	markers = ['o', '*', 'd', '^', '<']


	results = importmetrics()

	for method, color in zip(methods, colors):
		for rung, marker in zip(rungs[::-1], markers[::-1]):

			dbnew = [item for item in db if item["rung"] == rung]
			#dbnew = db
			result = [result for result in results if result["algorithm"] == str(method) and result["rung"] == str(rung)][0]

			f = pycs.tdc.metrics.getf(dbnew, method, len(dbnew))
			P, Perr = pycs.tdc.metrics.getP(dbnew, method)
			Pm, Pmerr = (float(result["P"]), float(result["Perr"]))
			A, Aerr = pycs.tdc.metrics.getA(dbnew, method)
			Am, Amerr = (float(result["A"]), float(result["Aerr"]))
			chi2, chi2err = pycs.tdc.metrics.getchi2(dbnew, method)
			chi2m, chi2merr = (float(result["chi2"]), float(result["chi2err"]))

			# print section, check we got more or less the same than metrics.txt

			print "*"*4, method, 'rung', rung, '*'*4
			"""
			print 'f: ', f
			print 'P: ', P, Perr
			print 'A: ', A, Aerr
			print 'chi2: ', chi2, chi2err

			print '*'*10
			print 'Pm: ', Pm,Pmerr
			print 'Am: ', Am,Amerr
			print 'chi2m: ', chi2m,chi2merr

			#print 'Pdiff: ', Pm-P
			#print 'Adiff: ', Am-A
			#print 'chi2diff: ', chi2m-chi2
			"""

			# plot it !

			skwargs = {'color': 'black', 'marker': marker, 's': 200, 'lw':1.5, 'facecolor': color, 'alpha':0.8}
			lkwargs = {'color': 'black', 'lw': 2.5, 'alpha': 0.5}
			ekwargs = {'color': color, 'linewidth': 2}

			Pmin = 0
			Pmax = 0.03
			Amin = -0.03
			Amax = 0.03
			chi2min = 0.5
			chi2max = 1.5

			#ax1.errorbar(Pm,Am,xerr=Pmerr, yerr=Amerr, **ekwargs)
			ax1.scatter(Pm, Am, **skwargs)
			ax1.set_xlabel(r'$P$',fontsize=20)
			ax1.set_ylabel(r'$A$',fontsize=20)
			ax1.set_xlim(0,0.18)
			ax1.axhspan(Amin, Amax, facecolor='grey', alpha=0.01)
			ax1.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
			ax1.set_ylim(-0.02,0.02)

			#ax2.errorbar(Pm,chi2m,xerr=Pmerr, yerr=chi2merr, **ekwargs)
			ax2.scatter(Pm, chi2m, **skwargs)
			ax2.set_xlabel(r'$P$',fontsize=20)
			#ax2.set_ylabel(r'$\chi^2$',fontsize=20)
			ax2.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax2.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
			ax2.set_xlim(0,0.18)
			ax2.set_ylim(2.8,15)
			ax2.get_xaxis().set_visible(False)

			#ax2s.errorbar(Pm,chi2m,xerr=Pmerr, yerr=chi2merr, **ekwargs)
			ax2s.scatter(Pm, chi2m, **skwargs)
			ax2s.set_xlabel(r'$P$',fontsize=20)
			ax2s.set_ylabel(r'$\chi^2$', fontsize=20, y=1.05)
			ax2s.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax2s.axvspan(Pmin, Pmax, facecolor='grey', alpha=0.01)
			ax2s.set_xlim(0,0.18)
			ax2s.set_ylim(0,2)

			#ax3.errorbar(Am,chi2m,xerr=Amerr, yerr=chi2merr, **ekwargs)
			ax3.scatter(Am, chi2m, **skwargs)
			ax3.set_xlabel(r'$A$',fontsize=20)
			#ax3.set_ylabel(r'$\chi^2$',fontsize=20)
			ax3.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax3.axvspan(Amin, Amax, facecolor='grey', alpha=0.01)
			ax3.set_xlim(-0.02,0.02)
			ax3.set_ylim(2.8,18)
			ax3.get_xaxis().set_visible(False)

			#ax3s.errorbar(Am,chi2m,xerr=Amerr, yerr=chi2merr, **ekwargs)
			ax3s.scatter(Am, chi2m, **skwargs)
			ax3s.set_xlabel(r'$A$',fontsize=20)
			ax3s.set_ylabel(r'$\chi^2$', fontsize=20, y=1.05)
			ax3s.axhspan(chi2min, chi2max, facecolor='grey', alpha=0.01)
			ax3s.axvspan(Amin, Amax, facecolor='grey', alpha=0.01)
			ax3s.set_ylim(0,2)
			ax3s.set_xlim(-0.02,0.02)



			from matplotlib.ticker import MaxNLocator
			for ax in [ax1,ax2,ax3,ax2s,ax3s]:
				ax.xaxis.set_major_locator(MaxNLocator(4))
				ax.yaxis.set_major_locator(MaxNLocator(4))

	for method, color in zip(methods, colors):
		methodreduc = method.split('_')[-1].split('-')[0]+'-'+method.split('_')[-1].split('-')[2]
		ax1.plot([],[],lw=10,label=methodreduc,color=color,alpha=0.8)

	for rung, marker in zip(rungs, markers)[0:3]:
		ax2.scatter([],[],label='rung'+str(rung),color='grey',marker=marker,s=200,lw=1)
	for rung, marker in zip(rungs, markers)[3:]:
		ax3.scatter([],[],label='rung'+str(rung),color='grey',marker=marker,s=200,lw=1)

	ax1.legend()
	ax2.legend(scatterpoints=1)
	ax3.legend(scatterpoints=1)
	#ax1.plot([1,2],[1,2])
	plt.show()

