# -*- coding: utf-8 -*-
"""
Package for using AmpScan to run statistical shape modeling using mean-centered principal component analysis 
on a group of scans 
Copyright: Joshua Steer 2018, Joshua.Steer@soton.ac.uk
"""

import os
import numpy as np
from .core import AmpObject
from .registration import registration


class pca(object):
    r"""
    Principal Component Analysis methods for a training data set of AmpObjects
    Used to investigate modes of variation across the population 
    
    Examples
    --------
    >>> p = pca()
    >>> p.importFolder('/path/')
    >>> p.baseline('dir/baselinefh.stl')
    >>> p.register(save = '/regpath/')
    >>> p.pca()
    >>> sfs = [0, 0.1, -0.5 ... 0]
    >>> newS = p.newShape(sfs)
    
    """
    
    def __init__(self):
        self.shapes = []
        
        
    def setBaseline(self, baseline):
        r"""
        Function to set the baseline mesh used for registration of the 
        pca training data meshes
        
        Parameters
        ----------
        baseline: str
            The file handle of the stl file used as the baseline
            
        """
        self.baseline = AmpObject(baseline, 'limb')
        
        
    def importFolder(self, path, unify=True):
        r"""
        Function to import multiple stl files from folder into the pca object 
        
        Parameters
        ----------
        path: str
            The path to the folder containing the stl files to be used as the 
            training data for the PCA model
        unify: bool, default True
            Designmate whether to unify the vertices on stl import 

        """
        self.fnames = [f for f in os.listdir(path) if f.endswith('.stl')]
        self.shapes = [AmpObject(path + f, 'limb', unify=unify) for f in self.fnames]
        for s in self.shapes:
            s.lp_smooth(3, brim=True)
        
    def sliceFiles(self, height):
        r"""
        Function to run a planar trim on all the training data for the PCA 
        model
        
        Parameters
        ----------
        height: float
            The hight of the z slice plane 

        """
        for s in self.shapes:
            s.planarTrim(height)
        
    def register(self, scale=None, save=None, baseline=True):
        r"""
        Register all the AmpObject training data to the baseline AmpObject 
        
        Parameters
        ----------
        scale: float, default None
            scale parameter used for the registration
        save: str, default None
            If not None, this will save the registered
        baseline: bool, default True
            If True, the baseline AmpObject will also be included in the PCA 
            model
        
        """
        self.registered = []
        for t in self.shapes:
            r = registration(self.baseline, t, fixBrim=True, steps=5, scale=scale, smooth=1, neigh=50).reg
            r.lp_smooth()
            self.registered.append(r)
        if save is not None:
            for f, r in zip(self.fnames, self.registered):
                r.save(save + f)
        self.X = np.array([r.vert.flatten() for r in self.registered]).T
        if baseline is True:
            self.X = np.c_[self.X, self.baseline.vert.flatten()]
        
        
    def pca(self):
        r"""
        Function to run mean centered pca using a singular value decomposition 
        method
        
        """
        self.pca_mean = self.X.mean(axis=1)
        X_meanC = self.X - self.pca_mean[:, None]
        (self.pca_U, self.pca_S, self.pca_V) = np.linalg.svd(X_meanC, full_matrices=False)
        self.pc_weights = np.dot(np.diag(self.pca_S), self.pca_V)
        self.pc_stdevs = np.std(self.pc_weights, axis=1)
    
    def newShape(self, sfs, scale = 'eigs'):
        r"""
        Function to calculate a new shape based upon the eigenvalues 
        or stdevs
        
        Parameters
        ----------
        sfs: array_like
            An array of scaling factors to generate the new shape. This 
            must be of the same length as the number of principal components
        scale: str, default 'eigs'
            A string to indicate whether the sfs correspond to mode energy or
            to standard deviations about the mean

        """
        try: len(sfs) == len(self.pc_stdevs)
        except: ValueError('sfs must be of the same length as the number of '
                           'principal components')
        if scale == 'eigs':
            sf = (self.pca_U * sfs).sum(axis=1)
        elif scale == 'std':
            sf = (self.pca_U * self.pc_stdevs * sfs).sum(axis=1)
        return self.pca_mean + sf
