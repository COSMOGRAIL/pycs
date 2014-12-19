import pycs
import numpy as np
import os,sys
import matplotlib.pyplot as plt

metrics = open('metrics.txt').readlines()


# team algorithm rung f chi2 chi2err P Perr A Aerr X f-nc chi2-nc chi2-ncerr P-nc P-ncerr A-nc A-ncerr

"""
0 = team
1 = algorith
2 = rung
3 = f
4 = chi2
5 = chi2err
6 = P
7 = Perr
8 = A
9 = Aerr
10 = X
11 = f-nc
12 = chi2-nc
13 = chi2-ncerr
14 = P-nc
15 = P-ncerr
16 = A-nc
17 = A-ncerr
"""


def recombine_submissions(results):

	"""
	Give me a pack of results per rung, I recombine them per methods
	"""

	combis = []
	methods = sorted(list(set([result['algorithm'] for result in results])))

	for method in methods:

		combi = {}
		relateds = [result for result in results if result["algorithm"] == method]
		
		"""
		how to get chi2 combined, P combined...:
		
		if P1 = 1/(f1*N)*sum(blahblah1) and P2 = 1/(f2*N)*sum(blahblah2)
		
		N*(f1*P1+f2*P2) = sum(blahblah1)+sum(blahblah2)=sum(blahblah12)
		
		or,
		
		P12 = 1/{[(f1+f2)/2]*2N}*sum(blahblah12)
		
		then,
		
		N*(f1+f2)*P12 = sum(blahblah12) = sum(blahblah1) + sum(blahblah2) = N*(f1*P1+f2*P2)
		
		thus,
		
		P12 = sum(fi*Pi)/sum(fi), thus the computations below for chi2, P and A
		"""	


		combi["team"] = relateds[0]["team"]
		combi["algorithm"] = method
		combi["rung"] = 'all'
		combi["f"] = sum([float(related["f"]) for related in relateds])/5.0 # as some submissions are not complete...(i.e. no rung 4)
		combi["chi2"] = sum([float(related["f"])*float(related["chi2"]) for related in relateds])/sum([float(related["f"]) for related in relateds])
		combi["chi2err"] = None
		combi["P"] = sum([float(related["f"])*float(related["P"]) for related in relateds])/sum([float(related["f"]) for related in relateds])
		combi["Perr"] = None
		combi["A"] = sum([float(related["f"])*float(related["A"]) for related in relateds])/sum([float(related["f"]) for related in relateds])
		combi["Aerr"] = None
		combi["X"] = None
		combi["f-nc"] = None
		combi["chi2-nc"] = None
		combi["chi2-ncerr"] = None
		combi["P-nc"] = None
		combi["P-ncerr"] = None
		combi["A-nc"] = None
		combi["A-ncerr"] = None

		combis.append(combi)

	return combis




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
			result["algorithm"] = reduced[1]
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


#Selection Criterias
	
#results = [result for result in results if result["rung"] == "4"]

combis = recombine_submissions(results)



# 1) crude cuts, tdc0 success criterias
if 0:
	# P < 15%
	Pcut=[0,0.15]

	# f > 0.3
	fcut=[0.3,1]

	# A < 15%
	Acut=[-0.15,0.15]

	# 0.5 < chi2 < 2.0
	chi2cut=[0.5,2.0]


# 2) competitive cuts
if 0:
	# P < 3%
	Pcut=[0,0.03]

	# f > 0.5
	fcut=[0.5,1]

	# A < 3%
	Acut=[-0.03,0.03]

	# chi2 < 1.5
	chi2cut=[0.5,1.5]
	
# 3) LSST longer run cut
if 1:
	# P < 3%
	Pcut=[0,0.03]

	# f > 0.5
	fcut=[0.5,1]

	# A < 0.2%
	Acut=[-0.002,0.002]

	# chi2 < 1.5
	chi2cut=[0,1.5]	




#results = combis
'''
for combi in results:
	if combi["team"] == "Jackson":
		print combi['f'],combi['P'],combi['A'],combi['chi2']
sys.exit()		
'''

for combi in results:
	if float(combi["P"]) < 0.03 and abs(float(combi["A"])) < 0.002 and float(combi["f"]) > 0.1 and float(combi["chi2"]) < 1.5 and float(combi["chi2"]) > 0.5:
		print combi["team"],combi["algorithm"],'rung',combi["rung"],'have an A = %s' %combi["A"]




xtoplot = 'f'
ytoplot = 'P'
plt.figure('competitive - rungs',figsize=(18,14))

