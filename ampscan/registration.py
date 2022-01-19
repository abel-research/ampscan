# -*- coding: utf-8 -*-
"""
Package for dealing with registration methods between two AmpObject meshes
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk
"""
import numpy as np
import copy
from scipy import spatial
from ampscan.core import AmpObject
import matplotlib.pyplot as plt

# For the doc examples
import os
basefh = os.path.join(os.getcwd(), "tests", "stl_file.stl")
targfh = os.path.join(os.getcwd(), "tests", "stl_file_2.stl")

class registration(object):
    r"""
    Registration methods between two AmpObject meshes. This function morphs the baseline 
    vertices onto the surface of the target and returns a new AmpObject
    
    Parameters
    ----------
    baseline: AmpObject
    	The baseline AmpObject, the vertices from this will be morphed onto the target
    target: AmpObject
    	The target AmpObject, the shape that the baseline attempts to morph onto
    method: str: default 'point2plane'
    	A string of the method used for registration
    *args:
    	The arguments used for the registration methods
    **kwargs:
    	The keyword arguments used for the registration methods
        
    Returns
    -------
    reg: AmpObject
        The registered AmpObject, the vertices of this are on the surface of the target 
        and it has the same number of vertices and face array as the baseline AmpObject
        Access this accessing the registration.reg 
    
    Examples
    --------
    >>> from ampscan.core import AmpObject
    >>> baseline = AmpObject(basefh)
    >>> target = AmpObject(targfh)
    >>> reg = registration(baseline, target, steps=10, neigh=10, smooth=1).reg
		
    """ 
    def __init__(self, baseline, target, method='point2plane', *args, **kwargs):
        self.setBaseline(baseline)
        self.setTarget(target)
        self.reg = None
        self.values = None
        if method is not None:
            getattr(self, method)(*args, **kwargs)
        

    def setBaseline(self, amp):
        r"""
        Set the baseline AmpObject
        """
        self.b = amp
    
    def setTarget(self, amp):
        r"""
        Set the target AmpObject
        """
        self.t = amp
    
    def getReg(self):
        r"""
        Return the registered AmpObject
        """
        return self.reg

    def getValues(self):
        r""""
        Return the values array from the registration
        """
        return self.values

        
        
    def point2plane(self, steps = 1, neigh = 10, inside = True, subset = None, 
                    scale=None, smooth=1, fixBrim=False, error='norm'):
        r"""
        Point to Plane method for registration between the two meshes 
        
        Parameters
        ----------
        steps: int, default 1
            Number of iterations
        int, default 10
            Number of nearest neighbours to interrogate for each baseline point
        inside: bool, default True
            If True, a barycentric centre check is made to ensure the registered 
            point lines within the target triangle
        subset: array_like, default None
            Indicies of the baseline nodes to include in the registration, default is none so 
            all are used
        scale: float, default None
            If not None scale the baseline mesh to match the target mesh in the z-direction, 
            the value of scale will be used as a plane from which the nodes are scaled.
            Nodes with a higher z value will not be scaled. 
        smooth: int, default 1
            Indicate number of Laplacian smooth steps in between the steps 
        fixBrim: bool, default False
            If True, the nodes on the brim line will not be included in the smooth
        error: bool, default False
            If True, the polarity will be included when calculating the distance 
            between the target and baseline mesh
		
        """
        # Calc FaceCentroids
        fC = self.t.vert[self.t.faces].mean(axis=1)
        # Construct knn tree
        tTree = spatial.cKDTree(fC)
        bData = dict(zip(['vert', 'faces', 'values'], 
                         [self.b.vert, self.b.faces, self.b.values]))
        regData = copy.deepcopy(bData)
        self.reg = AmpObject(regData, stype='reg')
        self.disp = AmpObject({'vert': np.zeros(self.reg.vert.shape),
                               'faces': self.reg.faces,
                               'values':self.reg.values}, struc=False)
        self.disp.calcEdges()
        
        if scale is not None:
            tmin = self.t.vert.min(axis=0)[2]
            rmin = self.reg.vert.min(axis=0)[2]
            SF = ((tmin-scale)/(rmin-scale)) - 1
            logic = self.reg.vert[:, 2] < scale
            d = (self.reg.vert[logic, 2] - scale) * SF
            self.disp.vert[logic, 2] += d
            self.reg.vert = self.b.vert + self.disp.vert
        normals = np.cross(self.t.vert[self.t.faces[:,1]] -
                         self.t.vert[self.t.faces[:,0]],
                         self.t.vert[self.t.faces[:,2]] -
                         self.t.vert[self.t.faces[:,0]])
        mag = (normals**2).sum(axis=1)
        for step in np.arange(steps, 0, -1, dtype=float):
            # Index of 10 centroids nearest to each baseline vertex
            ind = tTree.query(self.reg.vert, neigh)[1]
            if ind.ndim == 1:
                ind = ind[:, None]
            # Define normals for faces of nearest faces
            norms = normals[ind]
            # Get a point on each face
            fPoints = self.t.vert[self.t.faces[ind, 0]]
            # Calculate dot product between point on face and normals
            d = np.einsum('ijk, ijk->ij', norms, fPoints)
            t = (d - np.einsum('ijk, ik->ij', norms, self.reg.vert))/mag[ind]
            # Calculate the vector from old point to new point
            G = self.reg.vert[:, None, :] + np.einsum('ijk, ij->ijk', norms, t)
            # Ensure new points lie inside points otherwise set to 99999
            # print(G.shape, ind.shape)
            if inside is True:
                # Adjust so inside face 
                G = self.__adjustBarycentric(self.reg.vert, G, ind)
                # G = self.__calcBarycentric(self.reg.vert, G, ind)
            # Find smallest distance from old to new point 
            G = G - self.reg.vert[:, None, :]
            GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G))
            GInd = GMag.argmin(axis=1)
            # Define vector from baseline point to intersect point
            D = G[np.arange(len(G)), GInd, :]
