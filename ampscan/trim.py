# -*- coding: utf-8 -*-
"""
Package for dealing with trimming the AmpObject mesh
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk
"""

import numpy as np
from numbers import Number
import os

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