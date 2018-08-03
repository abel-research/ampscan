# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 16:07:10 2017

@author: js22g12
"""
import numpy as np
import pandas as pd 
import copy
from scipy import spatial
from .core import AmpObject

#"""
#import os
#path = ('J:\\Shared Resources\\AmpScan IfLS Team\\'
#        '100 PYTHON\\STLReader')
#filename = '01_PhantomShell_ICEM_3mm.stl'
#filename2 = '01_PhantomShell_ICEM_3mm_write.stl'
#baseline = 'B_PTB.stl'
#target = 'B_NormalLiner.stl'
#os.chdir(path)
#ampObj = AmpObject(filename)
#regObj = regObject(ampObj)
#ampObj.vert.loc[0,:]
#regObj.vert.loc[0,:]
#ampObj.icp()
#regObj.icp()
#regObj.registration()
#ampObj.registration()

#Data = AmpObject(target)
#Data.getBaseline(baseline)
#Reg = regObject(Data)
#Reg.reg_fast()
#
#
#Use mesh object as parent class with standard function
#and then inherit for all other classes ie socket, residuum, registered
#Either create from filename, object or fv
#
#Standard functions:
#    Rotation 
#    Translation 
#    Read 
#    Write 
#    Normals
#    Slice analyse
#Child classes:
#    Residuum
#    Socket
#    Registration (Target)
#    Soft tissue mesh (Bones, Liner)
#    FE mesh 
#"""

def registration(baseline, target, method='default', steps=5, direct=True):
    """
    Function to register the regObject to the baseline mesh
    
    Parameters
    ----------
    Steps: int, default 1
        Number of iterations
    """
    bV = baseline.vert
    # Calc FaceCentroids
    fC = target.vert[target.faces].mean(axis=1)
    # Construct knn tree
    tTree = spatial.cKDTree(fC)
    for step in np.arange(steps, 0, -1):
        # Index of 10 centroids nearest to each baseline vertex
        ind = tTree.query(bV, 10)[1]
        D = np.zeros(bV.shape)
        # Define normals for faces of nearest faces
        norms = target.norm[ind]
        # Get a point on each face
        fPoints = target.vert[target.faces[ind, 0]]
        # Calculate dot product between point on face and normals
        d = np.einsum('ijk, ijk->ij', norms, fPoints)
        t = d - np.einsum('ijk, ik->ij', norms, bV)
        # Calculate new points
        G = np.einsum('ijk, ij->ijk', norms, t)
        GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G)).argmin(axis=1)
        # Define vector from baseline point to intersect point
        D = G[np.arange(len(G)), GMag, :]
        bV = bV + D/step
    bData = dict(zip(['vert', 'faces', 'values'], [bV, baseline.faces, baseline.values]))
    regObj = AmpObject(bData, stype='reg')
    regObj.lp_smooth(5)
    
    def calcError(baseline, regObj, direct=True):
        """
        A function within a function will not be documented

        """
        if direct is True:
            values = np.linalg.norm(regObj.vert - baseline.vert, axis=1)
            # Calculate the unit vector normal between corresponding vertices
            # baseline and target
            vector = (regObj.vert - baseline.vert)/values[:, None]
            # Calculate angle between the two unit vectors using normal of cross
            # product between vNorm and vector and dot
            normcrossP = np.linalg.norm(np.cross(vector, target.vNorm), axis=1)
            dotP = np.einsum('ij,ij->i', vector, target.vNorm)
            angle = np.arctan2(normcrossP, dotP)
            polarity = np.ones(angle.shape)
            polarity[angle < np.pi/2] =-1.0
            values = values * polarity
            return values
        else:
            values = np.linalg.norm(regObj.vert - baseline.vert, axis=1)
            return values

    #regObj.values[:] = calcError(baseline, regObj, False)
    return regObj

        
