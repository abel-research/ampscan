# -*- coding: utf-8 -*-
"""
Package for dealing with smoothing functions for the AmpObject mesh
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk
"""

from itertools import count
import numpy as np
import copy

class smoothMixin(object):
    
    def lp_smooth(self, n=1, brim = True):
        r"""
        Function to apply a Laplacian smooth to the mesh. This method replaces 
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

    def hc_smooth(self, n=1 ,beta=0.6, brim=True, norms = True):
        r"""
        Function to apply a Humphrey’s Classes smooth to the mesh. Note, this assumes
        that alpha=0 (ie the original point through the iteration has no effect). 
        If beta=1, then this effectively acts as the Laplacian smooth 

        Parameters
        ----------
        
        n: int, default 1
            number of iterations of smoothing
        beta: float, default 0.6
            scalar between [0, 1] which dictates influence of distance from adjacent to original point.  
            If beta=1, then this effectively acts as the Laplacian smooth 
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
                # calculate new Laplacian location 
                p = adj.mean(axis=0)
                # Distance between Laplacian and original 
                b = p - q
                # Mean distance adjacent between original 
                d = (adj - q).mean(axis=0)
                # Based upon beta, get the updated location 
                self.vert[j, :] = q + beta*b - (1-beta)*d
        if norms is True:
            self.calcNorm()
            self.calcVNorm()
    
    def adjustCoincident(self, maxiter = 10, beta = 1):
        r"""
        Adjust any coincident vertices via a hc smooth
        """
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
        for i in range(maxiter):
            # List all vertices 
            vert = copy.deepcopy(self.getVert())
            neighVerts = vert[self.edges[row, 1-col], :]
            unq_vert, indC, unq_count = np.unique(vert, return_inverse=True, return_counts=True, axis=0)
            vert_count = unq_count[indC]
            vRange = np.arange(vert.shape[0])
            vRange = vRange[vert_count > 1]
            if vRange.size == 0:
                break
            for j in vRange:
                # Get the adjacent vertices
                adj = neighVerts[ndx[j]:ndx[j+1]]
                # Get the original vertex
                q = self.vert[j, :]
                # calculate new Laplacian location 
                p = adj.mean(axis=0)
                # Distance between Laplacian and original 
                b = p - q
                # Mean distance adjacent between original 
                d = (adj - q).mean(axis=0)
                # Based upon beta, get the updated location 
                self.vert[j, :] = q + beta*b - (1-beta)*d
        self.calcNorm()
        self.calcVNorm()

    def smoothValues(self, n=1):
        """
        Function to apply a simple Laplacian smooth to the values array. 
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
            