# -*- coding: utf-8 -*-
"""
Package for dealing with registration methods between two AmpObject meshes
Copyright: Joshua Steer 2018, Joshua.Steer@soton.ac.uk
"""
import numpy as np
import copy
from scipy import spatial
from .core import AmpObject

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
    >>> baseline = AmpScan.AmpObject(basefh)
    >>> target = AmpScan.AmpObject(targfh)
    >>> reg = AmpScan.registration(steps=10, neigh=10, smooth=1).reg
		
    """ 
    def __init__(self, baseline, target, method='point2plane', *args, **kwargs):
        self.b = baseline
        self.t = target
        if method is not None:
            getattr(self, method)(*args, **kwargs)
        
        
    def point2plane(self, steps = 1, neigh = 10, inside = True, subset = None, 
                    scale=None, smooth=1, fixBrim=False, error=False):
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
        smooth: int, default 1
            Indicate number of laplacian smooth steps in between the steps 
        fixBrim: bool, default False
            If True, the nodes on the brim line will not be included in the smooth
		
        """
        # Calc FaceCentroids
        fC = self.t.vert[self.t.faces].mean(axis=1)
        # Construct knn tree
        tTree = spatial.cKDTree(fC)
        bData = dict(zip(['vert', 'faces', 'values'], 
                         [self.b.vert, self.b.faces, self.b.values]))
        regData = copy.deepcopy(bData)
        self.reg = AmpObject(regData, stype='reg')
        if scale is not None:
            tmin = self.t.vert.min(axis=0)[2]
            rmin = self.reg.vert.min(axis=0)[2]
            SF = ((tmin-scale)/(rmin-scale)) - 1
            logic = self.reg.vert[:, 2] < scale
            d = (self.reg.vert[logic, 2] - scale) * SF
            self.reg.vert[logic, 2] += d
        normals = np.cross(self.t.vert[self.t.faces[:,1]] -
                         self.t.vert[self.t.faces[:,0]],
                         self.t.vert[self.t.faces[:,2]] -
                         self.t.vert[self.t.faces[:,0]])
        mag = (normals**2).sum(axis=1)
        if subset is None:
            rVert = self.reg.vert
        else:
            rVert = self.reg.vert[subset]
        for step in np.arange(steps, 0, -1, dtype=float):
            # Index of 10 centroids nearest to each baseline vertex
            ind = tTree.query(rVert, neigh)[1]
#            D = np.zeros(self.reg.vert.shape)
            # Define normals for faces of nearest faces
            norms = normals[ind]
            # Get a point on each face
            fPoints = self.t.vert[self.t.faces[ind, 0]]
            # Calculate dot product between point on face and normals
            d = np.einsum('ijk, ijk->ij', norms, fPoints)
            t = (d - np.einsum('ijk, ik->ij', norms, rVert))/mag[ind]
            # Calculate the vector from old point to new point
            G = rVert[:, None, :] + np.einsum('ijk, ij->ijk', norms, t)
            # Ensure new points lie inside points otherwise set to 99999
            # Find smallest distance from old to new point 
            if inside is False:
                G = G - rVert[:, None, :]
                GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G))
                GInd = GMag.argmin(axis=1)
            else:
                G, GInd = self.calcBarycentric(rVert, G, ind)
            # Define vector from baseline point to intersect point
            D = G[np.arange(len(G)), GInd, :]
            rVert += D/step
            if smooth > 0 and step > 1:
#                v = self.reg.vert[~subset]
                self.reg.lp_smooth(smooth, brim = fixBrim)
#                self.reg.vert[~subset] = v
            else:
                self.reg.calcNorm()
        
        self.reg.calcStruct()
#        self.reg.values[:] = self.calcError(False)
        self.reg.values[:] = self.calcError(error)
        
    def calcError(self, direct=True):
        r"""
        Calculate the magnitude of distances between the baseline and registered array
		
        Parameters
        ----------
        direct: bool, default True
            If true, the magnitude can be positive or negative depending on whether the registered
            vertex is inside or outside the baseline surface

        Returns
        -------
        values: array_like
            Magnitude of distances

        """
        if direct is True:
            self.b.calcVNorm()
            values = np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
            # Calculate the unit vector normal between corresponding vertices
            # baseline and target
#            vector = (self.reg.vert - self.b.vert)/values[:, None]
#            # Calculate angle between the two unit vectors using normal of cross
#            # product between vNorm and vector and dot
#            normcrossP = np.linalg.norm(np.cross(vector, self.b.vNorm), axis=1)
#            dotP = np.einsum('ij,ij->i', vector, self.b.vNorm)
#            angle = np.arctan2(normcrossP, dotP)
#            polarity = np.ones(angle.shape)
#            polarity[angle < np.pi/2] =-1.0
            cent = self.b.vert.mean(axis=0)
            r = np.linalg.norm(self.reg.vert - cent, axis=1)
            b = np.linalg.norm(self.b.vert - cent, axis=1)
            polarity = np.ones([self.reg.vert.shape[0]])
            polarity[r<b] = -1
            values = values * polarity
            return values
        else:
            values = np.linalg.norm(self.reg.vert - self.b.vert, axis=1)
            return values
        
    def calcBarycentric(self, vert, G, ind):
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
        GInd: array_like
            The index of the shortest distance between each baseline vertex and the registered vertex
            
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
        G = G - vert[:, None, :]
        GMag = np.sqrt(np.einsum('ijk, ijk->ij', G, G))
        GInd = GMag.argmin(axis=1)
        return G, GInd
