from PIL import Image
import glob
import os,sys

"""
merging Images...
"""


def makeplot(workdir,filelists,savefig=True):

	plotdir = os.path.join(workdir,'combi_pngs')
	if not os.path.isdir(plotdir):
		os.mkdir(plotdir)


	for ind,filelist in enumerate(filelists):

		print '='*10,'%i/%i'%(ind+1,len(filelists)),'='*10

		plotname = os.path.join(plotdir,os.path.basename(filelist))
		rung = filelist.split('_')[-2]
		pair = filelist.split('_')[-1]



		png1 = Image.open("%s/tdc1_%s_%s/plot_res_singleshift.png" %(workdir,rung,pair))
		png2 = Image.open("%s/tdc1_%s_%s/plot_res_perseasons_sum.png" %(workdir,rung,pair))
		png3 = Image.open("%s/tdc1_%s_%s/plot_res_perseasons_median.png" %(workdir,rung,pair))
		png4 = Image.open("%s/tdc1_%s_%s/plot_res_perseasons_individual.png" %(workdir,rung,pair))
		png5 = Image.open("%s/tdc1_%s_%s/spline.png" %(workdir,rung,pair))


		scale1 = 0.6
		scale2 = 0.6
		scale3 = 0.6
		scale4 = 0.6


		png1 = png1.resize([int(val*scale1) for val in png1.size],resample=Image.ANTIALIAS)
		png2 = png2.resize([int(val*scale2) for val in png2.size],resample=Image.ANTIALIAS)
		png3 = png3.resize([int(val*scale3) for val in png3.size],resample=Image.ANTIALIAS)
		png4 = png4.resize([int(val*scale4) for val in png4.size],resample=Image.ANTIALIAS)

		png5 = png5.resize([int(png1.size[0]+png2.size[0]+png3.size[0]-png4.size[0])-210,png4.size[1]],resample=Image.ANTIALIAS)



		merge_image = Image.new("RGB", (max(png1.size[0]+png2.size[0]+png3.size[0],png4.size[0])-140,max(png1.size[1],png2.size[1],png3.size[1])+png4.size[1]), "white")

		merge_image.paste(png1, (0,0))
		merge_image.paste(png2, (png1.size[0]-70,0))
		merge_image.paste(png3, (png1.size[0]+png2.size[0]-140,0))
		merge_image.paste(png4, (0,max(png1.size[1],png2.size[1],png3.size[1])))	
		merge_image.paste(png5, (png4.size[0],max(png1.size[1],png2.size[1],png3.size[1])))	

		if savefig == True:
			merge_image.save(os.path.join(plotname+'.png'),"png")
		else:
			merge_image.show()


def mergesumspics(workdir,pairids):

	pngs = []
	for pairid in pairids:
		pngs.append(Image.open("%s/%s/plot_res_perseason_sum.png" %(workdir,pairid)))

	merge_image = Image.new("RGB", (0,0), "white")
	scale = 0.6
	for png in pngs:
		png = png.resize([int(val*scale) for val in png.size],resample=Image.ANTIALIAS)

if __name__ == "__main__":

	workdir = 'all-4'
	pairids = ['tdc1_0_1014','tdc1_3_313','tdc1_1_507']
	mergesumspics(workdir,pairids)
	#filelists = sorted(glob.glob(os.path.join(workdir,'tdc1_*_*')))
	#makeplot(workdir,filelists)



