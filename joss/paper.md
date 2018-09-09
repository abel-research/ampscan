---
title: 'AmpScan: A lightweight Python package for clinical analysis of prosthetics and orthotics'
date: 03 September 2018
bibliography: paper.bib
---
# Summary

The increasing accessibility of digitised surface scanners are increasingly used. In particular, these devices are being used with prosthetics and orthotics clinics where they are used to capture the patients individual geometry. These scans are imported into computer-aided design packages in order to generate patient-specific medical devices. Despite this, the analysis performed on these scans is limited denying clinicans access to a large amount of data which could be used to inform and improve clinical practice. 

In a previously published paper [@Dickinson:2016], a method was detailed for comparing between pairs of surface scans using alignment, registration and visualisation. In this paper, this method was used for evaluation of the accuracy and inter- and intra-reliability of the scanners. Further studies have also demonstrated using this package for comparing the consistency of casting techniques [Dickinson: ], statistical shape modelling across the population [@Worsley: ISPO World] and quantifying rectifications between the residual limb and the prosthetic socket [@Steer: AOPA]. 

[A Graphical summary of the AmpScan process](AmpScan_Overview.png)

This method was written in MATLAB, however, this was considered restrictive for other researchers to access as they may not possess a MATLAB license.  In order to maximise access to the developed techniques and improve performance, especially for 3D visualisation, the methods were rewritten from scratch within Python, including updated algorithms for each stage of the aforementioned process. 

The AmpScan package has been designed with clinical researchers in mind, with an appreciation that they may not have an extensive knowledge of code. To this aim, this software has been developed in Python and leverages the commonly used libraries of NumPy, SciPy, matplotlib, vtk and pyqt. As such, full functionality of the software can be accessed without requiring additional installs. The core analysis of the package can be carried out with, additionally, a simple GUI has been supplied to allow the user to access the core functionality of AmpScan without scripting.  

The core functionality of AmpScan is summarised below with a more detailed description available in the online [documentation](https://ampscan.readthedocs.io/en/latest/):
- **[AmpObject](https://ampscan.readthedocs.io/en/latest/source/AmpScan.html#AmpScan.core.AmpObject)**: this is the key object of the package and holds the key data and methods. The key data held within the AmpObject is the mesh data including arrays of the vertices, faces, normals and field values. Additionally, the vtk actor for visualisation is also stored. The [core](https://ampscan.readthedocs.io/en/latest/source/core.html) methods of the AmpObject include imports for .stl files, saving .stl files, rotation and translation. Additional methods are added via mixins for [analysis](https://ampscan.readthedocs.io/en/latest/source/analyse.html), [smoothing](https://ampscan.readthedocs.io/en/latest/source/smooth.html), [trimming](https://ampscan.readthedocs.io/en/latest/source/trim.html) and [visualisation](https://ampscan.readthedocs.io/en/latest/source/ampVis.html). 
- **[Alignment](https://ampscan.readthedocs.io/en/latest/source/align.html)**: This takes two AmpObjects, one fixed and one moving, and applies a rigid transformation to the moving AmpObject in order to minimise the spatial error between the two AmpObjects. This is performed through an Iterative Closest Point (ICP) algorithm.
- **[Registration](https://ampscan.readthedocs.io/en/latest/source/registration.html)**: This takes two AmpObjects, one baseline and one target, and applied a non-rigid transformation to morph the baseline vertices onto the surface of the target. This is performed by a point-to-plane method. The registered shape ends up with the same number of vertices and connectivity as the baseline, thereby enabling shape comparison between the shapes.
- **[Statistical Shape Modelling](https://ampscan.readthedocs.io/en/latest/source/ssm.html)**: This provides methods for analysing the shapes of scans across a population using the Principal Component Analysis method. 
- **[Graphical User Interface]**: This enables visualisation to multiple AmpObjects within a single window, giving access to the automated and manual alignment tools as well as registration. This faciliates the core analysis of the scan data for users who are not experienced Python users. 

Other packages perform the specific tasks of AmpScan more comprehensively such as [mayavi](https://docs.enthought.com/mayavi/mayavi/index.html) for scientific data visualisation, [open3d](http://www.open3d.org/docs/getting_started.html) for alignment and registration techniques. We encourage researchers who have developed their own alignment and registration algorithms in python, further the package does not contain any mesh fixing tools that may be required from messy scans. Until such methods are implemented, the authors recommend [meshlab](http://www.meshlab.net/) which also contains methods for alignment and visualisation.

# Acknowledgements 


# References