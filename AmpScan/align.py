# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:15:30 2017

@author: js22g12
"""

import numpy as np
from scipy import spatial
from scipy.optimize import minimize


def align(moving, static, method = 'P2P'):
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

    def icp():
        """
        Automated alignment function between two meshes
        
        """

        tTree = spatial.cKDTree(self.baseline.vert)
        rot = np.array([0,0,0], dtype=float)
        res = minimize(self.calcDistError, rot, method='BFGS',
                       options={'gtol':1e-6, 'disp':True})
        
        
    def calcDistError(rot, tTree):
        """
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
    
    return moving

def rotMatrix(R, ang='rad'):
    r"""
    Needs desc @josh_steer

    """
    if ang == 'deg':
        R = np.deg2rad(R)
    angx = R[0]
    angy = R[1]
    angz = R[2]
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
    return R