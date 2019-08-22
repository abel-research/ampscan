AmpScan
=======

![ampscanlogo](docs/AmpScanlogo.svg)

**Join chat:** [![Join the chat at https://gitter.im/ampscan](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/ampscan)

**Build Status:** [![Build Status](https://travis-ci.org/abel-research/ampscan.svg?branch=master)](https://travis-ci.org/abel-research/ampscan)

**License:** [![License](https://img.shields.io/github/license/abel-research/ampscan](../LICENSE)

AmpScan is an open-source Python package for analysis and visualisation of digitised surface scan data, specifically for applications within Prosthetics and Orthotics, developed with the ABEL at the University of Southampton. These industries are increasingly using surface scanners as part of clinical practice to capture the patient's individual geometry to design personalised devices. AmpScan gives researchers within this field access to powerful tools to analyse the collected scans to help inform clinical practice towards improved patient-outcomes. This package has been designed to be accessible for researchers and clinicians with only a limited knowledge of Python. Therefore, analysis procedures can all be accessed using the lightweight Graphical User Interface. 

AmpScan relies heavily on [NumPy](http://www.numpy.org/) and [SciPy](https://www.scipy.org/) to perform mathematical operations with visualisation handled by [PyQt](https://riverbankcomputing.com/software/pyqt/intro) and [VTK](https://www.vtk.org/). The package is still under development by researchers at the University of Southampton. For full documentation, visit the [AmpScan website](https://ampscan.readthedocs.io/en/latest/).

Installing with Conda (Recommended)
-----------------------------------

AmpScan has a number of dependencies, namely; NumPy, SciPy, Matplotlib, PyQt and vtk. We recommend using 
conda to deal with these. Before installation, ensure your environment is using Python 3. Verify that 
you are running the latest version of pip:

``python -m pip install --upgrade pip``

Install dependencies using conda:

``conda install numpy scipy pyqt matplotlib vtk==8.1.0``

Install AmpScan using pip:

``pip install AmpScan``

Installing with Pip
-------------------

AmpScan has a number of dependencies, namely; NumPy, SciPy, Matplotlib, PyQt and vtk. Before 
installing, ensure you have the latest version of pip:

``python -m pip install --upgrade pip``

Then install the dependencies using:

``pip install numpy matplotlib scipy pyqt5 vtk==8.1.0``

You can then install AmpScan from test PyPI using:

``pip install AmpScan``

Developer Install
-----------------

For the most up to date version of AmpScan, clone directly from the gitlab repository using:

``git clone https://github.com/abel-research/ampscan``

Navigate to the `AmpScan/` directory and run a pip install using:

``pip install -e .``

Maintainer Notes
----------------

Documentation for the AmpScan library is automatically generated using 
[sphinx](http://www.sphinx-doc.org/en/master/). Any additional code should be documented in 
accordance with 'numpy style' docstrings. A template can be found 
[here](https://www.numpy.org/devdocs/docs/howto_document.html#example).

Testing is performed automatically using [Travis Ci](https://travis-ci.org/). New tests can be added to the repo. 

How to acknowledge
------------------

Find license [here](../LICENSE)
