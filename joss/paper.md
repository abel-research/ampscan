---
title: 'ampscan: A lightweight Python package for shape analysis of prosthetics and orthotics'
tags:
- Python
- prosthetics
- orthotics
- scanning
- meshes
- measurement
authors:
 - name: Joshua W Steer
   orcid: 0000-0002-6288-1347
   affiliation: 1
 - name: Oliver Stocks
   affiliation: 1
 - name: Jack Parsons
   affiliation: 1 
 - name: Peter R Worsley
   orcid: 0000-0003-0145-5042
   affiliation: 2
 - name: Alexander S Dickinson
   orcid: 0000-0002-9647-1944
   affiliation: 1
affiliations:
 - name: Bioengineering Sciences Research Group, School of Engineering, Faculty of Engineering and Physical Sciences, University of Southampton
   index: 1
 - name: Clinical Academic Facility, School of Health Sciences, Faculty of Environment and Life Sciences, University of Southampton
   index: 2
date: 04 November 2019
bibliography: paper.bib
---
# Summary

The increasing accessibility of surface scanners is giving users the ability to accurately digitise the 3D surface geometry of real world objects which may then be manufactured by CNC machining or 3D printing. In addition to hobbyist applications, these devices are being increasingly used within the medical field, for example in prosthetics and orthotics clinics to capture the patients' individual limb geometry. These scans are imported into computer-aided design packages to generate patient-specific medical devices, such as prosthetic sockets, spinal braces or ankle-foot orthoses. This increasing digitsiation of patient data provides great potential for analysis in order to inform and improve clinical practice. While this has been an area of academic interest for several decades, clinical use is limited to date. One of the reasons for this is the lack of tools available for clinicians to analyse the geometry of their patient datasets. 

Building on foundational work published by Zachariah, Sorenson and Sanders [@Sanders:2005], in a previously published paper [@Dickinson:2016] we detailed a method for comparing pairs of surface scans using alignment, registration and visualisation. This enabled extraction of key measurements for evaluation of the accuracy and reliability of clinically-used scanners. Further studies have also demonstrated using this package for comparing the consistency of casting techniques [@Dickinson:APOSM], statistical shape modeling across the population [@Steer:BMMB] and quantifying rectifications between the residual limb and the prosthetic socket [@Steer:AOPA]. 

This method was written in MATLAB, although this was considered restrictive for other researchers to access as they may not possess a relevant license.  In order to maximise access to the developed techniques and improve performance, especially for 3D visualisation, the methods were rewritten from scratch within Python, including updated algorithms for each stage of the process. 

The ampscan package has been designed with a range of user groups in mind, from practicing clinicians to biomedical engineering researchers, with an appreciation that they may not have an extensive background in coding. To this aim, the software has been developed in Python and leverages the commonly used libraries of NumPy, SciPy, matplotlib, vtk and pyqt. As such, full functionality of the software can be accessed without requiring additional installs. The core analysis of the package can be carried out either within a script-based environment, or with the supplied lightweight graphical user interface [@Steer:ISPO].  

![A graphical summary of a typical ampscan process. a) Importing a pair of scans, b) Automatically snap centres, c) Align using ICP algorithm, d) Register and visualise shape deviation and e) Automatically analyse the registered scan](AmpScan_Overview.png)

The typical ampscan process is demonstrated above (Figure 1) and the core functionality summarised below, with a more detailed description available in the online [documentation](https://ampscan.readthedocs.io/en/latest/):

- **[AmpObject](https://ampscan.readthedocs.io/en/latest/source/core.html)**: this is the core object of the package and holds the key data and methods. The key data held within the AmpObject is the mesh data including arrays of the vertices, faces, normals and field values. The vtk actor for visualisation is also stored. The [core](https://ampscan.readthedocs.io/en/latest/source/core.html) methods of the AmpObject include imports for .stl files, saving .stl files, rotation and translation. Further methods on the core AmpObject include [smoothing](https://ampscan.readthedocs.io/en/latest/source/smooth.html), [trimming](https://ampscan.readthedocs.io/en/latest/source/trim.html) and [visualisation](https://ampscan.readthedocs.io/en/latest/source/ampVis.html). 

- **[Alignment](https://ampscan.readthedocs.io/en/latest/source/align.html)**: This takes two AmpObjects, one fixed and one moving, and applies a rigid transformation to the moving AmpObject in order to minimise the spatial error between the two AmpObjects. This is performed through an Iterative Closest Point (ICP) algorithm.

- **[Registration](https://ampscan.readthedocs.io/en/latest/source/registration.html)**: This takes two AmpObjects, one baseline and one target, and applies a non-rigid transformation to morph the baseline vertices onto the surface of the target. This is performed by a point-to-plane method. The registered shape ends up with the same number of vertices and connectivity as the baseline, thereby enabling shape comparison.

- **[Analysis](https://ampscan.readthedocs.io/en/latest/source/analyse.html)**: This is used to extract key geometrical infomation about the shape, including volume and serial slice cross section areas and perimeters.

- **Graphical User Interface**: This enables visualisation of multiple AmpObjects within a single window, giving access to the automated and manual alignment tools as well as registration. This facilitates the core analysis of the scan data for people who are not experienced Python users. The Python version of the GUI is available in the [gui](https://github.com/abel-research/ampscan/tree/master/gui) folder from the git repo.

Other packages perform the specific tasks of ampscan more comprehensively such as mayavi for scientific data visualisation [@ramachandran2011mayavi], open3d for alignment and registration techniques [@Zhou2018], and GIBBON for integration with finite element modelling [@Moerman:GIBBON]. At this time, the package only contains limited mesh fixing tools that may be required for erroneous scans. Until such methods are implemented, the authors recommend meshlab which also contains methods for alignment and visualisation [@meshlab]. 

An ampscan [webapp](https://github.com/abel-research/ampscan_webapp) is currently in development to further increase accessibility of these tools for clinicians and researchers working across the growing field of bespoke digital medical device design, and enable them to perform standardised, accessible and reliable analysis, and enhance patient experience.

# Acknowledgments 
While the ampscan package was not funded directly, the authors would like to thank the following for their financial support:

- JWS: the University of Southampton’s EPSRC Doctoral Training Program (ref EP/M508147/1) and EUROSTARS project (ref 9396).

- PRW: the EPSRC-NIHR “Medical Device and Vulnerable Skin Network” (ref EP/M000303/1).

- ASD: the Royal Academy of Engineering, UK, (ref RF/130) and the EPSRC-NIHR "Global Challenges Research Fund" (ref EP/R014213/1).

Finally, the authors would like to thank the Research Software Group at the University of Southampton for all their support during the development of this software, as well as Omar Animashaun and Tim Dunn for their contributions to ampscan.  

# References
