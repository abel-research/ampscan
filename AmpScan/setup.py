# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 15:54:27 2018

@author: js22g12
"""

from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
      ext_modules = cythonize('cython_ext.pyx'),
      include_dirs=[numpy.get_include()]
      )