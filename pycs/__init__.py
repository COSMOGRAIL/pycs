"""
This is PyCS, a python toolbox to estimate time delays between COSMOGRAIL light curves.

:Authors: Vivien Bonvin and Malte Tewes
:License: GPLv3 or later (see README.txt)

If you use PyCS in a publication, please cite our `COSMOGRAIL XI <http://arxiv.org/abs/1208.5598>`_ paper, thanks !

.. note:: To use this toolbox, just ``import pycs``; this gives you access to subpackages, e.g. you could call ``pycs.gen.lc.display(lcs)``.
	There is one **exception** : the ``regdiff`` subpackage requires ``pymc``, but I don't want to add this as a dependency.
	Hence ``regdiff`` is not imported by default. To use this particular curve shifting technique, add ``import pycs.regdiff``.

"""

__author__ = "Vivien Bonvin and Malte Tewes"
__copyright__ = "2013"
__version__ = "2.0dev"


__all__ = ["gen", "disp", "spl", "sim", "tdc", "spldiff"]


import gen
import disp
import spl
import sim
import tdc
import spldiff
#import regdiff
#import regdiff2
