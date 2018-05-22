# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:25:23 2017

@author: js22g12
"""

import numpy as np
import pandas as pd

class smoothMixin(object):
    
    def lp_smooth(self, n=1):

        """
        Function to apply a simple laplacian smooth to the mesh

        Parameters
        ---------
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
        # Map indicies between flatted edges array and standard
        row, col = np.unravel_index(o_idx, self.edges.shape)
        for i in np.arange(n):
            # List all vertices 
            neighVerts = self.vert[self.edges[row, 1-col], :]
            # Split into list with each array contating vertices
            spl = np.split(neighVerts, ndx[0:-1])
            # Get average of each array 
            vert = [vert.mean(axis=0) for vert in spl]
            # Write to the AmpObj
            self.vert[:, :] = np.array(vert)
    
    def smoothValues(self, n=1):
        """
        Function to apply a simple laplacian smooth to the values array
        """
        # Flatten the edges array to 1D
        e = self.edges.flatten()
        # Get the indicies to sort edges 
        o_idx = e.argsort()
        # Get indicies of sorted array where last of each vertex index 
        # occurs 
        ndx = np.searchsorted(e[o_idx], np.arange(len(self.values)), 
                              side='right')
        # Map indicies between flatted edges array and standard
        row, col = np.unravel_index(o_idx, self.edges.shape)
        for i in np.arange(n):
            # List all vertices 
            neighValues = self.values[self.edges[row, 1-col]]
            # Split into list with each array contating vertices
            spl = np.split(neighValues, ndx[0:-1])
            # Get average of each array 
            values = [val.mean() for val in spl]
            # Write to the AmpObj
            self.values[:] = np.array(values)
            