# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:15:30 2017

@author: js22g12
"""

import numpy as np
from scipy import spatial
from scipy.optimize import minimize


def align(moving, static, method = 'P2P'):
    

    def icp():
        """
        Autmated alignment function between two 
        """
        tTree = spatial.cKDTree(self.baseline.vert)
        rot = np.array([0,0,0], dtype=float)
        res = minimize(self.calcDistError, rot, method='BFGS',
                       options={'gtol':1e-6, 'disp':True})
        
        
    def calcDistError(rot, tTree):
        Id = np.identity(3)
        for i in range(3):
            if rot[i] != 0:
                ax = Id[i, :]
                ang = np.deg2rad(rot[i])
                dot = np.reshape(self.vert[:, 0] * ax[0] +
                                 self.vert[:, 1] * ax[1] +
                                 self.vert[:, 2] * ax[2], (-1, 1))
                self.vert = (self.vert * np.cos(ang) +
                             np.cross(ax, self.vert) * np.sin(ang) +
                             np.reshape(ax, (1, -1)) * dot * (1-np.cos(ang)))
        dist = tTree.query(self.vert, 10)[0]
        dist = dist.min(axis=1)
        return dist.sum()
    
    return moving

def rotMatrix(R, ang='rad'):
    if ang == 'deg':
        R = np.deg2rad(R)
    angx = R[0]
    angy = R[1]
    angz = R[2]
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(angx), -np.sin(angx)],
                   [0, np.sin(angx), np.cos(angx)]])
    Ry = np.array([[np.cos(angy), 0, np.sin(angy)],
                   [0, 1, 0],
                   [-np.sin(angy), 0, np.cos(angy)]])
    Rz = np.array([[np.cos(angz), -np.sin(angz), 0],
                   [np.sin(angz), np.cos(angz), 0],
                   [0, 0, 1]])
    R = np.dot(np.dot(Rz, Ry), Rx)
    return R