plt.subplot(3,2,2)
plt.plot([result[xtoplot] for result in results if result["team"] == "Tewes"],[result[ytoplot] for result in results if result["team"] == "Tewes"],'bo',label='Tewes')
plt.plot([result[xtoplot] for result in results if result["team"] == "Shafieloo"],[result[ytoplot] for result in results if result["team"] == "Shafieloo"],'ro',label='Shafieloo')
plt.plot([result[xtoplot] for result in results if result["team"] == "Jackson"],[result[ytoplot] for result in results if result["team"] == "Jackson"],'go',label='Jackson')
plt.plot([result[xtoplot] for result in results if result["team"] == "Kumar"],[result[ytoplot] for result in results if result["team"] == "Kumar"],'yo',label='Kumar')
plt.plot([result[xtoplot] for result in results if result["team"] == "Hojjati"],[result[ytoplot] for result in results if result["team"] == "Hojjati"],'mo',label='Hojjati')
plt.plot([result[xtoplot] for result in results if result["team"] == "Rumbaugh"],[result[ytoplot] for result in results if result["team"] == "Rumbaugh"],'ko',label='Rumbaugh')
plt.plot([result[xtoplot] for result in results if result["team"] == "DeltaTBayes"],[result[ytoplot] for result in results if result["team"] == "DeltaTBayes"],'y*',label='DeltaTbayes')
plt.plot([result[xtoplot] for result in results if result["team"] == "JPL"],[result[ytoplot] for result in results if result["team"] == "JPL"],'m*',label='JPL')
plt.xlabel(xtoplot)
plt.ylabel(ytoplot)
plt.legend(numpoints=1,fontsize=15)
xcut=[min([result[xtoplot] for result in results]),max([result[xtoplot] for result in results])]
ycut=[min([result[ytoplot] for result in results]),max([result[ytoplot] for result in results])]
if xtoplot == 'A':
	xcut = Acut
if ytoplot == 'A':
	ycut = Acut
if xtoplot == 'P':
	xcut = Pcut
if ytoplot == 'P':
	ycut = Pcut
if xtoplot == 'f':
	xcut = fcut
if ytoplot == 'f':
	ycut = fcut
if xtoplot == 'chi2':
	xcut = chi2cut
if ytoplot == 'chi2':
	ycut = chi2cut	
plt.axis(xcut+ycut)
plt.grid(True)


xtoplot = 'f'
ytoplot = 'A'
plt.subplot(3,2,1)
plt.plot([result[xtoplot] for result in results if result["team"] == "Tewes"],[result[ytoplot] for result in results if result["team"] == "Tewes"],'bo',label='Tewes')
plt.plot([result[xtoplot] for result in results if result["team"] == "Shafieloo"],[result[ytoplot] for result in results if result["team"] == "Shafieloo"],'ro',label='Shafieloo')
plt.plot([result[xtoplot] for result in results if result["team"] == "Jackson"],[result[ytoplot] for result in results if result["team"] == "Jackson"],'go',label='Jackson')
plt.plot([result[xtoplot] for result in results if result["team"] == "Kumar"],[result[ytoplot] for result in results if result["team"] == "Kumar"],'yo',label='Kumar')
plt.plot([result[xtoplot] for result in results if result["team"] == "Hojjati"],[result[ytoplot] for result in results if result["team"] == "Hojjati"],'mo',label='Hojjati')
plt.plot([result[xtoplot] for result in results if result["team"] == "Rumbaugh"],[result[ytoplot] for result in results if result["team"] == "Rumbaugh"],'ko',label='Rumbaugh')
plt.plot([result[xtoplot] for result in results if result["team"] == "DeltaTBayes"],[result[ytoplot] for result in results if result["team"] == "DeltaTBayes"],'y*',label='DeltaTbayes')
plt.plot([result[xtoplot] for result in results if result["team"] == "JPL"],[result[ytoplot] for result in results if result["team"] == "JPL"],'m*',label='JPL')
plt.xlabel(xtoplot)
plt.ylabel(ytoplot)
xcut=[min([result[xtoplot] for result in results]),max([result[xtoplot] for result in results])]
ycut=[min([result[ytoplot] for result in results]),max([result[ytoplot] for result in results])]
if xtoplot == 'A':
	xcut = Acut
if ytoplot == 'A':
	ycut = Acut
if xtoplot == 'P':
	xcut = Pcut
if ytoplot == 'P':
	ycut = Pcut
if xtoplot == 'f':
	xcut = fcut
if ytoplot == 'f':
	ycut = fcut
if xtoplot == 'chi2':
	xcut = chi2cut
if ytoplot == 'chi2':
	ycut = chi2cut	
plt.axis(xcut+ycut)
plt.grid(True)


