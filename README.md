AmpScan
=======

AmpScan is a Python package that provides matrix manipulation tools specifically for 
the design of prosthetic sockets. It provides functions for handling common design workflows 
such as importing, aligning and registering meshes. AmpScan relies heavily on [NumPy](http://www.numpy.org/) 
and [SciPy](https://www.scipy.org/) to perform mathematical operations with vizualisation handled by 
[PyQt](https://riverbankcomputing.com/software/pyqt/intro) and [VTK](https://www.vtk.org/). The package is 
still under development by researchers at the University of Southampton. For full documentation, 
visit the [AmpScan website](https://ampscan.readthedocs.io/en/latest/).

Installing with Conda (Recommended)
-----------------------------------

AmpScan has a number of dependencies, we recommend using conda to deal with these. To create a new 
environment to run AmpScan in:  

``conda create -n env_name python=3 numpy scipy pyqt matplotlib``

``conda install -c conda-forge vtk=8.1.0``

Installing with Pip
-------------------

AmpScan has a number of dependencies, namely; NumPy, SciPy, Matplotlib, PyQt and vtk. Before 
installing, ensure you have the latest version of pip using:

``python -m pip install --upgrade pip``

Then install the dependencies using:

``pip install numpy matplotlib scipy pyqt5 vtk==8.1.0``

You can then install AmpScan from test PyPI using:

``python -m pip install --index-url https://test.pypi.org/simple/ AmpScan``

TODO: update to pip install (not test PyPI)

Developer Install
-----------------

For the most up to date version of AmpScan, clone directly from the gitlab repository using:

``git clone https://git.soton.ac.uk/js22g12/AmpScan.git``

Navigate to the `AmpScan/` directory and run a pip install using:

``pip install -e .``

How to acknowledge
------------------

Find license [here](../LICENSE)