#            rVert += D/step
            self.disp.vert += D/step
            if smooth > 0 and step > 1:
                self.disp.hc_smooth(smooth, beta=0.6,  brim = fixBrim, norms=False)
                self.reg.vert = self.b.vert + self.disp.vert
            else:
                self.reg.vert = self.b.vert + self.disp.vert
                self.reg.adjustCoincident(beta=0.6)
        self.reg.calcStruct(vNorm=True)
        self.values = self.calcError(error)
        self.reg.values[:] = self.values

        
    def calcError(self, method='norm'):
        r"""
        Calculate the magnitude of distances between the baseline and registered array
		
        Parameters
        ----------
        method: str, default 'norm'
            The method used to calculate the distances. 'abs' returns the absolute
            distance. 'cent'calculates polarity based upon distance from centroid.
            'norm' calculates dot product between baseline vertex normal and distance 
            normal

        Returns
        -------
        values: array_like
            Magnitude of distances

        """
        method = '_registration__' + method + 'Dist'
        try:
            values = getattr(self, method)()
            return values
        except: ValueError('"%s" is not a method, try "abs", "cent" or "prod"' % method)
            
    
    def __absDist(self):
        r"""
        Return the error based upon the absolute distance
        
        Returns
        -------
        values: array_like
            Magnitude of distances

        """
        return np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
    
    def __centDist(self):
        r"""
        Return the error based upon distance from centroid 
        
        Returns
        -------
        values: array_like
            Magnitude of distances

        """
        values = np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
        cent = self.b.vert.mean(axis=0)
        r = np.linalg.norm(self.reg.vert - cent, axis=1)
        b = np.linalg.norm(self.b.vert - cent, axis=1)
        polarity = np.ones([self.reg.vert.shape[0]])
        polarity[r<b] = -1
        return values * polarity

    def __normDist(self):
        r"""
        Returns error based upon scalar product of normal 
        
        Returns
        -------
        values: array_like
            Magnitude of distances

        """
        self.b.calcVNorm()
        D = self.reg.vert - self.b.vert
        n = self.b.vNorm
        values = np.linalg.norm(D, axis=1)
        polarity = np.sum(n*D, axis=1) < 0
        values[polarity] *= -1.0
        return values
        
        
    def __calcBarycentric(self, vert, G, ind):
        r"""
        Calculate the barycentric co-ordinates of each target face and the registered vertex, 
        this ensures that the registered vertex is within the bounds of the target face. If not 
        the registered vertex is moved to the nearest vertex on the target face 

        Parameters
        ----------
        vert: array_like
            The array of baseline vertices
        G: array_like
            The array of candidates for registered vertices. If neigh>1 then axis 2 will correspond 
            to the number of nearest neighbours selected
        ind: array_like
            The index of the nearest faces to the baseline vertices
        
        Returns
        -------
        G: array_like 
            The new array of candidates for registered vertices, from here, the one with 
            smallest magnitude is selected. All these points will lie within the target face

        """
        P0 = self.t.vert[self.t.faces[ind, 0]]
        P1 = self.t.vert[self.t.faces[ind, 1]]
        P2 = self.t.vert[self.t.faces[ind, 2]]
        
        v0 = P2 - P0
        v1 = P1 - P0
        v2 = G - P0
        
        d00 = np.einsum('ijk, ijk->ij', v0, v0)
        d01 = np.einsum('ijk, ijk->ij', v0, v1)
        d02 = np.einsum('ijk, ijk->ij', v0, v2)
        d11 = np.einsum('ijk, ijk->ij', v1, v1)
        d12 = np.einsum('ijk, ijk->ij', v1, v2)
        
        denom = d00*d11 - d01*d01
        u = (d11 * d02 - d01 * d12)/denom
        v = (d00 * d12 - d01 * d02)/denom
        # Test if inside 
        logic = (u >= 0) * (v >= 0) * (u + v < 1)
        
        P = np.stack([P0, P1, P2], axis=3)
        pg = G[:, :, :, None] - P
        pd =  np.linalg.norm(pg, axis=2)
        pdx = pd.argmin(axis=2)
        i, j = np.meshgrid(np.arange(P.shape[0]), np.arange(P.shape[1]))
        nearP = P[i.T, j.T, :, pdx]
        G[~logic, :] = nearP[~logic, :]
        return G


    def __adjustBarycentric(self, vert, G, ind):
        r"""
        Calculate the barycentric co-ordinates of each target face and the registered vertex, 
        this ensures that the registered vertex is within the bounds of the target face. If not 
        the registered vertex is moved to the nearest vertex or edge on the target face 

        Parameters
        ----------
        vert: array_like
            The array of baseline vertices
        G: array_like
            The array of candidates for registered vertices. If neigh>1 then axis 2 will correspond 
            to the number of nearest neighbours selected
        ind: array_like
            The index of the nearest faces to the baseline vertices
        
        Returns
        -------
        G: array_like 
            The new array of candidates for registered vertices, from here, the one with 
            smallest magnitude is selected. All these points will lie within the target face
 
        """
        P0 = self.t.vert[self.t.faces[ind, 0]]
        P1 = self.t.vert[self.t.faces[ind, 1]]
        P2 = self.t.vert[self.t.faces[ind, 2]]
        
        
        v0 = P2 - P0
        v1 = P1 - P0
        v2 = G - P0

        d00 = np.einsum('ijk, ijk->ij', v0, v0)
        d01 = np.einsum('ijk, ijk->ij', v0, v1)
        d02 = np.einsum('ijk, ijk->ij', v0, v2)
        d11 = np.einsum('ijk, ijk->ij', v1, v1)
        d12 = np.einsum('ijk, ijk->ij', v1, v2)
        
        # Compute barycentric co-ordinates
        denom = d00*d11 - d01*d01
        u = (d11 * d02 - d01 * d12)/denom
        v = (d00 * d12 - d01 * d02)/denom
        w = 1 - u - v
        
        # Logic for adjustment 
        P0_log = (w > 0) * (v < 0) * (u < 0)
        P1_log = (w < 0) * (v > 0) * (u < 0)
        P2_log = (w < 0) * (v < 0) * (u > 0)
        P0P1_log = (w > 0) * (v > 0) * (u < 0)
        P0P2_log = (w > 0) * (v < 0) * (u > 0)
        P1P2_log = (w < 0) * (v > 0) * (u > 0)
        
        G[P0_log, :] = P0[P0_log, :]
        G[P1_log, :] = P1[P1_log, :]
        G[P2_log, :] = P2[P2_log, :]
        
        # Compute line intersection 
        for pa, pb, log in [[P0, P1, P0P1_log], [P0, P2, P0P2_log], [P1, P2, P1P2_log]]:
            s = pb - pa
            t = G - pa
            ps = np.einsum('ijk, ijk->ij', t, s)
            l2 = np.einsum('ijk, ijk->ij', s, s)
            newG = pa + ps[:, :, None] / l2[:, :, None] * s
            G[log, :] = newG[log, :]
        return G


    
    def plotResults(self, name=None, xrange=None, color=None, alpha=None):
        r"""
        Function to generate a mpl figure. Includes a rendering of the 
        AmpObject, a histogram of the registration values 
        
        Returns
        -------
        fig: mplfigure
            A matplot figure of the standard analysis
        
        """
        fig, ax = plt.subplots(1)
        n, bins, _ = ax.hist(self.reg.values, 50, density=True, range=xrange,
                             color=color, alpha=alpha)
        mean = self.reg.values.mean()
        stdev = self.reg.values.std()
        ax.set_title(r'Distribution of shape variance, '
                     '$\mu=%.2f$, $\sigma=%.2f$' % (mean, stdev))
        ax.set_xlim(None)
        if name is not None:
            plt.savefig(name, dpi = 300)
        return ax, n, bins