xtoplot = 'f'
ytoplot = 'chi2'
plt.subplot(3,2,3)
plt.plot([result[xtoplot] for result in results if result["team"] == "Tewes"],[result[ytoplot] for result in results if result["team"] == "Tewes"],'bo',label='Tewes')
plt.plot([result[xtoplot] for result in results if result["team"] == "Shafieloo"],[result[ytoplot] for result in results if result["team"] == "Shafieloo"],'ro',label='Shafieloo')
plt.plot([result[xtoplot] for result in results if result["team"] == "Jackson"],[result[ytoplot] for result in results if result["team"] == "Jackson"],'go',label='Jackson')
plt.plot([result[xtoplot] for result in results if result["team"] == "Kumar"],[result[ytoplot] for result in results if result["team"] == "Kumar"],'yo',label='Kumar')
plt.plot([result[xtoplot] for result in results if result["team"] == "Hojjati"],[result[ytoplot] for result in results if result["team"] == "Hojjati"],'mo',label='Hojjati')
plt.plot([result[xtoplot] for result in results if result["team"] == "Rumbaugh"],[result[ytoplot] for result in results if result["team"] == "Rumbaugh"],'ko',label='Rumbaugh')
plt.plot([result[xtoplot] for result in results if result["team"] == "DeltaTBayes"],[result[ytoplot] for result in results if result["team"] == "DeltaTBayes"],'y*',label='DeltaTbayes')
plt.plot([result[xtoplot] for result in results if result["team"] == "JPL"],[result[ytoplot] for result in results if result["team"] == "JPL"],'m*',label='JPL')
plt.xlabel(xtoplot)
plt.ylabel(ytoplot)
xcut=[min([result[xtoplot] for result in results]),max([result[xtoplot] for result in results])]
ycut=[min([result[ytoplot] for result in results]),max([result[ytoplot] for result in results])]
if xtoplot == 'A':
	xcut = Acut
if ytoplot == 'A':
	ycut = Acut
if xtoplot == 'P':
	xcut = Pcut
if ytoplot == 'P':
	ycut = Pcut
if xtoplot == 'f':
	xcut = fcut
if ytoplot == 'f':
	ycut = fcut
if xtoplot == 'chi2':
	xcut = chi2cut
if ytoplot == 'chi2':
	ycut = chi2cut	
plt.axis(xcut+ycut)
plt.grid(True)


xtoplot = 'A'
ytoplot = 'P'
plt.subplot(3,2,4)
plt.plot([result[xtoplot] for result in results if result["team"] == "Tewes"],[result[ytoplot] for result in results if result["team"] == "Tewes"],'bo',label='Tewes')
plt.plot([result[xtoplot] for result in results if result["team"] == "Shafieloo"],[result[ytoplot] for result in results if result["team"] == "Shafieloo"],'ro',label='Shafieloo')
plt.plot([result[xtoplot] for result in results if result["team"] == "Jackson"],[result[ytoplot] for result in results if result["team"] == "Jackson"],'go',label='Jackson')
plt.plot([result[xtoplot] for result in results if result["team"] == "Kumar"],[result[ytoplot] for result in results if result["team"] == "Kumar"],'yo',label='Kumar')
plt.plot([result[xtoplot] for result in results if result["team"] == "Hojjati"],[result[ytoplot] for result in results if result["team"] == "Hojjati"],'mo',label='Hojjati')
plt.plot([result[xtoplot] for result in results if result["team"] == "Rumbaugh"],[result[ytoplot] for result in results if result["team"] == "Rumbaugh"],'ko',label='Rumbaugh')
plt.plot([result[xtoplot] for result in results if result["team"] == "DeltaTBayes"],[result[ytoplot] for result in results if result["team"] == "DeltaTBayes"],'y*',label='DeltaTbayes')
plt.plot([result[xtoplot] for result in results if result["team"] == "JPL"],[result[ytoplot] for result in results if result["team"] == "JPL"],'m*',label='JPL')
plt.xlabel(xtoplot)
plt.ylabel(ytoplot)
xcut=[min([result[xtoplot] for result in results]),max([result[xtoplot] for result in results])]
ycut=[min([result[ytoplot] for result in results]),max([result[ytoplot] for result in results])]
if xtoplot == 'A':
	xcut = Acut
if ytoplot == 'A':
	ycut = Acut
if xtoplot == 'P':
	xcut = Pcut
if ytoplot == 'P':
	ycut = Pcut
if xtoplot == 'f':
	xcut = fcut
if ytoplot == 'f':
	ycut = fcut
if xtoplot == 'chi2':
	xcut = chi2cut
if ytoplot == 'chi2':
	ycut = chi2cut	
plt.axis(xcut+ycut)
plt.grid(True)


