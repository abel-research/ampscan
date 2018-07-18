# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 13:43:43 2016

@author: js22g12
"""

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='AmpScan',
      version='2017.11',
      description=('Package for analysis of '
                   'surface scan data of residual limbs'),
      long_description=readme(),
      author='Joshua Steer',
      author_email='Joshua.Steer@soton.ac.uk',
      license='MIT',
      packages=['AmpScan',],
      install_requires=['numpy', 'pandas', 'matplotlib', 'scipy', 'sphinxcontrib-napoleon', 'vtk', 'PyQt5', 'struct'],
      package_data={'example_stl':' 01_PhantomShell_ICEM_3mm.stl'},
      include_package_data=True,
      zip_safe=False)
