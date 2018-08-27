# -*- coding: utf-8 -*-
"""
Package for dealing with trimming the AmpObject mesh
Copyright: Joshua Steer 2018, Joshua.Steer@soton.ac.uk
"""

import numpy as np

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
        >>> amp = AmpObject(fh)
        >>> amp.planarTrim(100, 2)

        """
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
        self.calcStruct()