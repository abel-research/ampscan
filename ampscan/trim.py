# -*- coding: utf-8 -*-
"""
Package for dealing with trimming the AmpObject mesh
Copyright: Joshua Steer 2019, Joshua.Steer@soton.ac.uk
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
