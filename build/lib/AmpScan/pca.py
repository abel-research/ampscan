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
        
        
    def importFolder(self, path):
        r"""
        Function to import multiple stl files from folder
        """
        self.shapes = [AmpObject(f, 'limb') for f in 
                       os.listdir(path) if f.endswith('.stl')]
        
    def register(self):
        r"""
        Function to register all the shapes to a baseline
        """
        self.registered = [registration(self.baseline, t) for t in self.shapes]
        self.X = np.array([r.vert for r in self.registered])
        
    def pca(self):
        r"""
        Function to run mean centered pca on the registered data
        """
        self.pca_mean = self.X.mean(axis=1)
        X_meanC = self.X - self.pca_mean[:, None]
        (self.pca_U, self.pca_S, self.pca_V) = np.linalg.svd(X_meanC, full_matrices=False)
        self.pc_weights = np.dot(np.diag(self.pca_S), self.pca_V.T)
    
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
            sf = (self.pca_U * sfs).sum(axis=1)
        return self.pca_mean + sf
