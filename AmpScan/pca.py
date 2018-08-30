# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 15:03:12 2018

@author: js22g12
"""

import os
import numpy as np
from .core import AmpObject
from .registration import registration


class pca(object):
    
    def __init__(self):
        self.shapes = []
        
        
    def setBaseline(self, baseline):
        self.baseline = AmpObject(baseline, 'limb')
        
        
    def importFolder(self, path, unify=True):
        r"""
        Function to import multiple stl files from folder
        """
        self.fnames = [f for f in os.listdir(path) if f.endswith('.stl')]
        self.shapes = [AmpObject(path + f, 'limb', unify=unify) for f in self.fnames]
        for s in self.shapes:
            s.lp_smooth(3, brim=True)
        
    def sliceFiles(self, height):
        r"""
        Function to slice
        """
        for s in self.shapes:
            s.planarTrim(height)
        
    def register(self, scale=None, save=None, baseline=True):
        r"""
        Function to register all the shapes to a baseline
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
        Function to run mean centered pca on the registered data
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
        
        Notes
        -----
        Update so works with stdevs
        """
        if scale == 'eigs':
            sf = (self.pca_U * sfs).sum(axis=1)
        elif scale == 'std':
            sf = (self.pca_U * self.pc_stdevs * sfs).sum(axis=1)
        return self.pca_mean + sf
