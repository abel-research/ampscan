![ampscanlogo](docs/ampscan_header.svg)

**Join chat:** [![Join the chat at https://gitter.im/ampscan](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/ampscan)
**Build status:** [![Build Status](https://travis-ci.org/abel-research/ampscan.svg?branch=master)](https://travis-ci.org/abel-research/ampscan)
**License:** [![License](https://img.shields.io/github/license/abel-research/ampscan)](../master/LICENSE)

ampscan is an open-source Python package for analysis and visualisation of digitised surface scan data, specifically for applications within Prosthetics and Orthotics, developed with the ABEL at the University of Southampton. These industries are increasingly using surface scanners as part of clinical practice to capture the patient's individual geometry to design personalised devices. ampscan gives researchers within this field access to powerful tools to analyse the collected scans to help inform clinical practice towards improved patient-outcomes. This package has been designed to be accessible for researchers and clinicians with only a limited knowledge of Python. Therefore, analysis procedures can all be accessed using the lightweight Graphical User Interface within the git repo, and will soon be available as a standalone [web-app](https://github.com/abel-research/ampscan_webapp).

ampscan relies heavily on [NumPy](http://www.numpy.org/) and [SciPy](https://www.scipy.org/) to perform mathematical operations with visualisation handled by [PyQt](https://riverbankcomputing.com/software/pyqt/intro) and [VTK](https://www.vtk.org/). The package is still under development by researchers at the University of Southampton. For full documentation, visit the [ampscan website](https://ampscan.readthedocs.io/en/latest/).

Installing ampscan
-------------------

ampscan has a number of dependencies, namely; NumPy, SciPy, Matplotlib, PyQt and vtk. We recommend using 
conda to deal with these. Before installation, ensure your environment is using Python 3. 

Install dependencies using conda:

``conda install numpy scipy pyqt matplotlib vtk==8.1.0``

For the most up to date version of ampscan, clone directly from the github repository using:

``git clone https://github.com/abel-research/ampscan``

Navigate to the `ampscan/` directory and run a pip install using:

``pip install -e .``

ampscan will soon be available on pip once v0.3 is released 

If you are installing on Red Hat, you may need to install the dependencies listed in the [Yum Requirements file](yum_requirements.txt).

Maintainer Notes
----------------

Documentation for the ampscan library is automatically generated using 
[sphinx](http://www.sphinx-doc.org/en/master/). Any additional code should be documented in 
accordance with 'numpy style' docstrings. A template can be found 
[here](https://www.numpy.org/devdocs/docs/howto_document.html#example).

Testing
-------

Testing is performed automatically using [Travis Ci](https://travis-ci.org/abel-research/ampscan). New tests can be added to the repo. 

How to acknowledge
------------------

Find license [here](../master/LICENSE)
