# -*- coding: utf-8 -*-
"""
Package for dealing with smoothing functions for the AmpObject mesh
Copyright: Joshua Steer 2018, Joshua.Steer@soton.ac.uk
"""

import numpy as np
import copy

class smoothMixin(object):
    
    def lp_smooth(self, n=1, brim = True):
        r"""
        Function to apply a laplacian smooth to the mesh. This method replaces 
        each vertex with the mean of its connected neighbours 

        Parameters
        ----------
        
        n: int, default 1
            number of iterations of smoothing
        
        """
        if brim is True:
            eidx = (self.faceEdges == -99999).sum(axis=1).astype(bool)
            vBrim = np.unique(self.edges[eidx, :])
        else: vBrim = []
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
            vRange = np.arange(self.vert.shape[0])
            log = np.isin(vRange, vBrim)
            vRange = vRange[~log]
            for j in vRange:
                # Calculate the mean of the vertex set
                self.vert[j, :] = neighVerts[ndx[j]:ndx[j+1]].mean(axis=0)
        self.calcNorm()
        self.calcVNorm()
    
    def smoothValues(self, n=1):
        """
        Function to apply a simple laplacian smooth to the values array. 
        Identical to the vertex smoothing expect it applies the smoothing 
        to the values

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
            