# -*- coding: utf-8 -*-
"""
Package for dealing with alignment methods between two AmpObject meshes
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk
"""

import numpy as np
import copy
import vtk
import math
from scipy import spatial
from scipy.optimize import minimize
from ampscan.core import AmpObject
from ampscan.vis import vtkRenWin
from ampscan.analyse import create_slices, est_volume, calc_csa

# For doc examples
import os
staticfh = os.path.join(os.getcwd(), "tests", "stl_file.stl")
movingfh = os.path.join(os.getcwd(), "tests", "stl_file_2.stl")


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
    	The arguments used for the alignment methods
    **kwargs:
    	The keyword arguments used for the alignment methods

    Returns
    -------
    m: AmpObject
        The aligned AmpObject, it same number of vertices and face array as 
        the moving AmpObject
        Access this using align.m

    Examples
    --------
    >>> static = AmpObject(staticfh)
    >>> moving = AmpObject(movingfh)
    >>> al = align(moving, static).m

    """    

    def __init__(self, moving, static, method = 'linPoint2Plane', 
                inverse=False, *args, **kwargs):
        mData = dict(zip(['vert', 'faces', 'values'], 
                         [moving.vert, moving.faces, moving.values]))
        alData = copy.deepcopy(mData)
        self.setMoving(AmpObject(alData, stype='reg'))
        self.setStatic(static)
        self.R = np.eye(3)
        self.T = np.zeros(3)
        self.tForm = np.eye(4)
        self.rmse = 0

        if inverse:
            self.inverse(method=method, *args, **kwargs)
        else:
            self.runICP(method=method, *args, **kwargs)

    def setStatic(self, amp):
        r"""
        Set the static AmpObject
        """
        self.s = amp
    
    def setMoving(self, amp):
        r"""
        Set the moving AmpObject
        """
        self.m = amp

    def getAlign(self):
        r"""
        Return the aligned AmpObject
        """
        return self.m

    def getRT(self):
        r"""
        Return the rotation and translation array
        """
        return (self.R, self.T)
    
    def getTForm(self):
        r"""
        Return the transformation array
        """
        return self.tForm

    def getRMSE(self):
        r"""
        Return the RMSE post alignment
        """
        return self.rmse


    
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
        	The arguments used for the alignment methods
        **kwargs:
        	The keyword arguments used for the alignment methods
        
        """
        # Define the rotation, translation, error and quaterion arrays
        Rs = np.zeros([3, 3, maxiter+1])
        Ts = np.zeros([3, maxiter+1])
        err = np.zeros([maxiter+1])
        if initTransform is None:
            initTransform = np.eye(4)
        Rs[:, :, 0] = initTransform[:3, :3]
        Ts[:, 0] = initTransform[3, :3]
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
            elif method == 'contPoints':
                [R, T] = getattr(self, method)(*args, **kwargs)
                self.m.rigidTransform(R, T)
                [dist, idx] = kdTree.query(self.m.vert, 1)
                sort = np.argsort(dist)
                [dist, idx] = [dist[sort], idx[sort]]
                [dist, idx, sort] = dist[:inlier], idx[:inlier], sort[:inlier]
                self.tForm = np.r_[np.c_[R, np.zeros(3)], np.append(T, 1)[:, None].T]
                self.R = R
                self.T = T
                self.rmse = math.sqrt(dist.mean())
                return
            elif method == 'idxPoints':
                [R, T] = getattr(self, 'idxPoints')(*args, **kwargs)
                self.m.rigidTransform(R, T)
                [dist, idx] = kdTree.query(self.m.vert, 1)
                sort = np.argsort(dist)
                [dist, idx] = [dist[sort], idx[sort]]
                [dist, idx, sort] = dist[:inlier], idx[:inlier], sort[:inlier]
                self.tForm = np.r_[np.c_[R, np.zeros(3)], np.append(T, 1)[:, None].T]
                self.R = R
                self.T = T
                self.rmse = math.sqrt(dist.mean())
                return
            elif method == 'optZVol':
                self.optZVol(*args, **kwargs)
                # print(self.T)
                [dist, idx] = kdTree.query(self.m.vert, 1)
                sort = np.argsort(dist)
                [dist, idx] = [dist[sort], idx[sort]]
                [dist, idx, sort] = dist[:inlier], idx[:inlier], sort[:inlier]
                self.tForm = np.r_[np.c_[self.R, np.zeros(3)], np.append(self.T, 1)[:, None].T]
                self.rmse = math.sqrt(dist.mean())
                return
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
            
    def inverse(self, method = 'linPoint2Plane', *args, **kwargs):
        #inverting the objects
        self.temp = self.s
        self.s = self.m
        self.m = self.temp
        self.runICP(method=method, *args, **kwargs)
        #resetting the objects
        self.temp = self.s
        self.s = self.m
        self.m = self.temp
        del self.temp
        #inverting the transformation on both objects
        self.R = self.R.transpose()
        self.T = -self.T
        self.tForm = np.r_[np.c_[self.R, np.zeros(3)], np.append(self.T, 1)[:, None].T]
        self.s.rigidTransform(self.R, self.T)
        self.m.rigidTransform(self.R, self.T)
    
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
        >>> static = AmpObject(staticfh)
        >>> moving = AmpObject(movingfh)
        >>> al = align(moving, static, method='linPoint2Plane').m
        
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
        >>> static = AmpObject(staticfh)
        >>> moving = AmpObject(movingfh)
        >>> al = align(moving, static, method='linPoint2Point').m

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
    def contPoints(mv=None, sv=None):
        r"""
        Point-to-Point Iterative Closest Point algorithm which 
        relies on using singular value decomposition on the centered arrays.  
        
        Parameters
        ----------
        mv: ndarray
            The array of control points to be moved 
        sv: ndarray
            The array of control points 
        
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
        >>> static = AmpObject(staticfh)
        >>> moving = AmpObject(movingfh)
        >>> al = align(moving, static, method='linPoint2Point').m

        """
        if mv is None or sv is None:
            return ValueError('To call the contPoints ICP method, ensure that '
                              'mv and sv have been defined as keyword arguments')
        mv = np.asarray(mv)
        sv = np.asarray(sv)
        if mv.shape != sv.shape:
            return ValueError('Not the same number of static and moving control points')
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
        # print(R)
        # print(T)
        return (R, T)

    def idxPoints(self, mv=None, sv=None):
        r"""
        Point-to-Point Iterative Closest Point algorithm which 
        relies on using singular value decomposition on the centered arrays.  
        
        Parameters
        ----------
        mv: ndarray
            The index array of moving vertices to be aligned
        sv: ndarray
            The index array of static vertices to be aligned to
        
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
        >>> static = AmpObject(staticfh)
        >>> moving = AmpObject(movingfh)
        >>> al = align(moving, static, mv = [0, 1, 2], sv = [0, 1, 2], method='idxPoints').m

        """
        if mv is None or sv is None:
            return ValueError('To call the contPoints ICP method, ensure that '
                              'mv and sv have been defined as keyword arguments')
        return self.contPoints(mv=self.m.vert[mv, :], sv=self.s.vert[sv, :])

    
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
        >>> static = AmpObject(staticfh)
        >>> moving = AmpObject(movingfh)
        >>> al = align(moving, static, method='optPoint2Point', opt='SLSQP').m
            
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

    def optZVol(self, z0 = 0):
        r"""
        Direct minimisation of the volume. 
        1) Translate moving object to match minZ of static 
        2) Calculate volume to static z0
        3) Cumulative sum the slices and evaluate volume
        4) Find slice nearest volume of static 
        
        Parameters
        ----------
        opt: z0, default 0
            The slice height to evaluate the static volume from  
        
        Returns
        -------
        R: ndarray
            The optimal rotation array, rotation 
        T: ndarray
            The optimal translation array
            
            
        """
        sMinZ = self.s.vert[:, 2].min()
        mMinZ = self.m.vert[:, 2].min()
        dZ = mMinZ - sMinZ
        # Keep track of T
        T = dZ
        self.m.vert[:, 2] += dZ
        mMaxZ = self.m.vert[:, 2].max()
        # Create slices of static from 2 mm below dist to z0
        # print([sMinZ + 1, z0])
        sPolys = create_slices(self.s, [sMinZ + 1, z0], 0.5, typ='real_intervals', axis=2)
        
        sVol = est_volume(sPolys)
        # Create slices of static from 2 mm below dist to z0
        mPolys = create_slices(self.m, [sMinZ + 1, mMaxZ - 1], 0.5, typ='real_intervals', axis=2)
        # Iterate through mPolys
        csa = calc_csa(mPolys)
        # Get the distance between each slice 
        d = []
        for p in mPolys: 
            d.append(p[:, 2].mean())
        d = np.asarray(d)
        # Get distance between each slice 
        dist = np.abs(d[1:]- d[:-1])
        vol = np.c_[csa[1:], csa[:-1]]
        vol = np.mean(vol, axis=1) * dist
        # Add in 0 at start to ease indexing 
        vol = np.insert(vol, 0, 0)
        
        # print(sVol)
        # print(vol)
        vol = np.cumsum(vol) - sVol
        # print(vol)
        for (i, v) in enumerate(vol):
            if v >= 0:
                break
        # Linear interpolate z in between slices, different as (n-1) sections to slices
        zl = d[i - 1]
        zh = d[i]
        vl = vol[i - 1]
        vh = vol[i]
        dz = zh - zl
        dv = vh - vl
        # Absolute value of z to reach
        z =  zl + ((0 - vl)/ dv) * dz;
        # print(z)
        #  Translate by the calculated z value 
        # z -= d[0]
        T -= z
        # print(vl, sVol, vh)
        self.m.vert[:, 2] -= z




        self.R = np.eye(3)
        self.T = [0, 0, T]

    
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


    def genIm(self, crop=False):
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
        # Set camera projection 
        win.setView([0, -1, 0], 0)
        win.SetSize(512, 512)
        win.Modified()
        win.OffScreenRenderingOn()
        self.s.actor.setColor([1.0, 0.0, 0.0])
        self.s.actor.setOpacity(0.5)
        self.m.actor.setColor([0.0, 0.0, 1.0])
        self.m.actor.setOpacity(0.5)
        win.renderActors([self.s.actor, self.m.actor])
        win.Render()
        win.rens[0].GetActiveCamera().Azimuth(0)
        win.rens[0].GetActiveCamera().SetParallelProjection(True)
        win.Render()
        im = win.getImage()
        if crop is True:
            mask = np.all(im == 1, axis=2)
            mask = ~np.all(mask, axis=1)
            im = im[mask, :, :]
            mask = np.all(im == 1, axis=2)
            mask = ~np.all(mask, axis=0)
            im = im[:, mask, :]
        return im, win

