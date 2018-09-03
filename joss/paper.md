---
title: 'AmpScan: A lightweight Python package for shape analysis'
date: 03 September 2018
bibliography: paper.bib
---
# Summary

Digitised surface scanners are incresingly used. In particular, 
Based upon MATLAB code from a previously published paper [@Dickinson:2016]

Alignment of files used an iterative closest point algorithm 
The authors recognise that these individual steps have been extensively documented in 
literature and 

In the name of simplicity for researchers, this package has been designed to be lightweight and curated for a specific application. 
Other packages perform the specific tasks of AmpScan more comprehensively such as [mayavi](https://docs.enthought.com/mayavi/mayavi/index.html) for scientfic data visualisation, [open3d](http://www.open3d.org/docs/getting_started.html) for alignment and registration techniques  

This is a lightweight package built mostly on Numpy. As such this requires minimal additional 
packages and simple install designed to be used by researchers without extensive software background. 

Those looking for a more comprehensive set of registration and algorithms are recommended to look for alternative 
software packages such as open3D. 

Simple visualisation is provided by adding a thin layer around the VTK package. Again those look

We encourage researchers who have developed their own alignment and registration algorithms in python, further the package does not contain any mesh fixing tools that may be required from messy scans. Until such methods are implemented, the authors recommend [meshlab](http://www.meshlab.net/) which also contains methods for alignment and visualisation. 



# References