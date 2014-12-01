import pycs
import matplotlib.pyplot as plt
import os,sys
import numpy as np


db = pycs.gen.util.readpickle('db.pkl').values()
#db = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry ] # selecting confidence level...dumb way
db = [entry for entry in db if entry["in_tdc1"] == 1]
#db = [entry for entry in db if entry["crude_conflevel"] == 1]
#db = [entry for entry in db if entry["crude_sigmabestmin"] > 1.5]



# plot fraction of catastrophic errors vs sigma
fig,ax1 = plt.subplots()
ax1 = fig.add_subplot(111)

colors=['chartreuse','crimson','cyan']
for ind,method in enumerate(["all-4","all-5"]):
	sigmas = np.linspace(0,max([entry["%s_crude_sigmabestmin" %method] for entry in db]),500)
	errfrac_auto = []
	errfrac_d3cs = []
	dblengths = []
	for sigma in sigmas:
		diffsum = 0
		dbnew = [entry for entry in db if entry["%s_crude_sigmabestmin" %method] >= sigma] #and entry["%s_crude_nmin" %method] < 2 and entry["%s_perseasons_sum_stdmag" %method] < 0.01]
		for entry in dbnew:
			if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
				diffsum +=1

		errfrac_auto.append(float(float(diffsum)/(len(dbnew)+0.001)*100))
		dblengths.append(len(dbnew))
	ax1.plot(sigmas,errfrac_auto,colors[ind],linewidth=4,label='Crude Estimator')


# add d3cs values

def getposonsigmaaxis(npairs):
	val =  min(dblengths, key=lambda dblength: abs(dblength-npairs))
	return sigmas[dblengths.index(val)]

diffdou = 0
dbdou = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-dou-full_td" in entry]
for entry in dbdou:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-dou-full_td"])>20:
		diffdou += 1
ax1.scatter(getposonsigmaaxis(len(dbdou)),float(diffdou)/len(dbdou)*100,s=240,c='blue',marker='d',label='D3CS-dou(%i)' %len(dbdou))

diffdoupla = 0
dbdoupla = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]
for entry in dbdoupla:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>20:
		diffdoupla += 1
ax1.scatter(getposonsigmaaxis(len(dbdoupla)),float(diffdoupla)/len(dbdoupla)*100,s=240,c='green',marker='d',label='D3CS-doupla(%i)' %len(dbdoupla))


diffdouplamul = 0
dbdouplamul = [entry for entry in db if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry]
for entry in dbdouplamul:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
		diffdouplamul += 1
ax1.scatter(getposonsigmaaxis(len(dbdouplamul)),float(diffdouplamul)/len(dbdouplamul)*100,s=240,c='yellow',marker='d',label='D3CS-douplamul(%i)' %len(dbdouplamul))

diffall = 0
for entry in db:
	if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
			diffall +=1
	else:
		diffall +=1
ax1.scatter(getposonsigmaaxis(len(db)),float(diffall)/len(db)*100,s=240,c='red',marker='d',label='D3CS-all(%i)' %len(db))


'''
diffpla = 0
dbpla = [entry for entry in dbdoupla if not "pycs_tdc1_d3cs-vanilla-dou-full_td" in entry]
for entry in dbpla:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-doupla-full_td"])>20:
		diffpla += 1

diffmul = 0
dbmul = [entry for entry in dbdouplamul if not "pycs_tdc1_d3cs-vanilla-doupla-full_td" in entry]
for entry in dbmul:
	if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
		diffmul += 1
'''


for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
	label.set_fontname('Arial')
	label.set_fontsize(13)
ax1.set_xlabel("sigma", fontsize=13)
ax1.set_ylabel("critical failures [%]", fontsize=13)
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
ax2.set_xlabel('number of pairs', fontsize=13)



plt.show()
sys.exit()



# compute how many catastrophic failures
method= "all-4"
#db = [entry for entry in db if entry["%s_crude_sigmabestmin" % method] >= 2]
print "length of database:", len(db)


diffalld3cs = 0
for entry in db:
	if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20 and abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
			diffalld3cs += 1
	else:
		if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
			diffalld3cs += 1

print diffalld3cs/float(len(db))*100
sys.exit()


diffd3cs = 0
diffsingleshift = 0
diffsum = 0
diffmedian = 0

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

	allfail = 0
	if "pycs_tdc1_d3cs-vanilla-douplamul-full_td" in entry:
		if abs(entry["truetd"]-entry["pycs_tdc1_d3cs-vanilla-douplamul-full_td"])>20:
			diffd3cs +=1
	else:
		diffd3cs +=1
	if abs(entry["truetd"]-entry["%s_singleshift_td" %method])>20:
		diffsingleshift +=1
		singleshift_id.append(entry["id"])
		allfail+=1
	if abs(entry["truetd"]-entry["%s_perseasons_sum_td" %method])>20:
		diffsum +=1
		sum_id.append(entry["id"])
		allfail+=1
	if abs(entry["truetd"]-entry["%s_perseasons_median_td" %method])>20:
		diffmedian +=1
		median_id.append(entry["id"])
		allfail+=1

	if allfail == 3:
		allfail_id.append(entry["id"])


print 'd3cs: %.2f'%float(float(diffd3cs)/len(db)*100),"%"
print 'singleshift: %.2f'%float(float(diffsingleshift)/len(db)*100),"%"
print 'sum: %.2f'%float(float(diffsum)/len(db)*100),"%"
print 'median: %.2f'%float(float(diffmedian)/len(db)*100),"%"
print 'allfail: %.2f' %float(float(len(allfail_id))/len(db)*100),"%"
#print '='*80
#print 'MEDIAN',median_id
#print '='*80
#print 'SUM',sum_id
sys.exit()

### Now, displaying troublemakers:
todisplay = 'display'
for pairid in sum_id:
	#print pairid
	todisplay +=' %s/%s/plot_res_perseasons_sum.png' %(method, pairid)
	#residuals  = pycs.gen.util.readpickle(os.path.join(workdir,"%s/resids_perseasons_sum.pkl" %pairid))
	#imgpath = os.path.join(workdir, "%s/plot_res_perseasons_sum.png" %pairid)
	#os.system("display %s" %imgpath)
#pycs.gen.util.writepickle(sum_id,"tempid.pkl")
os.system(todisplay)
