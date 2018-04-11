# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 12:49:32 2017

@author: js22g12
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict
import AmpScan.cython_ext as cyext



class analyseMixin(object):

    def plot_slices(self, axis='Z', slWidth=10, stype=0):
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        # Find the brim edges 
        ind = np.where(data['faceEdges'][:,1] == -99999)
        # Define max Z from lowest point on brim
        maxZ = data['vert'][data['edges'][ind, :], 2].min()
        fig = plt.figure()
        fig.set_size_inches(6, 4.5)

        ax1 = fig.add_subplot(221, projection='3d')
        ax2 = fig.add_subplot(222)
        #Z position of slices 
        slices = np.arange(data['vert'][:,2].min() + slWidth,
                           maxZ, slWidth)
        polys = analyseMixin.create_slices_cy(data, slices, axis)
        PolyArea = np.zeros([len(polys)])
        for i, poly in enumerate(polys):
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
        self.addActor(stype='reglimb', CMap = self.CMapN2P)
        Im = self.genIm(actor=['reglimb'])
        ax4.imshow(Im, None)
        ax4.set_axis_off()
        plt.tight_layout()
        plt.show()
        
    @staticmethod
    def create_slices(data, slices, axis='Z'):
        vE = data['vert'][:,2][data['edges']]
        # Find all vertices below plane 
        polys = []
        for i, plane in enumerate(slices):
            ind = vE < plane
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
            j=0
            while True:
                try:
                    w = g[v].pop()
                except KeyError:
                    break
                g[w].remove(v)
                faceOrder[j] = v
                j+=1
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
            #Create poly from 
            polys.append(analyseMixin.planeEdgeintersect(EdgePoints, plane, axis=axis))
        return polys
    
    def create_slices_cy(data, slices, axis='Z'):
        vE = data['vert'][:,2][data['edges']]
        # Find all vertices below plane 
        polys = []
        for i, plane in enumerate(slices):
            ind = vE < plane
            # Select edges with one vertex above and one below the slice plane 
            validEdgeInd = np.where(np.logical_xor(ind[:,0], ind[:,1]))[0]
            validfE = data['faceEdges'][validEdgeInd, :].astype(int)
            faceOrder = cyext.logEuPath(validfE)
            #Get array of three edges attached to each face
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
#            polys.append(analyseMixin.planeEdgeintersect(EdgePoints, plane, axis=axis))
            polys.append(cyext.planeEdgeIntersect(EdgePoints, plane, 2))
        return polys




    @staticmethod
    def planeEdgeintersect(edges, plane, axis='Z'):
        # Define index of axis of plane slicing
        axisInd = 0 if axis == 'X' else 1 if axis == 'Y' else 2
        # Allocate intersect points array
        intersectPoints = np.zeros((edges.shape[0], 3))
        # Define the plane of intersect points
        intersectPoints[:, axisInd] = plane
        axesInd = np.array([0,1,2])[np.array([0,1,2]) != axisInd]
        for i in axesInd:
            intersectPoints[:, i] = (edges[:, i] +
                                     (plane - edges[:, axisInd]) *
                                     (edges[:, i+3] - edges[:, i]) /
                                     (edges[:, axisInd+3] - edges[:, axisInd]))
        return intersectPoints

