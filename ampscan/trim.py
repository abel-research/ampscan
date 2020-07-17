# -*- coding: utf-8 -*-
"""
Package for dealing with trimming the AmpObject mesh
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk
"""

import numpy as np
from ampscan import AmpObject
from numbers import Number
import os
from scipy import spatial
import copy

# Used by doc tests
filename = os.path.join(os.getcwd(), "tests", "stl_file.stl")


class trimMixin(object):
    r"""
    Methods for trimming the AmpObject mesh

    """
    
    def planarTrim(self, height, plane = 2, above = True):
        r"""
        Trim the vertices using a flat plane, all vertices above plane will be 
        trimmed

        Parameters
        -----------
        height: float
            Trim height, values above this will be deleted
        plane: int, default 2
            plane for slicing
        
        Examples
        --------

        >>> from ampscan import AmpObject
        >>> amp = AmpObject(filename)
        >>> amp.planarTrim(100, 2)

        """
        if isinstance(height, Number) and isinstance(plane, int):
            # planar values for each vert on face 
            fv = self.vert[self.faces, plane]
            # Number points on each face are above cut plane
            fvlogic = (fv > height).sum(axis=1)
            # Faces with points both above and below cut plane
            adjf = self.faces[np.logical_or(fvlogic == 2, fvlogic == 1)]
            # Get adjacent vertices
            adjv = np.unique(adjf)
            # Get vert above height and set to height
            abvInd = adjv[self.vert[adjv, plane] > height]
            self.vert[abvInd, plane] = height
            # Find all verts above plane
            delv = self.vert[:, plane] > height
            # Reorder verts to account for deleted one
            vInd = np.cumsum(~delv) - 1
            self.faces = self.faces[fvlogic != 3, :]
            self.faces = vInd[self.faces]
            self.vert = self.vert[~delv, :]
            self.values = self.values[~delv]
            self.calcStruct()
        else:
            raise TypeError("height arg must be a float")


    def threePointTrim(self, p0, p1, p2, above = True):
        r"""
        Trim the vertices using a plane defined by three points. By default, all points  
        above the plane are deleted.

        Parameters
        -----------
        p0: array_like 
            The co-ordinates of the first point to define the plane
        p1: array_like 
            The co-ordinates of the second point to define the plane
        p2: array_like 
            The co-ordinates of the third point to define the plane

        
        Examples
        --------

        >>> from ampscan import AmpObject
        >>> amp = AmpObject(filename)
        >>> p0 = [50, 50, 0]
        >>> p1 = [50, -50, -40]
        >>> p2 = [-50, 50, 10]
        >>> amp.threePointTrim(p0, p1, p2)

        """
        # Ensure asarrays
        p0 = np.asarray(p0)
        p1 = np.asarray(p1)
        p2 = np.asarray(p2)

        # Calculate plane 
        v0 = p1 - p0
        v1 = p2 - p0
        c = np.cross(v0, v1)
        c = c/np.linalg.norm(c)
        k = -np.multiply(c, p0).sum()
        # planar values for each vert on face 
        height = -(self.vert[:, 0]*c[0] + self.vert[:, 1]*c[0] + k)/c[2]
        # Number points on each face are above cut plane
        fv = self.vert[self.faces, 2]
        fvHeight = height[self.faces]
        fvlogic = (fv > fvHeight).sum(axis=1)
        # Faces with points both above and below cut plane
        adjf = self.faces[np.logical_or(fvlogic == 2, fvlogic == 1)]
        # Get adjacent vertices
        adjv = np.unique(adjf)
        # Get vert above height and set to height
        abvInd = adjv[self.vert[adjv, 2] > height[adjv]]
        self.vert[abvInd, 2] = height[abvInd]
        # Find all verts above plane
        delv = self.vert[:, 2] > height
        # Reorder verts to account for deleted one
        vInd = np.cumsum(~delv) - 1
        self.faces = self.faces[fvlogic != 3, :]
        self.faces = vInd[self.faces]
        self.vert = self.vert[~delv, :]
        self.values = self.values[~delv]
        self.calcStruct()
    
    @staticmethod
    def dynamictrim(s, m, maxdist = 20):
        """
        This function trims vertices and faces from the m mesh. It calculates 
        the distance between the m mesh centroids and their nearest neighbour 
        on the s mesh. If this distance is more than maxdist, the face is 
        removed, and subsequently the vertices no longer connected to a face.
                                            
        Parameters
        ----------
        s : AmpObject
            The target object
        m : AmpObject
            The active object. This is the object where faces/vertices will be
            removed.
        maxdist : float
            The threshold distance. Faces on the m mesh that have a higher 
            distance with their nearest neighbour on the s mesh than maxdist
            will be removed, as will the vertices no longer connected to a 
            face afterwards.
            
        Returns
        -------
        m : AmpObject
            The edited object.
        """
        
        kdTree = spatial.cKDTree(s.vert)
        fC = m.vert[m.faces].mean(axis=1)
        [dist, idx] = kdTree.query(fC,1)
        faceid = []
        vertid = []
        for i in range(len(dist)):
            if np.absolute(dist[i]) < maxdist:
                faceid.append(i)
        faces = np.zeros([len(faceid), 3], dtype=int)
        for i in faceid:
            vertid.append(m.faces[i,0])
            vertid.append(m.faces[i,1])
            vertid.append(m.faces[i,2])
        vertid = list(dict.fromkeys(vertid))
        vertices = m.vert[vertid,:]
        
        for i in range(len(faceid)):
            faces[i,0] = vertid.index(m.faces[faceid[i],0])
            faces[i,1] = vertid.index(m.faces[faceid[i],1])
            faces[i,2] = vertid.index(m.faces[faceid[i],2])
        
        mData = dict(zip(['vert', 'faces', 'values'], 
                             [vertices, 
                              faces, 
                              m.values[vertid]]))
        preppedData = copy.deepcopy(mData)
        m = AmpObject(preppedData, stype='reg')
        return m