# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 16:07:10 2017

@author: js22g12
"""
import numpy as np
from scipy import spatial
from .core import AmpObject

class registration(object):
    
    def __init__(self, baseline, target, method='point2plane', steps=5):
        self.b = baseline
        self.t = target
        self.steps = steps
        if method is not None:
            getattr(self, method)()
        
        
    def point2plane(self):
        """
        Function to register the regObject to the baseline mesh
        
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
        self.reg = AmpObject(bData, stype='reg')
        for step in np.arange(self.steps, 0, -1):
            # Index of 10 centroids nearest to each baseline vertex
            ind = tTree.query(self.reg.vert, 10)[1]
            D = np.zeros(self.reg.vert.shape)
            # Define normals for faces of nearest faces
            norms = self.t.norm[ind]
            # Get a point on each face
            fPoints = self.t.vert[self.t.faces[ind, 0]]
            # Calculate dot product between point on face and normals
            d = np.einsum('ijk, ijk->ij', norms, fPoints)
            t = d - np.einsum('ijk, ik->ij', norms, self.reg.vert)
            # Calculate new points
            G = np.einsum('ijk, ij->ijk', norms, t)
            GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G)).argmin(axis=1)
            # Define vector from baseline point to intersect point
            D = G[np.arange(len(G)), GMag, :]
            self.reg.vert += D/step
            self.reg.lp_smooth(1)
        
        self.reg.calcStruct()
        self.reg.values[:] = self.calcError(False)
        
    def calcError(self, direct):
        """
        A function within a function will not be documented

        """
        if direct is True:
            values = np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
            # Calculate the unit vector normal between corresponding vertices
            # baseline and target
            vector = (self.reg.vert - self.b.vert)/values[:, None]
            # Calculate angle between the two unit vectors using normal of cross
            # product between vNorm and vector and dot
            normcrossP = np.linalg.norm(np.cross(vector, self.t.vNorm), axis=1)
            dotP = np.einsum('ij,ij->i', vector, self.t.vNorm)
            angle = np.arctan2(normcrossP, dotP)
            polarity = np.ones(angle.shape)
            polarity[angle < np.pi/2] =-1.0
            values = values * polarity
            return values
        else:
            values = np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
            return values

