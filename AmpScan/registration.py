# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 16:07:10 2017

@author: js22g12
"""
import numpy as np
import pandas as pd 
from scipy import spatial
from core import AmpObject
"""
import os
path = ('J:\\Shared Resources\\AmpScan IfLS Team\\'
        '100 PYTHON\\STLReader')
filename = '01_PhantomShell_ICEM_3mm.stl'
filename2 = '01_PhantomShell_ICEM_3mm_write.stl'
baseline = 'B_PTB.stl'
target = 'B_NormalLiner.stl'
os.chdir(path)
ampObj = AmpObject(filename)
regObj = regObject(ampObj)
ampObj.vert.loc[0,:]
regObj.vert.loc[0,:]
ampObj.icp()
regObj.icp()
regObj.registration()
ampObj.registration()

Data = AmpObject(target)
Data.getBaseline(baseline)
Reg = regObject(Data)
Reg.reg_fast()


Use mesh object as parent class with standard function
and then inherit for all other classes ie socket, residuum, registered
Either create from filename, object or fv

Standard functions:
    Rotation 
    Translation 
    Read 
    Write 
    Normals
    Slice analyse
Child classes:
    Residuum
    Socket
    Registration (Target)
    Soft tissue mesh (Bones, Liner)
    FE mesh 
"""

class regObject(AmpObject):
    
    def __init__(self, Data=None, stype='AmpObj'):
        super(regObject, self).__init__(Data, stype)

    def registration(self, steps=1, baseline='limb',
                     target='socket', reg = 'reglimb', direct=True):
        """
        Function to register the regObject to the baseline mesh
        
        Parameters
        ----------
        Steps: int, default 1
            Number of iterations
        """
        bData = getattr(self, baseline)
        tData = getattr(self, target)
        bV = bData['vert']
        # Calculate the face centroids of the regObject
        tData['fC'] = tData['vert'][tData['faces']].mean(axis=1)
        # Construct knn tree
        tTree = spatial.cKDTree(tData['fC'])
        for step in np.arange(steps, 0, -1):
            # Index of 10 centroids nearest to each baseline vertex
            ind = tTree.query(bV, 10)[1]
            D = np.zeros(bV.shape)
            # Define normals for faces of nearest faces
            norms = tData['norm'][ind]
            # Get a point on each face
            fPoints = tData['vert'][tData['faces'][ind, 0]]
            # Calculate dot product between point on face and normals
            d = np.einsum('ijk, ijk->ij', norms, fPoints)
            t = d - np.einsum('ijk, ik->ij', norms, bV)
            # Calculate new points
            G = np.einsum('ijk, ij->ijk', norms, t)
            GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G)).argmin(axis=1)
            # Define vector from baseline point to intersect point
            D = G[np.arange(len(G)), GMag, :]
            bV = bV + D/step
        regData = dict(bData)
        regData['vert'] = bV
        setattr(self, reg, regData)
        self.calcError(baseline, reg, direct)

        
    def calcError(self, baseline='limb', target='reglimb', direct=True):
        # This is kinda slow
        bData = getattr(self, baseline)
        tData = getattr(self, target)
        if direct is True:
            values = np.linalg.norm(tData['vert'] - bData['vert'], axis=1)
            # Calculate vertex normals on target from normal of surrounding faces
            vNorm = np.zeros(tData['vert'].shape)
            for face, norm in zip(tData['faces'], tData['norm']):
                vNorm[face, :] += norm
            vNorm = vNorm / np.linalg.norm(vNorm, axis=1)[:, None]
            # Calculate the unit vector normal between corresponding vertices
            # baseline and target
            vector = (tData['vert'] - bData['vert'])/values[:, None]
            # Calculate angle between the two unit vectors using normal of cross
            # product between vNorm and vector and dot
            normcrossP = np.linalg.norm(np.cross(vector, vNorm), axis=1)
            dotP = np.einsum('ij,ij->i', vector, vNorm)
            angle = np.arctan2(normcrossP, dotP)
            polarity = np.ones(angle.shape)
            polarity[angle < np.pi/2] =-1.0
            tData['values'] = values * polarity
        else:
            tData['values'] = np.linalg.norm(tData['vert'] - bData['vert'],
                                           axis=1)
        
