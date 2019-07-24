# -*- coding: utf-8 -*-
"""
Package for dealing with alignment methods between two AmpObject meshes
Copyright: Joshua Steer 2018, Joshua.Steer@soton.ac.uk
"""

import numpy as np
import copy
import vtk
import math
from scipy import spatial
from scipy.optimize import minimize
from AmpScan.core import AmpObject
from AmpScan.ampVis import vtkRenWin


class align(object):
    r"""
    Automated alignment methods between two meshes
    
    Parameters
    ----------
    moving: AmpObject
        The moving AmpObject that is to be aligned to the static object
    static: AmpObject
        The static AmpObject that the moving AmpObject that the moving object 
        will be aligned to
    method: str, default 'linPoint2Plane'
        A string of the method used for alignment
    *args:
    	The arguments used for the registration methods
    **kwargs:
    	The keyword arguments used for the registration methods

    Returns
    -------
    m: AmpObject
        The aligned AmpObject, it same number of vertices and face array as 
        the moving AmpObject
        Access this using align.m

    Examples
    --------
    >>> import AmpScan, os
    >>> staticfh = os.getcwd()+"\\tests\\stl_file.stl"
    >>> movingfh = os.getcwd()+"\\tests\\stl_file_2.stl"
    >>> static = AmpScan.AmpObject(staticfh)
    >>> moving = AmpScan.AmpObject(movingfh)
    >>> al = AmpScan.align(moving, static).m

    """    

    def __init__(self, moving, static, method = 'linPoint2Plane', *args, **kwargs):
        mData = dict(zip(['vert', 'faces', 'values'], 
                         [moving.vert, moving.faces, moving.values]))
        alData = copy.deepcopy(mData)
        self.m = AmpObject(alData, stype='reg')
        self.s = static
        self.runICP(method=method, *args, **kwargs)
        
    
    def runICP(self, method = 'linPoint2Plane', maxiter=20, inlier=1.0,
               initTransform=None, *args, **kwargs):
        r"""
        The function to run the ICP algorithm, this function calls one of 
        multiple methods to calculate the affine transformation 
        
        Parameters
        ----------
        method: str, default 'linPoint2Plane'
            A string of the method used for alignment
        maxiter: int, default 20
            Maximum number of iterations to run the ICP algorithm
        inlier: float, default 1.0
            The proportion of closest points to use to calculate the 
            transformation, if < 1 then vertices with highest error are 
            discounted
        *args:
        	The arguments used for the registration methods
        **kwargs:
        	The keyword arguments used for the registration methods
        
        """
        # Define the rotation, translation, error and quaterion arrays
        Rs = np.zeros([3, 3, maxiter+1])
        Ts = np.zeros([3, maxiter+1])
