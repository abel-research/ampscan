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
        if len(files) == 3:
            data = {}
            names = ['vert', 'faces', 'values']
            for n, f in zip(names, files):
                data[n] = np.loadtxt(f)
        self.FE = data
        self.getSurf()
        
    def getSurf(self):
        valInd = self.FE['values'][:, 0].astype(int)
        log = np.isin(self.FE['faces'], valInd)
        f = self.FE['faces'][log].reshape([-1, 4])
        log = np.zeros(len(self.FE['vert']), dtype=bool)
        log[valInd] = True
        fInd = np.cumsum(log) - 1
        self.FE['vert'] = self.FE['vert'][log, :]
        self.FE['faces'] = fInd[f].astype(np.int64)
        self.FE['values'] = np.array(self.FE['values'][:, 1])
        self.FE['edges'] = np.reshape(self.FE['faces'][:, [0, 1, 0, 2, 0, 3, 1, 2, 1, 3, 2, 3]], [-1, 2])
        self.FE['edges'] = np.sort(self.FE['edges'], 1)
        # Unify the edges
        self.FE['edges'], indC = np.unique(self.FE['edges'], return_inverse=True, axis=0)