# -*- coding: utf-8 -*-
"""
Created on Wed Nov 01 14:13:50 2017

@author: js22g12
"""

import numpy as np

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
        valInd = self.values[:, 0].astype(int)
        log = np.isin(self.faces, valInd)
        f = self.faces[log].reshape([-1, 4])
        log = np.zeros(len(self.vert), dtype=bool)
        log[valInd] = True
        fInd = np.cumsum(log) - 1
        self.vert = self.vert[log, :]
        self.faces = fInd[f].astype(np.int64)
        self.values = np.array(self.values[:, 1])
        self.edges = np.reshape(self.faces[:, [0, 1, 0, 2, 0, 3, 1, 2, 1, 3, 2, 3]], [-1, 2])
        self.edges = np.sort(self.edges, 1)
        # Unify the edges
        self.edges, indC = np.unique(self.edges, return_inverse=True, axis=0)