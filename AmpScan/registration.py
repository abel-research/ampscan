# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 16:07:10 2017

@author: js22g12
"""
import numpy as np
import copy
from scipy import spatial
from .core import AmpObject

class registration(object):
    
    def __init__(self, baseline, target, method='point2plane', steps=5):
        self.b = baseline
        self.t = target
        self.steps = steps
        if method is not None:
            getattr(self, method)()
        
        
    def point2plane(self, neigh = 10, inside = True, smooth=0):
        """
        Function to register the regObject to the baseline mesh
        
        Need to add test to ensure inside triangle, currently not performing
        that so ending up in weird places on plane 
        
        Parameters
        ----------
        Steps: int, default 1
            Number of iterations
        """
        # Calc FaceCentroids
        fC = self.t.vert[self.t.faces].mean(axis=1)
        # Construct knn tree
        tTree = spatial.cKDTree(fC)
        bData = dict(zip(['vert', 'faces', 'values'], 
                         [self.b.vert, self.b.faces, self.b.values]))
        regData = copy.deepcopy(bData)
        self.reg = AmpObject(regData, stype='reg')
        for step in np.arange(self.steps, 0, -1, dtype=float):
            # Index of 10 centroids nearest to each baseline vertex
            ind = tTree.query(self.reg.vert, neigh)[1]
#            D = np.zeros(self.reg.vert.shape)
            # Define normals for faces of nearest faces
            norms = self.t.norm[ind]
            # Get a point on each face
            fPoints = self.t.vert[self.t.faces[ind, 0]]
            # Calculate dot product between point on face and normals
            d = np.einsum('ijk, ijk->ij', norms, fPoints)
            t = d - np.einsum('ijk, ik->ij', norms, self.reg.vert)
            # Calculate the vector from old point to new point
            G = np.einsum('ijk, ij->ijk', norms, t)
            # Ensure new points lie inside points otherwise set to 99999
            # Find smallest distance from old to new point 
            if inside is False:
                GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G))
                GInd = GMag.argmin(axis=1)
            else:
                GInd = GInd = self.calcBarycentric(G, ind)
            # Define vector from baseline point to intersect point
            D = G[np.arange(len(G)), GInd, :]
            self.reg.vert += D/step
            if smooth > 0:
                self.reg.lp_smooth(smooth)
        
        self.reg.calcStruct()
#        self.reg.values[:] = self.calcError(False)
        self.reg.values[:] = self.calcError(False)
        
    def calcError(self, direct):
        """
        A function within a function will not be documented

        """
        if direct is True:
            self.b.calcVNorm()
            values = np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
            # Calculate the unit vector normal between corresponding vertices
            # baseline and target
            vector = (self.reg.vert - self.b.vert)/values[:, None]
            # Calculate angle between the two unit vectors using normal of cross
            # product between vNorm and vector and dot
            normcrossP = np.linalg.norm(np.cross(vector, self.b.vNorm), axis=1)
            dotP = np.einsum('ij,ij->i', vector, self.b.vNorm)
            angle = np.arctan2(normcrossP, dotP)
            polarity = np.ones(angle.shape)
            polarity[angle < np.pi/2] =-1.0
            values = values * polarity
            return values
        else:
            values = np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
            return values
        
    def calcBarycentric(self, G, ind):
        P0 = self.t.vert[self.t.faces[ind, 0]]
        P1 = self.t.vert[self.t.faces[ind, 1]]
        P2 = self.t.vert[self.t.faces[ind, 2]]
        NP = self.reg.vert[:, None, :] + G
        
        v0 = P2 - P0
        v1 = P1 - P0
        v2 = NP + G - P0
        
        d00 = np.einsum('ijk, ijk->ij', v0, v0)
        d01 = np.einsum('ijk, ijk->ij', v0, v1)
        d02 = np.einsum('ijk, ijk->ij', v0, v2)
        d11 = np.einsum('ijk, ijk->ij', v1, v1)
        d12 = np.einsum('ijk, ijk->ij', v2, v2)
        
        denom = d00*d01 - d01*d01
        u = (d11 * d02 - d01 * d12)/denom
        v = (d00 * d12 - d01 * d02)/denom
        # Test if inside 
        logic = (u >= 0) * (v >= 0) * (u + v < 1)
        
        P = np.stack([P0, P1, P2],axis=3)
        PG = NP[:, :, :, None] - P
        PD =  np.linalg.norm(PG, axis=3)
        pdx = PD.argmin(axis=2)
        i, j = np.meshgrid(np.arange(P.shape[0]), np.arange(P.shape[1]))
        nearP = P[i.T, j.T, :, pdx]
        nearG = nearP - self.reg.vert[:, None, :]
        G[~logic, :] = nearG[~logic, :] 
        GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G))
        GInd = GMag.argmin(axis=1)
        return GInd
