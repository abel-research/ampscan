# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 12:49:32 2017

@author: js22g12
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict

class analyseMixin(object):

    def plot_slices(self, axis='Z', SliceWidth=3, stype=0):
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        # Find the brim edges 
        ind = np.where(np.isnan(data['faceEdges'][:,1]))[0]
        # Define max Z from lowest point on brim
        maxZ = data['vert'][data['edges'][ind, :], 2].min()
        fig = plt.figure()
        fig.set_size_inches(12, 9)

        ax1 = fig.add_subplot(221, projection='3d')
        ax2 = fig.add_subplot(222)
        #Z position of slices 
        slices = np.arange(data['vert'][:,2].min() + SliceWidth, maxZ, SliceWidth)
        PolyArea = np.zeros([len(slices)])
        for i, pos in enumerate(slices):
            # Create a slice for each z position 
            poly = analyseMixin.create_slice(data, pos, axis)
            ax1.plot(poly[:,0],
                     poly[:,1],
                     poly[:,2],
                     c='b')
            #SlicePolys[i, :] = poly
            # Compute area of slice
            area = 0.5*np.abs(np.dot(poly[:,0], np.roll(poly[:,1], 1)) -
                              np.dot(poly[:,1], np.roll(poly[:,0], 1)))
            PolyArea[i] = area
        
        extents = np.array([getattr(ax1, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:,1] - extents[:,0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(ax1, 'set_{}lim'.format(dim))(ctr - r, ctr + r)
        ax1.set_axis_off()
        ax2.plot(slices-slices[0], PolyArea)
        # Rendering of the limb scan
        ax3 = fig.add_subplot(2,2,3)
        self.addActor(stype='limb')
        Im = self.genIm(actor=['limb'])
        ax3.imshow(Im, None)
        ax3.set_axis_off()
        # Rendering of the rectification map 
        ax4 = fig.add_subplot(2,2,4)
        CMap = np.array([[212.0, 221.0, 225.0],
                         [31.0, 73.0, 125.0]])/255.0
        self.addActor(stype='reglimb', CMap = CMap)
        Im = self.genIm(actor=['reglimb'])
        ax4.imshow(Im, None)
        ax4.set_axis_off()
        plt.tight_layout()
        
    @staticmethod
    def create_slice(data, plane, axis='Z'):
        # Find all vertices below plane 
        ind = data['vert'][:,2][data['edges']] < plane
        # Select edges with one vertex above and one below the slice plane 
        validEdgeInd = np.where(np.logical_xor(ind[:,0], ind[:,1]))[0]
        validfE = data['faceEdges'][validEdgeInd, :].astype(int)
        g = defaultdict(set)
        faceOrder = np.zeros(len(validEdgeInd), dtype=int)
        # Run eularian path algorithm to order faces
        for v, w in validfE:
            g[v].add(w)
            g[w].add(v)
        v = validfE[0,0]
        i=0
        while True:
            try:
                w = g[v].pop()
            except KeyError:
                break
            g[w].remove(v)
            faceOrder[i] = v
            i+=1
            v = w
        # Get array of three edges attached to each face
        validEdges = data['edgesFace'][faceOrder, :]
        # Remove the edge that is not intersected by the plane
        edges = validEdges[np.isin(validEdges, validEdgeInd)].reshape([-1,2])
        # Remove the duplicate edge from order 
        e = edges.flatten()
        odx = np.argsort(e)
        inds = np.arange(1, len(e), 2)
        row = np.unravel_index(odx, e.shape)[0]
        mask = np.ones(len(e), dtype=bool)
        mask[row[inds]] = False
        sortE = e[mask]
        # Add first edge to end of array
        sortE = np.append(sortE, sortE[0])
        polyEdge = data['edges'][sortE]
        EdgePoints = np.c_[data['vert'][polyEdge[:,0], :], 
                           data['vert'][polyEdge[:,1], :]]
        # Create poly from 
        poly = analyseMixin.planeEdgeintersect(EdgePoints, plane, axis=axis)
        return poly

    def create_slice_fast(self, plane, axis='Z'):
        # Find all vertices below plane 
        ind = self.vert[:,2][self.edges] < plane
        # Select edges with one vertex above and one below the slice plane 
        validEdgeInd = np.where(np.logical_xor(ind[:,0], ind[:,1]))[0]
        validfE = self.faceEdges[validEdgeInd, :].astype(int)
        
        col0, col0ind = np.unique(validfE[:,0], return_index=True)
        f0 = np.c_[col0, validfE[col0ind, 1]]
        col0indrep = np.where(~np.isin(np.arange(len(validfE)), col0ind))[0]
        f1 = validfE[col0indrep, :]
        
        col1, col1ind = np.unique(validfE[:,1], return_index=True)
        f1 = np.r_[np.c_[col1, validfE[col1ind, 0]], f1]
        col1indrep = np.where(~np.isin(np.arange(len(validfE)), col1ind))[0]
        f0 = np.r_[f0, validfE[col1indrep, :][:, [1,0]]]
        
        f0_idx = np.argsort(f0[:,0])
        f1_idx = np.argsort(f1[:,0])
        
        h = dict(zip(f0[f0_idx, 0].tolist(),
                     np.c_[f0[f0_idx, 1], f1[f1_idx, 1]].tolist()))
        faceOrder = np.zeros(len(validEdgeInd), dtype=int)
        # Run eularian path algorithm to order faces
        v = validfE[0,0]
        for i in range(len(validEdgeInd)):
            w = h[v].pop()
            h[w].remove(v)
            faceOrder[i] = v
            v = w
        # Get array of three edges attached to each face
        validEdges = self.edgesFace[faceOrder, :]
        # Remove the edge that is not intersected by the plane
        edges = validEdges[np.isin(validEdges, validEdgeInd)].reshape([-1,2])
        # Remove the duplicate edge from order 
        e = edges.flatten()
        odx = np.argsort(e)
        inds = np.arange(1, len(e), 2)
        row = np.unravel_index(odx, e.shape)[0]
        mask = np.ones(len(e), dtype=bool)
        mask[row[inds]] = False
        sortE = e[mask]
        # Add first edge to end of array
        sortE = np.append(sortE, sortE[0])
        polyEdge = self.edges[sortE]
        EdgePoints = np.c_[self.vert[polyEdge[:,0], :], 
                           self.vert[polyEdge[:,1], :]]
        # Create poly from 
        poly = analyseMixin.planeEdgeintersect(EdgePoints, plane, axis=axis)
        return poly
    
    @staticmethod
    def planeEdgeintersect(edges, plane, axis='Z'):
        axisInd = 0 if axis == 'X' else 1 if axis == 'Y' else 2
        intersectPoints = np.zeros((edges.shape[0], 3))
        intersectPoints[:, axisInd] = plane
        axesInd = np.arange(0, 2, 1)[np.arange(0, 2, 1) != axisInd]
        for i in axesInd:
            intersectPoints[:, i] = (edges[:, i] +
                                     (plane - edges[:, axisInd]) *
                                     (edges[:, i+3] - edges[:, i]) /
                                     (edges[:, axisInd+3] - edges[:, axisInd]))
        return intersectPoints
