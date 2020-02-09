# -*- coding: utf-8 -*-
"""
Package for dealing with smoothing functions for the AmpObject mesh
Copyright: Joshua Steer 2019, Joshua.Steer@soton.ac.uk
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

    def hc_smooth(self, beta=0.6, n=1, brim=True):
        r"""
        Function to apply a Humphrey’s Classes smooth to the mesh. Note, this assumes
        that alpha=0 (ie the original point through the iteration has no effect). 
        If beta=1, then this effectively acts as the laplacian smooth 

        Parameters
        ----------
        
        n: int, default 1
            number of iterations of smoothing
        beta: float, default 0.6
            scalar between [0, 1] which dictates influence of 
        brim: bool, default True
            If true, then this will not smooth the vertices on the brim
        
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
                # Get the adjacent vertices
                adj = neighVerts[ndx[j]:ndx[j+1]]
                # Get the original vertex
                q = self.vert[j, :]
                # calculate new laplacian location 
                p = adj.mean(axis=0)
                # Distance between laplacian and original 
                b = p - q
                # Mean distance adjacent between original 
                d = (adj - q).mean(axis=0)
                # Based upon beta, get the updated location 
                self.vert[j, :] = q + beta*b - (1-beta)*d
        self.calcNorm()
        self.calcVNorm()
    
    def smoothValues(self, n=1):
        """
        Function to apply a simple laplacian smooth to the values array. 
        Identical to the vertex smoothing except it applies the smoothing
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
            