xtoplot = 'A'
ytoplot = 'chi2'
plt.subplot(3,2,5)
plt.plot([result[xtoplot] for result in results if result["team"] == "Tewes"],[result[ytoplot] for result in results if result["team"] == "Tewes"],'bo',label='Tewes')
plt.plot([result[xtoplot] for result in results if result["team"] == "Shafieloo"],[result[ytoplot] for result in results if result["team"] == "Shafieloo"],'ro',label='Shafieloo')
plt.plot([result[xtoplot] for result in results if result["team"] == "Jackson"],[result[ytoplot] for result in results if result["team"] == "Jackson"],'go',label='Jackson')
plt.plot([result[xtoplot] for result in results if result["team"] == "Kumar"],[result[ytoplot] for result in results if result["team"] == "Kumar"],'yo',label='Kumar')
plt.plot([result[xtoplot] for result in results if result["team"] == "Hojjati"],[result[ytoplot] for result in results if result["team"] == "Hojjati"],'mo',label='Hojjati')
plt.plot([result[xtoplot] for result in results if result["team"] == "Rumbaugh"],[result[ytoplot] for result in results if result["team"] == "Rumbaugh"],'ko',label='Rumbaugh')
plt.plot([result[xtoplot] for result in results if result["team"] == "DeltaTBayes"],[result[ytoplot] for result in results if result["team"] == "DeltaTBayes"],'y*',label='DeltaTbayes')
plt.plot([result[xtoplot] for result in results if result["team"] == "JPL"],[result[ytoplot] for result in results if result["team"] == "JPL"],'m*',label='JPL')
plt.xlabel(xtoplot)
plt.ylabel(ytoplot)
xcut=[min([result[xtoplot] for result in results]),max([result[xtoplot] for result in results])]
ycut=[min([result[ytoplot] for result in results]),max([result[ytoplot] for result in results])]
if xtoplot == 'A':
	xcut = Acut
if ytoplot == 'A':
	ycut = Acut
if xtoplot == 'P':
	xcut = Pcut
if ytoplot == 'P':
	ycut = Pcut
if xtoplot == 'f':
	xcut = fcut
if ytoplot == 'f':
	ycut = fcut
if xtoplot == 'chi2':
	xcut = chi2cut
if ytoplot == 'chi2':
	ycut = chi2cut	
plt.axis(xcut+ycut)
plt.grid(True)



xtoplot = 'chi2'
ytoplot = 'P'
plt.subplot(3,2,6)
plt.plot([result[xtoplot] for result in results if result["team"] == "Tewes"],[result[ytoplot] for result in results if result["team"] == "Tewes"],'bo',label='Tewes')
plt.plot([result[xtoplot] for result in results if result["team"] == "Shafieloo"],[result[ytoplot] for result in results if result["team"] == "Shafieloo"],'ro',label='Shafieloo')
plt.plot([result[xtoplot] for result in results if result["team"] == "Jackson"],[result[ytoplot] for result in results if result["team"] == "Jackson"],'go',label='Jackson')
plt.plot([result[xtoplot] for result in results if result["team"] == "Kumar"],[result[ytoplot] for result in results if result["team"] == "Kumar"],'yo',label='Kumar')
plt.plot([result[xtoplot] for result in results if result["team"] == "Hojjati"],[result[ytoplot] for result in results if result["team"] == "Hojjati"],'mo',label='Hojjati')
plt.plot([result[xtoplot] for result in results if result["team"] == "Rumbaugh"],[result[ytoplot] for result in results if result["team"] == "Rumbaugh"],'ko',label='Rumbaugh')
plt.plot([result[xtoplot] for result in results if result["team"] == "DeltaTBayes"],[result[ytoplot] for result in results if result["team"] == "DeltaTBayes"],'y*',label='DeltaTbayes')
plt.plot([result[xtoplot] for result in results if result["team"] == "JPL"],[result[ytoplot] for result in results if result["team"] == "JPL"],'m*',label='JPL')
plt.xlabel(xtoplot)
plt.ylabel(ytoplot)
xcut=[min([result[xtoplot] for result in results]),max([result[xtoplot] for result in results])]
ycut=[min([result[ytoplot] for result in results]),max([result[ytoplot] for result in results])]
if xtoplot == 'A':
	xcut = Acut
if ytoplot == 'A':
	ycut = Acut
if xtoplot == 'P':
	xcut = Pcut
if ytoplot == 'P':
	ycut = Pcut
if xtoplot == 'f':
	xcut = fcut
if ytoplot == 'f':
	ycut = fcut
if xtoplot == 'chi2':
	xcut = chi2cut
if ytoplot == 'chi2':
	ycut = chi2cut	
plt.axis(xcut+ycut)
plt.grid(True)


plt.show()
















