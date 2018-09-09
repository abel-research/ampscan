.. image:: AmpScanlogo.svg
   :width: 30%
   :align: center


AmpScan
=======

AmpScan is a Python package that provides matrix manipulation tools specifically for 
the design of prosthetic sockets. It provides functions for handling common design workflows 
such as importing, aligning and registering meshes. AmpScan relies heavily on `NumPy`_ and 
`SciPy`_ to perform mathematical operations with vizualisation handled by `PyQt`_ and `VTK`_. 
The package is still under active development by researchers at the University of Southampton 
- this documentation should be considered the 'go-to' for anyone interested in using or 
developing AmpScan.

.. _numpy: http://www.numpy.org/
.. _SciPy: https://www.scipy.org/
.. _PyQt: https://riverbankcomputing.com/software/pyqt/intro
.. _VTK: https://www.vtk.org/


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

``git clone https://git.soton.ac.uk/js22g12/AmpScan.git``

Navigate to the `AmpScan/` directory and run a pip install using:

``pip install -e .``


Getting Started
---------------

.. toctree::
   :maxdepth: 3

   exampleDemos


Developers Guide
----------------
.. toctree::
   :maxdepth: 1
   
   code
   LICENSE

