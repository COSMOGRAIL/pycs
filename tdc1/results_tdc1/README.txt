In .
	
	Confidence computed with combiconf2, with god estimates.
	
	:method
		spline (spl) - pycs spline optimizer
		spldiff (sdi) - pycs spline difference optimizer

	:select
		doubtless (dou)
		plausible (pla)
		multimodal (mul)
		uninformative (uni)

	:ncopy (c***)
		how many copycurves are drawn for the mean estimation

	:nsim  (s***)
		how many simcurves are drawn for the error estimation

	:maxshift (m***)
		maximum shift for the "wrong delay" given around the "true delay" of the simcurves


	


---------------------------------------------------------------------
In combiconf1_pkls (old confidence level computation computation)

	pkls name (from run_pycs.py):


	:method
		spline (spl) - pycs spline optimizer
		spldiff (sdi) - pycs spline difference optimizer

	:select
		doubtless (dou)
		plausible (pla)
		multimodal (mul)
		doubtless_to_multimodal (dtm)
		doubtless_to_uninformative (dtu)
		uninformative (uni)	

	:ncopy
		how many copycurves are drawn for the mean estimation

	:nsim
		how many simcurves are drawn for the error estimation

	:maxshift
		maximum shift for the "wrong delay" given around the "true delay" of the simcurves

	:rtype
		uniform (uni) : we draw the wrong delay uniformly between 0 and maxshift	
		## implement gaussian ?
		WARNING - since 15.06, not used anymore !
	:rung
		0-1-2-3-4 : rung number					











