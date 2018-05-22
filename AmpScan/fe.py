# -*- coding: utf-8 -*-
"""
Created on Wed Nov 01 14:13:50 2017

@author: js22g12
"""

import numpy as np
from numpy.linalg import solve

class feMixin(object):
    
    def addFE(self, files):
        if len(files) == 1:
            data = np.load(files[0], encoding='bytes').item()
            for k in list(data.keys()):
                data[str(k, 'utf-8')] = data.pop(k)
            for k, v in data.items():
                setattr(self, k, v)
        if len(files) == 3:
            data = {}
            names = ['vert', 'faces', 'values']
            for n, f in zip(names, files):
                data[n] = np.loadtxt(f)
        self.getSurf()
        
        
    def getSurf(self):
        # Find verts with a pressure value for external surface
        valInd = self.values[:, 0].astype(int)
        # Find faces in array 
        log = np.isin(self.faces, valInd)
        f = self.faces[log].reshape([-1, 4])
        log = np.zeros(len(self.vert), dtype=bool)
        log[valInd] = True
        fInd = np.cumsum(log) - 1
        self.vert = self.vert[log, :]
        self.faces = fInd[f].astype(np.int64)
        self.values = np.array(self.values[:, 1])
        # order for ABAQUS hex element 
        self.edges = np.reshape(self.faces[:, [0, 1, 1, 2, 2, 3, 3, 0]], [-1, 2])
        self.edges = np.sort(self.edges, 1)
        # Unify the edges
        self.edges, indC = np.unique(self.edges, return_inverse=True, axis=0)
    
    def calcPPI(self):
        """
        Function to calculate the peak pressure indicies
        """
        self.values
    
    def calcGradients(self):
        """
        Function to calculate the gradients in values along z and theta
        """
        np.gradient(self.values)
    
    def addSurrogate(self, fname):
        self.surrogate = np.load(fname).item()
        surr = self.surrogate
        surr['sm_theta'] = 10 ** surr['sm_theta']

    def surrPred(self, x):
        surr = self.surrogate
        one = np.ones([125])
        eigs = np.zeros([20])
        for i in range(20):
            u = surr['sm_U'][:, : ,i]
            mu = surr['sm_mu'][i]
            y = surr['y'][:, i]
            theta = surr['sm_theta'][:,i]
            psi = np.exp(-np.sum(theta*np.abs(surr['x']-x)**2, axis=1))
            eigs[i] = mu + np.dot(psi.T, feMixin.comp(u, feMixin.comp(u.T,y-one*mu)))
        sf = (surr['pc_U'] * eigs).sum(axis=1)
        self.values[:] = surr['pc_mean'] + sf
    
    @staticmethod
    def comp(a, b):
        return solve(np.dot(a.T, a), np.dot(a.T, b))