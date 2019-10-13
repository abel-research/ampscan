.. image:: ampscan_header.svg
   :width: 100%
   :align: center

ampscan is an open-source Python package for analysis and visualisation of digitised surface scan data,
specifically for applications within Prosthetics and Orthotics (P&O), with an aim to improve evidence-
based clinical practice towards improved patient outcomes. The P&O industry is increasingly using surface 
scanners as part of clinical practice to capture patients' individual anatomic geometry, and design 
personalised devices. ampscan gives clinicians access to powerful tools to enhance their records and the 
evidence-base behind their practice. It gives researchers the capability to analyse data in a robust manner, 
and the project’s open-source distribution enables the community to contribute to the tool’s development, 
for example towards a mutually agreed standards of metrics and results presentation. 

This package has been designed to be accessible for researchers with only a limited knowledge of Python. 
Therefore, analysis procedures can all be accessed using the lightweight Graphical User Interface. 

ampscan relies heavily on numpy_ and scipy_ to perform 
mathematical operations with visualisation handled by PyQt_
and VTK_. The package is still under development by researchers at the Amputee BioEngineering Lab (ABEL) at University of Southampton. 
The foundations of this toolbox were developed in research funded by:
- the UK's Engineering and Physical Sciences Research Council (EPSRC), grants EP/M508147/1 and EP/M000303/1, and
- the UK's Royal Academy of Engineering (RAEng), grant RF/130.
For full documentation, visit the ampscan_ website.

.. _numpy: http://www.numpy.org/
.. _SciPy: https://www.scipy.org/
.. _PyQt: https://riverbankcomputing.com/software/pyqt/intro
.. _VTK: https://www.vtk.org/
.. _ampscan: https://ampscan.readthedocs.io/en/latest/

Installing ampscan
-------------------

ampscan has a number of dependencies, namely; NumPy, SciPy, Matplotlib, PyQt and vtk. We recommend using 
conda to deal with these. Before installation, ensure your environment is using Python 3. 

Install dependencies using conda:

``conda install numpy scipy pyqt matplotlib vtk==8.1.0``

For the most up to date version of ampscan, clone directly from the gitlab repository using:

``git clone https://github.com/abel-research/ampscan``

Navigate to the `ampscan/` directory and run a pip install using:

``pip install -e .``

ampscan will soon be available on pip once v0.1 is released 


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

