# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:25:23 2017

@author: js22g12
"""

import numpy as np
import copy

class smoothMixin(object):
    
    def lp_smooth(self, n=1):
        r"""
        Function to apply a simple laplacian smooth to the mesh

        Parameters
        ----------
        
        n: int, default 1
            number of iterations of smoothing
        
        """
        # Flatten the edges array to 1D
        e = self.edges.flatten()
        # Get the indicies to sort edges 
        o_idx = e.argsort()
        # Get indicies of sorted array where last of each vertex index 
        # occurs 
        ndx = np.searchsorted(e[o_idx], np.arange(len(self.vert)), 
                              side='right')
        ndx = np.r_[0, ndx]
        # Map indicies between flatted edges array and standard
        row, col = np.unravel_index(o_idx, self.edges.shape)
        for i in np.arange(n):
            # List all vertices 
            vert = copy.deepcopy(self.vert)
            neighVerts = vert[self.edges[row, 1-col], :]
            for j in np.arange(self.vert.shape[0]):
                # Calculate the mean of the vertex set
                self.vert[j, :] = neighVerts[ndx[j]:ndx[j+1]].mean(axis=0)
        self.calcNorm()
        self.calcVNorm()
    
    def smoothValues(self, n=1):
        """
        Function to apply a simple laplacian smooth to the values array

        Parameters
        ----------
        
        n: int, default 1
            number of iterations of smoothing
        """
        # Flatten the edges array to 1D
        e = self.edges.flatten()
        # Get the indicies to sort edges 
        o_idx = e.argsort()
        # Get indicies of sorted array where last of each vertex index 
        # occurs 
        ndx = np.searchsorted(e[o_idx], np.arange(len(self.values)), 
                              side='right')
        ndx = np.r_[0, ndx]
        # Map indicies between flatted edges array and standard
        row, col = np.unravel_index(o_idx, self.edges.shape)
        for i in np.arange(n):
            neighValues = self.values[self.edges[row, 1-col]]
            for j in np.arange(self.values.shape[0]):
                # Calculate mean of values set 
                self.values[j] = neighValues[ndx[j]:ndx[j+1]].mean()
            