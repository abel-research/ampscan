AmpScan
=======

AmpScan is a Python package that provides matrix manipulation tools specifically for 
the design of prosthetic sockets. It provides functions for handling common design workflows 
such as importing, aligning and registering meshes. AmpScan relies heavily on [NumPy](http://www.numpy.org/) 
and [SciPy](https://www.scipy.org/) to perform mathematical operations with vizualisation handled by 
[PyQt](https://riverbankcomputing.com/software/pyqt/intro) and [VTK](https://www.vtk.org/). The package is 
still under development by researchers at the University of Southampton.

Installation
------------

AmpScan has a number of dependencies, we recommend using conda to deal with these. To create a new 
environment to run AmpScan in:  

``conda create -n env_name python=3 numpy scipy pyqt matplotlib``

``conda install -c conda-forge vtk=8.1.0``

For the most up to date version of AmpScan, clone directly from the gitlab repository into a virtual environment using:

``git clone https://git.soton.ac.uk/js22g12/AmpScan.git``

Navigate to the `AmpScan/` directory and run a pip install using:

``pip install -e .``

A pip installation is also available through test PyPI (not latest version) using:

``$ pip install --index-url https://test.pypi.org/simple/ AmpScan``


## How to acknowledge

Find license [here](../LICENSE)
