# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:54:23 2017

@author: js22g12

Core functions for the AmpObject

Remove pd dependency and instead just use numpy arrays

Requires numpy 1.13

import os
path = (r'J:\\Shared Resources\\AmpScan IfLS Team\\'
        '100 PYTHON\\STLReader')
path = r'\\filestore.soton.ac.uk\SharedResources\AmpScan IfLS Team\100 PYTHON\STLReader'
path = (r'C:\Users\js22g12\OneDrive - University of Southampton\Documents ' 
        r'(OneDrive)\AmpScan\Code\2017_09\02_Code\AmpScan')
path = (r'C:\Users\Josh\OneDrive - University of Southampton\Documents '
        r'(OneDrive)\AmpScan\Code\2017_09\02_Code\AmpScan')
filename = '01_PhantomShell_ICEM_3mm.stl'
filename2 = '01_PhantomShell_ICEM_3mm_write.stl'
os.chdir(path)

AmpObject
    Read
    Write
    Centre
    Translate
    Rotate
    lp_smooth
    trimming
    alignment
Residuum
Socket
    SocketICP (overwrite)
    SocketBrimLine
Registration
SoftTissueDepth
    Bones
    Liner
Finite Element Analysis 
    FE Mesh
    FE Data
"""

import numpy as np
import struct
from autoAlign import alignMixin
from trim import trimMixin
from smooth import smoothMixin
from analyse import analyseMixin
from ampVis import visMixin
from fe import feMixin
from tsbSocketDesign import socketDesignMixin

class AmpObject(alignMixin, trimMixin, smoothMixin, analyseMixin, 
                visMixin, feMixin, socketDesignMixin):

    def __init__(self, Data, stype):
        self.stype = []
        self.actors = {}
        if stype in ['limb', 'socket', 'reglimb', 'regsocket', 'MRI']:
            self.addData(Data, stype)
        elif stype is 'AmpObj':
            for d in Data.stype:
                setattr(self, d, getattr(Data, d))
                self.stype.append(d)
            self.actors = Data.actors
        elif stype is 'FE':
            self.addFE([Data,])
        else:
            raise ValueError('dtype  not supported, please choose from ' + 
                             'limb, socket, reglimb, regsocket, MRI or AmpObj')

    
    def addData(self, Data, stype):
        if isinstance(Data, basestring):
            self.stype.append(stype)
            self.read_stl(Data, stype)
            # Import stl as filename
        elif isinstance(Data, dict):
            self.stype.append(stype)
            setattr(self, stype, Data)

    def read_stl(self, filename, stype=0, unify=True, edges=True):
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
        if isinstance(stype, int):
            stype = self.stype[stype]
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
        setattr(self, stype, dict(zip(['vert', 'faces', 'norm'],
                                      [vert, faces, norm])))
        # Call function to unify vertices of the array
        if unify is True:
            self.unify_vertices(stype)
        # Call function to calculate the edges array
        if edges is True:
            self.computeEdges(stype)

    def unify_vertices(self, stype=0):
        """
        Function to unify coincident vertices of the mesh to reduce
        size of the vertices array enabling speed increases
        """
        # Requires numpy 1.13
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        data['vert'], indC = np.unique(data['vert'], return_inverse=True, axis=0)
        # Maps the new vertices index to the face array
        data['faces'] = np.resize(indC[data['faces']], (len(data['norm']), 3))

    def computeEdges(self, stype=0):
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
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        # Get edges array
        data['edges'] = np.reshape(data['faces'][:, [0, 1, 0, 2, 1, 2]], [-1, 2])
        data['edges'] = np.sort(data['edges'], 1)
        # Get edges on each face 
        data['edgesFace'] = np.reshape(range(len(data['faces'])*3), [-1,3])
        # Unify the edges
        data['edges'], indC = np.unique(data['edges'], return_inverse=True, axis=0)
        #Remap the edgesFace array 
        data['edgesFace']  = indC[data['edgesFace'] ]
        #Initiate the faceEdges array
        data['faceEdges'] = np.empty([len(data['edges']), 2])
        data['faceEdges'].fill(np.nan)
        # Denote the face index for flattened edge array
        fInd = np.repeat(np.array(range(len(data['faces']))), 3)
        # Flatten edge array
        eF = np.reshape(data['edgesFace'], [-1])
        eFInd = np.unique(eF, return_index=True)[1]
        logic = np.zeros([len(eF)], dtype=bool)
        logic[eFInd] = True
        data['faceEdges'][eF[logic], 0] = fInd[logic]
        data['faceEdges'][eF[~logic], 1] = fInd[~logic]

    def save(self, filename, stype=0):
        """
        Function to save the AmpObj as a binary .stl file 
        
        Parameters
        -----------
        filename: str
            file path of the .stl file to save to
        """
        if isinstance(stype, int):
            stype = self.stype[stype]
        self.calc_norm(stype)
        data = getattr(self, stype)
        fv = data['vert'][np.reshape(data['faces'], len(data['faces'])*3)]
        fh = open(filename, 'wb')
        data_type = np.dtype([('normals', np.float32, (3, )),
                              ('vertices', np.float32, (9, )),
                              ('atttr', '<i2', (1, ))])
        header = '%s' % (filename)
        header = header[:80].ljust(80, ' ')
        packed = struct.pack('@i', len(data['faces']))
        fh.write(header)
        fh.write(packed)
        data_type = np.dtype([('normals', np.float32, (3, )),
                              ('vertices', np.float32, (9, )),
                              ('atttr', '<i2', (1, ))])
        data_write = np.zeros(len(data['faces']), dtype=data_type)
        data_write['normals'] = data['norm']
        data_write['vertices'] = np.reshape(fv, (len(data['faces']), 9))
        data_write.tofile(fh)
        fh.close()

    def calc_norm(self, stype=0):
        """
        Calculate the normal of each face of the AmpObj
        """
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        norms = np.cross(data['vert'][data['faces'][:,1]] -
                         data['vert'][data['faces'][:,0]],
                         data['vert'][data['faces'][:,2]] -
                         data['vert'][data['faces'][:,0]])
        mag = np.linalg.norm(norms, axis=1)
        data['norm'] = np.divide(norms, mag[:,None])

    def man_trans(self, trans, stype=0):
        """
        Translate the AmpObj in 3D space

        Parameters
        -----------
        trans: array-like
            1x3 array of the tranlation in [x, y, z]
        """
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        data['vert'] += trans

    def centre(self, stype=0):
        """
        Centre the AmpObj based upon the mean of all the vertices
        """
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        self.man_trans(-data['vert'].mean(axis=0))

    def man_rot(self, rot, stype=0):
        """
        Rotate the AmpObj in 3D space and re-calculate the normals 
        
        Parameters
        -----------
        rot: array-like
            1x3 array of the rotation around [x, y, z]
        """
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        Id = np.identity(3)
        for i, r in enumerate(rot):
            if r != 0:
                ax = Id[i, :]
                ang = np.deg2rad(rot[i])
                dot = np.reshape(data['vert'][:, 0] * ax[0] +
                                 data['vert'][:, 1] * ax[1] +
                                 data['vert'][:, 2] * ax[2], (-1, 1))
                data['vert'] = (data['vert'] * np.cos(ang) +
                                np.cross(ax, data['vert']) * np.sin(ang) +
                                np.reshape(ax, (1, -1)) * dot * (1-np.cos(ang)))
        self.calc_norm()
