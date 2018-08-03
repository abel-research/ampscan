# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:22:29 2017

@author: js22g12
"""

import numpy as np

class trimMixin(object):
    r"""
    docstring

    """
    
    def planarTrim(self, height, plane = 'z'):
        r"""
        Trim the vertices according to a flat plane

        Parameters
        -----------
        height: float
            Trim height, values above this will be deleted
        plane: str: 'x', 'y' or 'z'
            plane for slicing
        """
        if plane == 'z': 
            p = 2
        # planar values for each vert on face 
        fv = self.vert[self.faces, p]
        # Number points on each face are above cut plane
        fvlogic = (fv > height).sum(axis=1)
        # Faces with points both above and below cut plane
        adjf = self.faces[np.logical_or(fvlogic == 2, fvlogic == 1)]
        # Get adjacent vertices
        adjv = np.unique(adjf)
        # Get vert above height and set to height
        abvInd = adjv[self.vert[adjv, p] > height]
        self.vert[abvInd, p] = height
        # Find all verts above plane
        delv = self.vert[:, p] > height
        # Reorder verts to account for deleted one
        vInd = np.cumsum(~delv) - 1
        self.faces = self.faces[fvlogic != 3, :]
        self.faces = vInd[self.faces]
        self.vert = self.vert[~delv, :]
        self.calcStruct()