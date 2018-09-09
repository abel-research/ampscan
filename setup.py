# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 13:43:43 2016

@author: js22g12
"""

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='AmpScan',
      version='0.7',
      description=('Package for analysis of '
                   'surface scan data of residual limbs'),
      long_description=readme(),
      author='Joshua Steer',
      author_email='Joshua.Steer@soton.ac.uk',
      license='MIT',
      packages=['AmpScan'],
      install_requires=['numpy', 'matplotlib', 'scipy', 'pyqt5', 'vtk==8.1.0', 'sphinxcontrib-napoleon'],
      package_data={},
      include_package_data=True,
      zip_safe=False,)
