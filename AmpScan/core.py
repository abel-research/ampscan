# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:54:23 2017

@author: js22g12

Core functions for the AmpObject

Requires numpy 1.13

"""

import numpy as np
import struct
from .align import rotMatrix
from .trim import trimMixin
from .smooth import smoothMixin
from .analyse import analyseMixin
from .ampVis import visMixin
from .fe import feMixin
from .tsbSocketDesign import socketDesignMixin

class AmpObject(trimMixin, smoothMixin, analyseMixin, 
                visMixin, feMixin, socketDesignMixin):
    """
    Numpy style docstring.

    """

    def __init__(self, data=None, stype='limb'):
        self.stype = stype
        self.createCMap()
        if isinstance(data, str):    
            if stype == 'FE':
                self.addFE([data,])
            else:
                self.read_stl(data)
        elif isinstance(data, dict):
            for k, v in data.items():
                setattr(self, k, v)
            if stype == 'FE':
                self.getSurf()
            else:
                self.calcStruct()
    
    def createCMap(self, cmap=None, n = 50):
        """
        Function to generate a colormap for the AmpObj

        """
        if cmap is None:
            c1 = [31.0, 73.0, 125.0]
            c3 = [170.0, 75.0, 65.0]
            c2 = [212.0, 221.0, 225.0]
            CMap1 = np.c_[[np.linspace(st, en) for (st, en) in zip(c1, c2)]]
            CMap2 = np.c_[[np.linspace(st, en) for (st, en) in zip(c2, c3)]]
            CMap = np.c_[CMap1[:, :-1], CMap2]
            self.CMapN2P = np.transpose(CMap)/255.0
            self.CMap02P = np.flip(np.transpose(CMap1)/255.0, axis=0)


    def read_stl(self, filename, unify=True):
        """
        Function to read .stl file from filename and import data into 
        the AmpObj 
        
        Parameters
        -----------
        filename: str 
            file path of the .stl file to read 
        unify: boolean, default True
            unify the coincident vertices of each face
        edges: boolean, default True
            calculate the edges array automatically

        """
        fh = open(filename, 'rb')
        # Defined no of bytes for header and no of faces
        HEADER_SIZE = 80
        COUNT_SIZE = 4
        # State the data type and length in bytes of the normals and vertices
        data_type = np.dtype([('normals', np.float32, (3, )),
                              ('vertices', np.float32, (9, )),
                              ('atttr', '<i2', (1, ))])
        # Read the header of the STL
        fh.read(HEADER_SIZE).lower()
        # Read the number of faces
        NFaces, = struct.unpack('@i', fh.read(COUNT_SIZE))
        # Read the remaining data and save as void, then close file
        data = np.fromfile(fh, data_type)
        fh.close()
        # Write the data to a numpy arrays in AmpObj
        vert = np.resize(np.array(data['vertices']), (NFaces*3, 3))
        norm = np.array(data['normals'])
        faces = np.reshape(range(NFaces*3), [-1,3])
        self.faces = faces
        self.vert = vert
        self.norm = norm
        self.values = np.zeros([len(self.vert)])
        # Call function to unify vertices of the array
        if unify is True:
            self.unifyVert()
        # Call function to calculate the edges array
        self.calcStruct()
        
    def calcStruct(self, norm=True, edges=True, 
                   edgeFaces=True, faceEdges=True, vNorm=False):
        if norm is True:
            self.calcNorm()
        if edges is True:
            self.calcEdges()
        if edgeFaces is True:
            self.calcEdgeFaces()
        if faceEdges is True:
            self.calcFaceEdges()
        if vNorm is True:
            self.calcVNorm()

    def unifyVert(self):
        """
        Function to unify coincident vertices of the mesh to reduce
        size of the vertices array enabling speed increases

        """
        # Requires numpy 1.13
        self.vert, indC = np.unique(self.vert, return_inverse=True, axis=0)
        # Maps the new vertices index to the face array
        self.faces = np.resize(indC[self.faces], 
                               (len(self.norm), 3)).astype(np.int32)

    def calcEdges(self):
        """
        Function to compute the edges array, the edges on each face, 
        and the faces on each edge

        edges: numpy array N x 2 denotes the indicies of two vertices 
            on each edge
        edgesFace: numpy array N x 3 denotes the indicies of the three edges 
            on each face
        faceEdges: numpy array N x 2 denotes the indicies of the faces in each 
            edge, edges may have either 1 or 2 faces, if 1 then the second 
            index will be NaN

        """
        # Get edges array
        self.edges = np.reshape(self.faces[:, [0, 1, 0, 2, 1, 2]], [-1, 2])
        self.edges = np.sort(self.edges, 1)
        # Unify the edges
        self.edges, indC = np.unique(self.edges, return_inverse=True, axis=0)

    def calcEdgeFaces(self):
        edges = np.reshape(self.faces[:, [0, 1, 0, 2, 1, 2]], [-1, 2])
        edges = np.sort(edges, 1)
        # Unify the edges
        edges, indC = np.unique(edges, return_inverse=True, axis=0)
        # Get edges on each face 
        self.edgesFace = np.reshape(range(len(self.faces)*3), [-1,3])
        #Remap the edgesFace array 
        self.edgesFace = indC[self.edgesFace].astype(np.int32)

    def calcFaceEdges(self):
        #Initiate the faceEdges array
        self.faceEdges = np.empty([len(self.edges), 2], dtype=np.int32)
        self.faceEdges.fill(-99999)
        # Denote the face index for flattened edge array
        fInd = np.repeat(np.array(range(len(self.faces))), 3)
        # Flatten edge array
        eF = np.reshape(self.edgesFace, [-1])
        eFInd = np.unique(eF, return_index=True)[1]
        logic = np.zeros([len(eF)], dtype=bool)
        logic[eFInd] = True
        self.faceEdges[eF[logic], 0] = fInd[logic]
        self.faceEdges[eF[~logic], 1] = fInd[~logic]        
        

    def calcNorm(self):
        """
        Calculate the normal of each face of the AmpObj

        """
        norms = np.cross(self.vert[self.faces[:,1]] -
                         self.vert[self.faces[:,0]],
                         self.vert[self.faces[:,2]] -
                         self.vert[self.faces[:,0]])
        mag = np.linalg.norm(norms, axis=1)
        self.norm = np.divide(norms, mag[:,None])
        
    def calcVNorm(self):
        """
        Function to compute the vertex normals
        Not required for the AmpActor but may be needed for ICP

        """
        f = self.faces.flatten()
        o_idx = f.argsort()
        row, col = np.unravel_index(o_idx, self.faces.shape)
        ndx = np.searchsorted(f[o_idx], range(self.vert.shape[0]), side='right')
        ndx = np.r_[0, ndx]
        norms = self.norm[self.faces, :][row, col, :]
        self.vNorm = np.zeros(self.vert.shape)
        for i in range(self.vert.shape[0]):
            self.vNorm[i, :] = norms[ndx[i]:ndx[i+1], :].mean(axis=0)

    def save(self, filename):
        """
        Function to save the AmpObj as a binary .stl file 
        
        Parameters
        -----------
        filename: str
            file path of the .stl file to save to

        """
        self.calc_norm()
        fv = self.vert[np.reshape(self.faces, len(self.faces)*3)]
        fh = open(filename, 'wb')
        header = '%s' % (filename)
        header = header[:80].ljust(80, ' ')
        packed = struct.pack('@i', len(data['faces']))
        fh.write(header)
        fh.write(packed)
        data_type = np.dtype([('normals', np.float32, (3, )),
                              ('vertices', np.float32, (9, )),
                              ('atttr', '<i2', (1, ))])
        data_write = np.zeros(len(self.faces), dtype=data_type)
        data_write['normals'] = self.norm
        data_write['vertices'] = np.reshape(fv, (len(self.faces), 9))
        data_write.tofile(fh)
        fh.close()

    def translate(self, trans):
        """
        Translate the AmpObj in 3D space

        Parameters
        -----------
        trans: array-like
            1x3 array of the tranlation in [x, y, z]

        """
        self.vert[:] += trans

    def centre(self):
        """
        Centre the AmpObj based upon the mean of all the vertices

        """
        self.translate(-self.vert.mean(axis=0))
    
    def rotate(self, rot, ang='rad'):
        R = rotMatrix(rot, ang)
        self.vert[:, :] = np.dot(self.vert, np.transpose(R))

    def man_rot(self, rot):
        """
        Rotate the AmpObj in 3D space and re-calculate the normals 
        
        Parameters
        -----------
        rot: array-like
            1x3 array of the rotation around [x, y, z]
            
        Update this so calculated using matrices

        """
        Id = np.identity(3)
        for i, r in enumerate(rot):
            if r != 0:
                ax = Id[i, :]
                ang = np.deg2rad(rot[i])
                dot = np.reshape(self.vert[:, 0] * ax[0] +
                                 self.vert[:, 1] * ax[1] +
                                 self.vert[:, 2] * ax[2], (-1, 1))
                self.vert = (self.vert * np.cos(ang) +
                             np.cross(ax, self.vert) * np.sin(ang) +
                             np.reshape(ax, (1, -1)) * dot * (1-np.cos(ang)))
        self.calc_norm()
