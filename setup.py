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
      python_requires='>=3.6,<3.7',  # Your supported Python ranges
      install_requires=['numpy',
                        'matplotlib',
                        'scipy',
                        'sphinxcontrib-napoleon',
                        'vtk==8.1.0',
                        'PyPDF2==1.26.0',
                        'PyQt5==5.13.0',
                        'reportlab==3.5.23'],
      package_data={},
      include_package_data=True,
      zip_safe=False,)
