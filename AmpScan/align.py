# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:15:30 2017

@author: js22g12
"""

import numpy as np
import copy
import vtk
import math
from scipy import spatial
from scipy.optimize import minimize
from .core import AmpObject
from .ampVis import vtkRenWin


class align(object):
    r"""
    Using this function for sample docstring (one line desc).

    A more extended description that provides details of how the function works.

    Parameters
    ----------
    moving : array_like
        Rot has a structure that can be iterated through implying it should be an
        array like structure
    static : data_type
        Description of tTree input and what it does.
    method : data_type
        Desc of method

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.
    type_without_description

    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc

    Notes
    -----
    Notes about the implementation algorithm (if needed).

    This can have multiple paragraphs.

    You may include some math:

    .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}

    And even use a Greek symbol like :math:`\omega` inline.

    References
    ----------
    Cite the relevant literature, e.g. [1]_.  You may also cite these
    references in the notes section above.

    .. [1] O. McNoleg, "The integration of GIS, remote sensing,
       expert systems and adaptive co-kriging for environmental habitat
       modelling of the Highland Haggis using object-oriented, fuzzy-logic
       and neural-network techniques," Computers & Geosciences, vol. 22,
       pp. 585-588, 1996.

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> a = [1, 2, 3]
    >>> print [x + 3 for x in a]
    [4, 5, 6]
    >>> print "a\n\nb"
    a
    b

    """    

    def __init__(self, moving, static, method = 'linearICP', *args, **kwargs):
        mData = dict(zip(['vert', 'faces', 'values'], 
                         [moving.vert, moving.faces, moving.values]))
        alData = copy.deepcopy(mData)
        self.m = AmpObject(alData, stype='reg')
        self.s = static
        if method is not None:
            getattr(self, method)(*args, **kwargs)
        
    def icp(self):
        r"""
        Automated alignment function between two meshes
        
        """

        tTree = spatial.cKDTree(self.s.vert)
        rot = np.array([0,0,0], dtype=float)
        res = minimize(self.calcDistError, rot, method='BFGS',
                       options={'gtol':1e-6, 'disp':True})
        
        
    def calcDistError(self, rot, tTree):
        r"""
        Needs description. Note the blank line at the end of each 
        docstring - this is necessary.

        """
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
    
    def linearICP(self, metric = 'point2point', 
                  maxiter=20, inlier=1.0, initTransform=None):
        """
        Iterative Closest Point algorithm which relies on using least squares
        method on a having made the minimisation problem into a set of linear 
        equations
        """
        # Define the rotation, translation, error and quaterion arrays
        Rs = np.zeros([3, 3, maxiter+1])
        Ts = np.zeros([3, maxiter+1])
#        qs = np.r_[np.ones([1, maxiter+1]), 
#                   np.zeros([6, maxiter+1])]
#        dq  = np.zeros([7, maxiter+1])
        dTheta = np.zeros([maxiter+1])
        err = np.zeros([maxiter+1])
        if initTransform is None:
            initTransform = np.eye(4)
        Rs[:, :, 0] = initTransform[:3, :3]
        Ts[:, 0] = initTransform[3, :3]
#        qs[:4, 0] = self.rot2quat(Rs[:, :, 0]) 
#        qs[4:, 0] = Ts[:, 0]
        # Define 
        fC = self.s.vert[self.s.faces].mean(axis=1)
        kdTree = spatial.cKDTree(fC)
        self.m.rigidTransform(Rs[:, :, 0], Ts[:, 0])
        inlier = math.ceil(self.m.vert.shape[0]*inlier)
        [dist, idx] = kdTree.query(self.m.vert, 1)
        # Sort by distance
        sort = np.argsort(dist)
        # Keep only those within the inlier fraction
        [dist, idx] = [dist[sort], idx[sort]]
        [dist, idx, sort] = dist[:inlier], idx[:inlier], sort[:inlier]
        err[0] = math.sqrt(dist.mean())
        for i in range(maxiter):
            if metric == 'point2point':
                [R, T] = getattr(self, metric)(self.m.vert[sort],
                                               fC[idx, :])
            else: 
                [R, T] = getattr(self, metric)(self.m.vert[sort],
                                               fC[idx, :], 
                                               self.s.norm[idx, :])
                
            Rs[:, :, i+1] = np.dot(R, Rs[:, :, i])
            Ts[:, i+1] = np.dot(R, Ts[:, i]) + T
            self.m.rigidTransform(R, T)
            [dist, idx] = kdTree.query(self.m.vert, 1)
            sort = np.argsort(dist)
            [dist, idx] = [dist[sort], idx[sort]]
            [dist, idx, sort] = dist[:inlier], idx[:inlier], sort[:inlier]
            err[i+1] = math.sqrt(dist.mean())
#            qs[:, i+1] = np.r_[self.rot2quat(R), T]
        R = Rs[:, :, -1]
        #Simpl
        [U, s, V] = np.linalg.svd(R)
        R = np.dot(U, V.T)
        self.tForm = np.r_[np.c_[R, np.zeros(3)], np.append(Ts[:, -1], 1)[:, None].T]
        self.R = R
        self.T = Ts[:, -1]
        self.rmse = err[-1]
        
            
    
    @staticmethod
    def point2plane(mv, sv, sn):
        cn = np.c_[np.cross(mv, sn), sn]
        C = np.dot(cn.T, cn)
        v = sv - mv
        b = np.zeros([6])
        for i, col in enumerate(cn.T):
            b[i] = (v * np.repeat(col[:, None], 3, axis=1) * sn).sum()
        X = np.linalg.lstsq(C, b, rcond=None)[0]
        [cx, cy, cz] = np.cos(X[:3])
        [sx, sy, sz] = np.sin(X[:3])
        R = np.array([[cy*cz, sx*sy*cz-cx*sz, cx*sy*cz+sx*sz],
                      [cy*sz, cx*cz+sx*sy*sz, cx*sy*sz-sx*cz],
                      [-sy,            sx*cy,          cx*cy]])
        T = X[3:]
        return (R, T)
    
    @staticmethod
    def point2point(mv, sv):
        mCent = mv - mv.mean(axis=0)
        sCent = sv - sv.mean(axis=0)
        C = np.dot(mCent.T, sCent)
        [U,_,V] = np.linalg.svd(C)
        det = np.linalg.det(np.dot(U, V))
        sign = np.eye(3)
        sign[2,2] = np.sign(det)
        R = np.dot(V.T, sign)
        R = np.dot(R, U.T)
        T = sv.mean(axis=0) - np.dot(R, mv.mean(axis=0))
        return (R, T)
        
    
    @staticmethod
    def rot2quat(R):
        [[Qxx, Qxy, Qxz],
         [Qyx, Qyy, Qyz],
         [Qzx, Qzy, Qzz]] = R
        t = Qxx + Qyy + Qzz
        if t >= 0:
            r = math.sqrt(1+t)
            s = 0.5/r
            w = 0.5*r
            x = (Qzy-Qyz)*s
            y = (Qxz-Qzx)*s
            z = (Qyx-Qxy)*s
        else:
            maxv = max([Qxx, Qyy, Qzz])
            if maxv == Qxx:
                r = math.sqrt(1+Qxx-Qyy-Qzz)
                s = 0.5/r
                w = (Qzy-Qyz)*s
                x = 0.5*r
                y = (Qyx+Qxy)*s
                z = (Qxz+Qzx)*s
            elif maxv == Qyy:
                r = math.sqrt(1+Qyy-Qxx-Qzz)
                s = 0.5/r
                w = (Qxz-Qzx)*s
                x = (Qyx+Qxy)*s
                y = 0.5*r
                z = (Qzy+Qyz)*s
            else:
                r = math.sqrt(1+Qzz-Qxx-Qyy)
                s = 0.5/r
                w = (Qyx-Qxy)*s
                x = (Qxz+Qzx)*s
                y = (Qzy+Qyz)*s
                z = 0.5*r
        return np.array([w, x, y, z])
    
    def display(self):
        r"""
        Function to display the two aligned meshes in 
        """
        if not hasattr(self.s, 'actor'):
            self.s.addActor()
        if not hasattr(self.m, 'actor'):
            self.m.addActor()
        # Generate a renderer window
        win = vtkRenWin()
        # Set the number of viewports
        win.setnumViewports(1)
        # Set the background colour
        win.setBackground([1,1,1])
        # Set camera projection 
        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(win)
        renderWindowInteractor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        # Set camera projection 
        win.setView()
        self.s.actor.setColor([1.0, 0.0, 0.0])
        self.s.actor.setOpacity(0.5)
        self.m.actor.setColor([0.0, 0.0, 1.0])
        self.m.actor.setOpacity(0.5)
        win.renderActors([self.s.actor, self.m.actor])
        win.Render()
        win.rens[0].GetActiveCamera().Azimuth(180)
        win.rens[0].GetActiveCamera().SetParallelProjection(True)
        win.Render()
        return win