#        qs = np.r_[np.ones([1, maxiter+1]), 
#                   np.zeros([6, maxiter+1])]
#        dq  = np.zeros([7, maxiter+1])
#        dTheta = np.zeros([maxiter+1])
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
            if method == 'linPoint2Point':
                [R, T] = getattr(self, method)(self.m.vert[sort, :],
                                               fC[idx, :], 
                                               *args, **kwargs)
            elif method == 'linPoint2Plane': 
                [R, T] = getattr(self, method)(self.m.vert[sort, :],
                                               fC[idx, :], 
                                               self.s.norm[idx, :],
                                               *args, **kwargs)
            elif method == 'optPoint2Point':
                [R, T] = getattr(self, method)(self.m.vert[sort, :],
                                               fC[idx, :],
                                               *args, **kwargs)
            else: KeyError('Not a supported alignment method')
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
        R = np.dot(U, V)
        self.tForm = np.r_[np.c_[R, np.zeros(3)], np.append(Ts[:, -1], 1)[:, None].T]
        self.R = R
        self.T = Ts[:, -1]
        self.rmse = err[-1]
        
            
    
    @staticmethod
    def linPoint2Plane(mv, sv, sn):
        r"""
        Iterative Closest Point algorithm which relies on using least squares
        method from converting the minimisation problem into a set of linear 
        equations. This uses a 
        
        Parameters
        ----------
        mv: ndarray
            The array of vertices to be moved 
        sv: ndarray
            The array of static vertices, these are the face centroids of the 
            static mesh
        sn: ndarray
            The normals of the point in teh static array, these are derived 
            from the normals of the faces for each centroid
        
        Returns
        -------
        R: ndarray
            The optimal rotation array 
        T: ndarray
            The optimal translation array
        
        References
        ----------
        .. [1] Besl, Paul J.; N.D. McKay (1992). "A Method for Registration of 3-D
           Shapes". IEEE Trans. on Pattern Analysis and Machine Intelligence (Los
           Alamitos, CA, USA: IEEE Computer Society) 14 (2): 239-256.
        
        .. [2] Chen, Yang; Gerard Medioni (1991). "Object modelling by registration of
           multiple range images". Image Vision Comput. (Newton, MA, USA:
           Butterworth-Heinemann): 145-155

        Examples
        --------
        >>> import AmpScan, os
        >>> staticfh = os.getcwd()+"\\tests\\stl_file.stl"
        >>> movingfh = os.getcwd()+"\\tests\\stl_file_2.stl"
        >>> static = AmpScan.AmpObject(staticfh)
        >>> moving = AmpScan.AmpObject(movingfh)
        >>> al = AmpScan.align(moving, static, method='linPoint2Plane').m
        
        """
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
    def linPoint2Point(mv, sv):
        r"""
        Point-to-Point Iterative Closest Point algorithm which 
        relies on using singular value decomposition on the centered arrays.  
        
        Parameters
        ----------
        mv: ndarray
            The array of vertices to be moved 
        sv: ndarray
            The array of static vertices, these are the face centroids of the 
            static mesh
        
        Returns
        -------
        R: ndarray
            The optimal rotation array 
        T: ndarray
            The optimal translation array
        
        References
        ----------
        .. [1] Besl, Paul J.; N.D. McKay (1992). "A Method for Registration of 3-D
           Shapes". IEEE Trans. on Pattern Analysis and Machine Intelligence (Los
           Alamitos, CA, USA: IEEE Computer Society) 14 (2): 239-256.
        
        .. [2] Chen, Yang; Gerard Medioni (1991). "Object modelling by registration of
           multiple range images". Image Vision Comput. (Newton, MA, USA:
           Butterworth-Heinemann): 145-155

        Examples
        --------
        >>> import AmpScan, os
        >>> staticfh = os.getcwd()+"\\tests\\stl_file.stl"
        >>> movingfh = os.getcwd()+"\\tests\\stl_file_2.stl"
        >>> static = AmpScan.AmpObject(staticfh)
        >>> moving = AmpScan.AmpObject(movingfh)
        >>> al = AmpScan.align(moving, static, method='linPoint2Point').m

        """
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
    def optPoint2Point(mv, sv, opt='L-BFGS-B'):
        r"""
        Direct minimisation of the rmse between the points of the two meshes. This 
        method enables access to all of Scipy's minimisation algorithms 
        
        Parameters
        ----------
        mv: ndarray
            The array of vertices to be moved 
        sv: ndarray
            The array of static vertices, these are the face centroids of the 
            static mesh
        opt: str, default 'L_BFGS-B'
            The string of the scipy optimiser to use 
        
        Returns
        -------
        R: ndarray
            The optimal rotation array 
        T: ndarray
            The optimal translation array
            
        Examples
        --------
        >>> import AmpScan, os
        >>> staticfh = os.getcwd()+"\\tests\\stl_file.stl"
        >>> movingfh = os.getcwd()+"\\tests\\stl_file_2.stl"
        >>> static = AmpScan.AmpObject(staticfh)
        >>> moving = AmpScan.AmpObject(movingfh)
        >>> al = AmpScan.align(moving, static, method='optPoint2Point', opt='SLSQP').m
            
        """
        X = np.zeros(6)
        lim = [-np.pi/4, np.pi/4] * 3 + [-5, 5] * 3
        lim = np.reshape(lim, [6, 2])
        try:
            X = minimize(align.optDistError, X,
                         args=(mv, sv),
                         bounds=lim, method=opt)
        except:
            X = minimize(align.optDistError, X,
                         args=(mv, sv),
                         method=opt)
        [angx, angy, angz] = X.x[:3]
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
        T = X.x[3:]
        return (R, T)

    @staticmethod
    def optDistError(X, mv, sv):
        r"""
        The function to minimise. It performs the affine transformation then returns 
        the rmse between the two vertex sets
        
        Parameters
        ----------
        X:  ndarray
            The affine transformation corresponding to [Rx, Ry, Rz, Tx, Ty, Tz]
        mv: ndarray
            The array of vertices to be moved 
        sv: ndarray
            The array of static vertices, these are the face centroids of the 
            static mesh

        Returns
        -------
        err: float
            The RMSE between the two meshes
        
        """
        [angx, angy, angz] = X[:3]
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
        moved = np.dot(mv, R.T)
        moved += X[3:]
        dist = (moved - sv)**2
        dist = dist.sum(axis=1)
        err = np.sqrt(dist.mean())
        return err

    
    @staticmethod
    def rot2quat(R):
        """
        Convert a rotation matrix to a quaternionic matrix
        
        Parameters
        ----------
        R: array_like
            The 3x3 rotation array to be converted to a quaternionic matrix
        
        Returns
        -------
        Q: ndarray
            The quaternionic matrix

        """
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
        Display the static mesh and the aligned within an interactive VTK 
        window 
        
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


