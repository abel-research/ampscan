# -*- coding: utf-8 -*-
"""
Package for defining the core AmpObject
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk

"""

import numpy as np
import os
import struct
import math

from pyrsistent import v
from ampscan.trim import trimMixin
from ampscan.smooth import smoothMixin
from ampscan.vis import visMixin
from .analyse import create_slices, calc_perimeter, logEuPath


# The file path used in doc examples
filename = os.path.join(os.getcwd(), "tests", "stl_file.stl")


class AmpObject(trimMixin, smoothMixin, visMixin):
    r"""
    Base class for the ampscan project.
    Stores mesh data and extra information 
    Inherits methods via mixins
    Flexible class able to deal with surface data using 3 or 4 node faces and 
    visualise nodal data such as FEA outputs or shape deviations
    
    Parameters
    ----------
    data : str or dict
        Data input as either a string to import from an external file or a 
        dictionary to pull values directly
    stype : str, optional
        descriptor of the type of data the AmpObject is representing, e.g 
        'limb' or 'socket'. Default is 'limb'
    
    Returns
    -------
    AmpObject
        Initiation of the object
    
    Examples
    -------
    >>> amp = AmpObject(filename)

    """

    def __init__(self, data=None, stype='limb', unify=True, struc=True):
        self.stype = stype
        self.createCMap()
        self.landmarks = {}
        if isinstance(data, str):
            if data.lower().endswith('.aop'):
                self.read_aop(data, unify, struc)
            else:
                self.read_stl(data, unify, struc)
        elif isinstance(data, dict):
            for k, v in data.items():
                setattr(self, k, v)
            if struc is True:
                self.calcStruct()
        elif isinstance(data, bytes):
            self.read_bytes(data, unify, struc)

    


    def read_stl(self, filename, unify=True, struc=True):
        """
        Function to read .stl file from filename and import data into 
        the AmpObj 
        
        Parameters
        -----------
        filename: str 
            file path of the .stl file to read 
        unify: boolean, default True
            unify the coincident vertices of each face
        struc: boolean, default True
            Calculate the underlying structure of the mesh, such as edges

        """
        with open(filename, 'rb') as fh:
        # Defined no of bytes for header and no of faces
            HEADER_SIZE = 80
            COUNT_SIZE = 4
            # State the data type and length in bytes of the normals and vertices
            data_type = np.dtype([('normals', np.float32, (3, )),
                                  ('vertices', np.float32, (9, )),
                                  ('atttr', '<i2', (1, ))])
            # Read the header of the STL
            head = fh.read(HEADER_SIZE).lower()
            # Read the number of faces
            NFaces, = struct.unpack('@i', fh.read(COUNT_SIZE))
            # Read the remaining data and save as void, then close file
            data = np.fromfile(fh, data_type)
        # Test if the file is ascii
        if str(head[:5], 'utf-8') == 'solid':
            raise ValueError("ASCII files not supported")
        # Write the data to a numpy arrays in AmpObj
        tfcond = NFaces==data['vertices'].shape[0]			#assigns true or false to tfcond
        if not tfcond:							#if tfcond is false, raise error
            raise ValueError("File is corrupt")							#if true, move on
        vert = np.resize(np.array(data['vertices']), (NFaces*3, 3))
        norm = np.array(data['normals'])
        faces = np.reshape(range(NFaces*3), [NFaces,3])
        self.faces = faces
        self.vert = vert
        self.norm = norm
        
        # Call function to unify vertices of the array
        if unify is True:
            self.unifyVert()
        # Call function to calculate the edges array
#        self.fixNorm()
        if struc is True:
            self.calcStruct()
        self.values = np.zeros([len(self.vert)])

    def read_bytes(self, data, unify=True, struc=True):
        """
        Function to read .stl file from filename and import data into 
        the AmpObj 
        
        Parameters
        -----------
        filename: str 
            file path of the .stl file to read 
        unify: boolean, default True
            unify the coincident vertices of each face
        struc: boolean, default True
            Calculate the underlying structure of the mesh, such as edges

        """
        # Defined no of bytes for header and no of faces
        HEADER_SIZE = 80
        COUNT_SIZE = 4
        # State the data type and length in bytes of the normals and vertices
        data_type = np.dtype([('normals', np.float32, (3, )),
                                ('vertices', np.float32, (9, )),
                                ('atttr', '<i2', (1, ))])
        # Read the header of the STL
        head = data[:HEADER_SIZE].lower()
        # Read the number of faces
        NFaces, = struct.unpack('@i', data[HEADER_SIZE:HEADER_SIZE+COUNT_SIZE])
        # Read the remaining data and save as void, then close file
        data = np.frombuffer(data[COUNT_SIZE+HEADER_SIZE:], data_type)
        # Test if the file is ascii
        if str(head[:5], 'utf-8') == 'solid':
            raise ValueError("ASCII files not supported")
        # Write the data to a numpy arrays in AmpObj
        tfcond = NFaces==data['vertices'].shape[0]			#assigns true or false to tfcond
        if not tfcond:							#if tfcond is false, raise error
            raise ValueError("File is corrupt")							#if true, move on
        vert = np.resize(np.array(data['vertices']), (NFaces*3, 3))
        norm = np.array(data['normals'])
        faces = np.reshape(range(NFaces*3), [NFaces,3])
        self.faces = faces
        self.vert = vert
        self.norm = norm
        
        # Call function to unify vertices of the array
        if unify is True:
            self.unifyVert()
        # Call function to calculate the edges array
#        self.fixNorm()
        if struc is True:
            self.calcStruct()
        self.values = np.zeros([len(self.vert)])

    def read_aop(self, filename, unify=True, struc=True):
        """
        Function to read .aop file from filename and import data into 
        the AmpObj 
        
        Parameters
        -----------
        filename: str 
            file path of the .stl file to read 
        struc: boolean, default True
            Calculate the underlying structure of the mesh, such as edges
        
        To access the landmarks use te getLandmarks() methods after the file 
        has been imported

        """
        with open(filename, 'r') as f: 
            lines = f.read().splitlines()
        lID = 0
        maxID = len(lines)
        version = lines[lID]
        lID =+ 1
        # File comments
        comments = ""
        while lID < maxID:
            if "END COMMENTS" == lines[lID]:
                lID += 1
                break
            else:
                comments += lines[lID] + "\n"
                lID += 1
        # CYS 
        cys = lines[lID]
        lID +=1
        if cys != "CYLINDRICAL":
            return ValueError('AOP Reader only accepts files in CYLINDRICAL cys')
        # Orientation
        side = lines[lID]
        lID += 1
        # Landmarks 
        nLand = int(lines[lID])
        lID += 1
        self.landmarks = {}
        # For each landmark
        for i in range(nLand):
            landName = lines[lID]
            lID += 1
            nPoints = int(lines[lID])
            lID += 1
            points = np.zeros([nPoints, 3])
            # For each point in the landmark
            for j in range(nPoints):
                r = float(lines[lID])
                lID += 1
                theta = np.deg2rad(float(lines[lID]))
                lID += 1
                z = float(lines[lID])
                lID += 1
                # Convert to cartesian 
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                points[j, :] = [x, y, z]
            self.landmarks[landName] = points
        # file parameters
        # spokes 
        nSpokes = int(lines[lID])
        lID += 1
        spokeDist = np.deg2rad(float(lines[lID]))
        lID += 1
        # Create the spokes array
        if spokeDist == 0: 
            # Irregular spacing so read in 
            spokes = []
            for i in range(nSpokes):
                spokes.append(np.deg2rad(float(lines[lID])))
                lID += 1
            spokes = np.asarray(spokes)
        else:
            # regular spacing so compute 
            spokes = np.arange(-0.5*np.pi, 1.5*np.pi, spokeDist)
            spokes = np.flip(spokes)

        # slices
        nSlices = int(lines[lID])
        lID += 1
        sliceDist = float(lines[lID])
        lID += 1
        # Create the slices array
        if sliceDist == 0: 
            # Irregular spacing so read in 
            slices = []
            for i in range(nSlices):
                slices.append(float(lines[lID]))
                lID += 1
            slices = np.asarray(slices)
        else:
            # regular spacing so compute 
            slices = np.array([i * sliceDist for i in range(nSlices)])

        # set up the vert and faces arrays 
        nVerts = nSlices * nSpokes;
        nFaces = (nSlices - 1) * (nSpokes * 2);
        self.vert = np.zeros([nVerts, 3], dtype=float)
        self.faces = np.zeros([nFaces, 3], dtype=int)
        self.values = np.zeros([len(self.vert)])
        # Read in the radii as verts
        for i in range(nSlices):
            z = slices[i];
            for j in range(nSpokes):
                idx = (i * nSpokes) + j;
                line = lines[lID].split(' ')
                r = float(line[0])
                if len(line) > 1:
                    try: 
                        self.values[idx] = float(line[1])
                    except:
                        self.values[idx] = 0
                theta = spokes[j];
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                self.vert[idx, :] = [x, y, z]
                lID += 1
        # Construct faces array 
        fidx = 0;
        for sl in range(nSlices - 1):
            cur_stack_idx = sl * nSpokes;
            next_stack_idx = (sl + 1) * nSpokes;
            for sp in range(nSpokes):
                next_spoke = (sp + 1) % nSpokes;
                v0 = cur_stack_idx + sp;
                v1 = cur_stack_idx + next_spoke;
                v2 = next_stack_idx + next_spoke;
                v3 = next_stack_idx + sp;
                self.faces[fidx, :] = [v0, v3, v1];
                self.faces[fidx + 1, :] = v1, v3, v2;
                fidx += 2;
        # Call function to unify vertices of the array
        self.calcStruct()
        if unify is True:
            self.unifyVert()
        # Call function to calculate the edges array
#        self.fixNorm()
        if struc is True:
            self.calcStruct()
        
        
    def calcStruct(self, norm=True, edges=True, 
                   edgeFaces=True, faceEdges=True, vNorm=False):
        r"""
        Top level function to calculate the underlying structure of the 
        AmpObject
        
        Parameters
        ----------
        norm: boolean, default True
            If true, the normals of each face in the mesh will be calculated
        edges: boolean, default True
            If true, the edges of the mesh will be calculated, the refers to
            the vertex index that make up any edge
        edgeFaces: boolean, default True
            If true, the edgeFaces array of the mesh will be calculated, this 
            refers to the index of the three edges that make up each face
        faceEdges: boolean, default True
            If true, the faceEdges array will be calculated, this refers to 
            index of the faces that are coincident to each edge. Normally, 
            there are two faces per edge, if there is only one, then -99999 
            will be used to indicate this 
        vNorm: boolean, default False
            If true, the normals of each vertex in the mesh will be calculated

        """
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

    def getVert(self):
        r"""
        Function to return the vert array
        """
        return self.vert

    def setVert(self, vert):
        r"""
        Function to set the vert array
        """
        self.vert = vert

    def getFaces(self):
        r"""
        Function to return the faces array
        """
        return self.faces

    def setFaces(self, faces):
        r"""
        Function to set the faces array
        """
        self.faces = faces

    def getValues(self):
        r"""
        Function to return the values array
        """
        return self.values

    def setValues(self, values):
        r"""
        Function to set the values array
        """
        self.values = values

    def getLandmarks(self):
        r"""
        Function to return the landmarks dictionary
        """
        return self.landmarks

    def setLandmarks(self, landmarks):
        r"""
        Function to set the landmarks dictionary
        """
        self.landmarks = landmarks

    def unifyVert(self):
        r"""
        Function to unify coincident vertices of the mesh to reduce
        size of the vertices array enabling speed increases when performing
        calculations using the vertex array
        
        Examples
        --------
        >>> amp = AmpObject(filename, unify=False)
        >>> amp.vert.shape
        (44832, 3)
        >>> amp.unifyVert()
        >>> amp.vert.shape
        (7530, 3)

        """
        # Requires numpy 1.13
        self.vert, indC = np.unique(self.vert, return_inverse=True, axis=0)
        # Maps the new vertices index to the face array
        self.faces = np.resize(indC[self.faces], 
                               (len(self.norm), 3)).astype(np.int32)

    def calcEdges(self):
        """
        Function to compute the edges array ie the index of the two vertices
        that make up each edge
        
        Returns
        -------
        edges: ndarray
            Denoting the indicies of two vertices on each edge

        """
        # Get edges array
        self.edges = np.reshape(self.faces[:, [0, 1, 0, 2, 1, 2]], [-1, 2])
        self.edges = np.sort(self.edges, 1)
        # Unify the edges
        self.edges, indC = np.unique(self.edges, return_inverse=True, axis=0)

    def calcEdgeFaces(self):
        r"""
        Function that calculates the indicies of the three edges that make up
        each face 
        
        Returns
        -------
        edgesFace: ndarray
            Denoting the indicies of the three edges on each face
        
        """
        edges = np.reshape(self.faces[:, [0, 1, 0, 2, 1, 2]], [-1, 2])
        edges = np.sort(edges, 1)
        # Unify the edges
        edges, indC = np.unique(edges, return_inverse=True, axis=0)
        # Get edges on each face 
        self.edgesFace = np.reshape(range(len(self.faces)*3), [-1,3])
        #Remap the edgesFace array 
        self.edgesFace = indC[self.edgesFace].astype(np.int32)

    def calcFaceEdges(self):
        r"""
        Function that calculates the indicies of the faces on each edge
        
        Returns
        -------
        faceEdges: ndarray
            The indicies of the faces in each edge, edges may have either 
            1 or 2 faces, if 1 then the second index will be NaN

        """
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
        r"""
        Calculate the normal of each face of the AmpObj
        
        Returns
        -------
        
        norm: ndarray
            normal of each face

        """
        norms = np.cross(self.vert[self.faces[:,1]] -
                         self.vert[self.faces[:,0]],
                         self.vert[self.faces[:,2]] -
                         self.vert[self.faces[:,0]])
        mag = np.linalg.norm(norms, axis=1)
        self.norm = np.divide(norms, mag[:,None])
    
    def fixNorm(self):
        r"""
        Fix normals of faces so they all face outwards 
        """
        fC = self.vert[self.faces].mean(axis=1)
        cent = self.vert.mean(axis=0)
        # polarity = np.sum(self.norm * (fC-cent), axis=1) < 0
        # if polarity.mean() > 0.5:
        #     self.faces[:, [1,2]] = self.faces[:, [2,1]]
        #     self.calcNorm()
        #     if hasattr(self, 'vNorm'): self.calcVNorm()
        polarity  = np.einsum('ij, ij->i', fC - cent, self.norm) < 0
        # self.faces[polarity, [1,2]] = self.faces[polarity, [2,1]]
        for i, f in enumerate(self.faces):
            if polarity[i] == True:
                self.faces[i, :] = [f[0], f[2], f[1]]

        self.calcNorm()
        if hasattr(self, 'vNorm'): self.calcVNorm()
        
    def calcVNorm(self):
        """
        Function to compute the vertex normals based upon the mean of the
        connected face normals 
        
        Returns
        -------
        vNorm: ndarray
            normal of each vertex

        """
        f = self.faces.flatten()
        o_idx = f.argsort()
        row, col = np.unravel_index(o_idx, self.faces.shape)
        ndx = np.searchsorted(f[o_idx], range(self.vert.shape[0]), side='right')
        ndx = np.r_[0, ndx]
        norms = self.norm[row, :]
        self.vNorm = np.zeros(self.vert.shape)
        for i in range(self.vert.shape[0]):
            self.vNorm[i, :] = np.nanmean(norms[ndx[i]:ndx[i+1], :], axis=0)
            

    def save(self, filename):
        r"""
        Function to save the AmpObj as a binary .stl file 
        
        Parameters
        -----------
        filename: str
            file path of the .stl file to save to

        """
        self.calcNorm()
        fv = self.vert[np.reshape(self.faces, len(self.faces)*3)]
        with open(filename, 'wb') as fh:
            header = '%s' % (filename)
            header = header.split('/')[-1].encode('utf-8')
            header = header[:80].ljust(80, b' ')
            packed = struct.pack('@i', len(self.faces))
            fh.write(header)
            fh.write(packed)
            data_type = np.dtype([('normals', np.float32, (3, )),
                                  ('vertices', np.float32, (9, )),
                                  ('atttr', '<i2', (1, ))])
            data_write = np.zeros(len(self.faces), dtype=data_type)
            data_write['normals'] = self.norm
            data_write['vertices'] = np.reshape(fv, (len(self.faces), 9))
            data_write.tofile(fh)

    def save_aop(self, filename, slices=100, spokes=72, sliceInterval = None, spokeInterval = None, closeEnd = True, centreEnd = True, 
                side=None, adaptive=False, commments=None, landmarks=False, returnVerts=False):
        r"""
        Function to save the AmpObj as an aop file 
        
        Parameters
        -----------
        filename: str
            file path of the .aop file to save to
        spokes: int or array_like
            Either number of evenly spaced spokes or an array of spoke theta (in degrees)
        slices: int or array_like
            Either number of evenly spaced slices or an array of slice heights
        spokeInterval: float
            Target spoke interval in degrees, will override spokes variable, must be less than 360
        slicesInterval: float
            Target slice interval in mm, will override slices variable
        closeEnd: bool, default True
            If True, then this will overwrite the most distal slice to close the shpae
        centreEnd: bool, default True
            If True, this will translate the shape so the distal end is centered in the 
            x and y plane
        side: str, default NONE
            Either 'LEFT', 'RIGHT' or 'NONE' for the side
        adaptive: bool, default False
            If True, this will add slices where there is significant change in perimeter 
            between consecutive slices
        comments: str, default None
            Any additional comments to add to the file
        landmarks: dict or bool, default False
            If True, then use the landmarks within the object. Otherwise pass a dictionary 
            with string keys and numpy arrays of size [n x 3] where n is the number of points
            in each landmark. Ensure passed in cartesian co-ordinates for ampscan  
        returnVerts: bool, default False
            if True, return the resampled verts in an N x 3 numpy array in
            cylindrical co-ordinates (r, theta, z)

        """
        
        minZ = self.getVert()[:, 2].min()
        maxZ = self.getVert()[:, 2].max()
        totZ = maxZ - minZ

        if sliceInterval is not None:
            slices = math.floor(totZ/sliceInterval)

        if spokeInterval is not None:
            spokes = math.floor(360/spokeInterval)

        if centreEnd:
            distVLog = self.getVert()[:, 2] < (minZ + (totZ * 0.05))
            xShift = self.getVert()[distVLog, 0].mean()
            yShift = self.getVert()[distVLog, 1].mean()
        else: 
            xShift = 0
            yShift = 0 
        # Get first slices
        delta = 0.001
        ind = 0
        polys = []
        while not polys:
            minSl = minZ + (totZ * ind * delta)
            polys = create_slices(self, [minSl], typ='slices', axis = 2)
            ind += 1
        ind = 0
        polys = []
        while not polys:
            maxSl = maxZ - (totZ * ind * delta)
            polys = create_slices(self, [maxSl], typ='slices', axis = 2)
            ind += 1

        
        lines = []
        lines.append("AAOP1\n")
        lines.append("AAOP1\n")
        if commments:
            lines.append("%s\n" % commments)
        lines.append("Exported from ampscan\n")
        lines.append("Please credit at https://doi.org/10.21105/joss.02060\n")
        lines.append("END COMMENTS\n")
        lines.append("CYLINDRICAL\n")
        # Set side
        if side is None: 
            lines.append("NONE\n")
        else:
            lines.append("%s\n" % side)
        # Set landmarks
        if landmarks is True:
            landmarks = self.getLandmarks()
        elif landmarks is False:
            landmarks = {}
        nLand = len(landmarks)
        lines.append("%i\n" % nLand)
        for landmark, points in landmarks.items():
            # Landmark name
            lines.append("%s\n" % landmark)
            nPoints = points.shape[0]
            lines.append("%i\n" % nPoints)
            for x, y, z in points:
                r = ((x ** 2) + (y ** 2)) ** 0.5
                t = np.rad2deg(np.atan2(y, x))
                z -= minZ
                lines.append("%f\n" % r)
                lines.append("%f\n" % t)
                lines.append("%f\n" % z)
        # Write the spokes 
        if isinstance(spokes, int):
            spacing = (360) / spokes
            spokes = np.arange(-90, 270, spacing)
            nSpokes = len(spokes)
            lines.append("%i\n" % nSpokes)
            lines.append("%f\n" % spacing)
        else:
            spacing = 0
            nSpokes = len(spokes)
            lines.append("%i\n" % nSpokes)
            lines.append("%i\n" % spacing)
            for spoke in spokes:
                lines.append("%f\n" % spoke)

        # Write the slices
        maxZ = self.getVert()[:, 2].max()

        if isinstance(slices, int):
            slices, spacing = np.linspace(minSl, maxSl, slices, retstep=True)
            nSlices = len(slices)
        else:
            spacing = 0
            nSlices = len(slices)

        if adaptive is True:
            minSliceDiff = 0.5
            maxDelta = 0.15
            spacing = 0
            polys = create_slices(self, slices, typ='slices', axis = 2)
            csa = calc_perimeter(polys)
            sliceSpacing = np.diff(slices)
            delta = np.abs(np.diff(csa) / csa[1:])
            maxiter = 0
            while (delta > maxDelta).any() and (sliceSpacing > minSliceDiff).all() and maxiter < 10: 
                
                idx = np.argmax(delta)

                # insert a new slice
                slices = np.insert(slices, idx+1, slices[[idx, idx+1]].mean())
                polys = create_slices(self, slices, typ='slices', axis = 2)
                csa = calc_perimeter(polys)
                sliceSpacing = np.diff(slices)
                delta = np.abs(np.diff(csa) / csa[1:])
                maxiter += 1
            nSlices = len(slices)
        

        lines.append("%i\n" % (nSlices))
        if spacing == 0:
            lines.append("%i\n" % spacing)
            for sl in slices:
                lines.append("%f\n" % (sl - slices[0]))
        else:   
            lines.append("%f\n" % spacing)

        polys = create_slices(self, slices, typ='slices', axis = 2)

        totPoints = len(spokes) * len(slices)
        # print(totPoints)
        vId = 0
        verts = np.zeros([totPoints, 3])

        if closeEnd:
            polys.pop(0)
            for i in range(len(spokes)):
                lines.append("%f\n" % 0)
                verts[vId, :] = [0, spokes[i], 0]
                vId += 1


        for i, p in enumerate(polys):
            x = p[:-1, 0] - xShift
            y = p[:-1, 1] - yShift
            z = slices[i] - minSl
            rPoly = ((x ** 2) + (y ** 2)) ** 0.5
            tPoly = np.rad2deg(np.arctan2(y, x))
            tPoly[tPoly < -90] += 360
            idx = np.argsort(tPoly)
            rPoly = rPoly[idx]
            np.append(rPoly, rPoly[0])
            tPoly = tPoly[idx]
            np.append(tPoly, 270)
            rs = np.interp(spokes, tPoly, rPoly)
            rs = np.flip(rs)
            for j, r in enumerate(rs):
                lines.append("%f\n" % r)
                verts[vId, :] = [r, spokes[j], z]
                vId += 1

        # lines.append("%f\n" % r)
        with open(filename, 'w') as f:
            f.writelines(lines)
        
        if returnVerts:
            return verts




    def translate(self, trans):
        r"""
        Translate the AmpObj in 3D space

        Parameters
        -----------
        trans: array_like
            Translation in [x, y, z]

        """

        # Check that trans is array like
        if isinstance(trans, (list, np.ndarray, tuple)):
            # Check that trans has exactly 3 dimensions
            if len(trans) == 3:
                self.vert[:] += trans
            else:
                raise ValueError("Translation has incorrect dimensions. Expected 3 but found: " + str(len(trans)))
        else:
            raise TypeError("Translation is not array_like: " + trans)

    def centre(self):
        r"""
        Centre the AmpObject based upon the mean of all the vertices

        """
        self.translate(-self.vert.mean(axis=0))

    def scale(self, sf):
        r"""
        Scale the vertices of the AmpObject by some scaling factor 

        Parameters
        ----------
        sf : float
            The scaling factor to apply to the verts

        """
        self.vert *= sf

    def centreStatic(self, static):
        r"""
        Centre this AmpObject on the static AmpObject's centroid based upon the mean of all the vertices

        Parameters
        ----------
        static : AmpObject
            The static shape to center this object onto

        """
        if isinstance(static, AmpObject):
            self.translate(-self.vert.mean(axis=0)+static.vert.mean(axis=0))
        else:
            raise TypeError("centre_static method expects AmpObject, found: {}".format(type(static)))
    
    def rotateAng(self, rot, ang='rad', norms=True):
        r"""
        Rotate the AmpObj in 3D space according to three angles

        Parameters
        -----------
        rot: array_like
            Rotation around [x, y, z]
        ang: str, default 'rad'
            Specify if the euler angles are in degrees or radians. 
            Default is radians
        
        Examples
        --------
        >>> amp = AmpObject(filename)
        >>> ang = [np.pi/2, -np.pi/4, np.pi/3]
        >>> amp.rotateAng(ang, ang='rad')
        """

        # Check that ang is valid
        if ang not in ('rad', 'deg'):
            raise ValueError("Ang expected 'rad' or 'deg' but {} was found".format(ang))

        if isinstance(rot, (tuple, list, np.ndarray)):
            R = self.rotMatrix(rot, ang)
            self.rotate(R, norms)
        else:
            raise TypeError("rotateAng requires a list")

            
    def rotate(self, R, norms=True):
        r"""
        Rotate the AmpObject using a rotation matrix 
        
        Parameters
        ----------
        R: array_like
            A 3x3 array specifying the rotation matrix
        norms: boolean, default True
            
        """
        if isinstance(R, (list, tuple)):
            # Make R a np array if its a list or tuple
            R = np.array(R, np.float)
        elif not isinstance(R, np.ndarray):
            # If
            raise TypeError("Expected R to be array-like but found: " + str(type(R)))
        if len(R) != 3 or len(R[0]) != 3:
            # Incorrect dimensions
            if isinstance(R, np.ndarray):
                raise ValueError("Expected 3x3 array, but found: {}".format(R.shape))
            else:
                raise ValueError("Expected 3x3 array, but found: 3x"+str(len(R)))
        self.vert[:, :] = np.dot(self.vert, R.T)
        if norms is True:
            self.norm[:, :] = np.dot(self.norm, R.T)
            if hasattr(self, 'vNorm'):
                self.vNorm[:, :] = np.dot(self.vNorm, R.T)
            
            
    def rigidTransform(self, R=None, T=None):
        r"""
        Perform a rigid transformation on the AmpObject, first the rotation, 
        then the translation 
        
        Parameters
        ----------
        R: array_like, default None
            A 3x3 array specifying the rotation matrix
        T: array_like, defauly None
            An array of the form [x, y, z] which specifies the translation
            
        """
        if R is not None:
            if isinstance(R, (tuple, list, np.ndarray)):
                self.rotate(R, True)
            else:
                raise TypeError("Expecting array-like rotation, but found: "+type(R))
        if T is not None:
            if isinstance(T, (tuple, list, np.ndarray)):
                self.translate(T)
            else:
                raise TypeError("Expecting array-like translation, but found: "+type(T))
        
    def close(self, overwrite=False):
        amp = AmpObject({
            'vert': self.vert.copy(),
            'faces': self.faces.copy(),
            'values': self.values.copy(),
        })
        amp.calcStruct()
        # Fill in the holes
        while (amp.faceEdges == -99999).sum() != 0: 
            # Find the edges which are only conected to one face
            edges = (amp.faceEdges == -99999).sum(axis=1).astype(bool)
            edges = amp.edges[edges, :]
            # Return the vert indicies for the loop
            vInd = logEuPath(edges)
            # Calculate the mmidpoint 
            midpoint = amp.vert[vInd, :].mean(axis=0)
            # Add in the new vertex
            amp.vert = np.r_[amp.vert, midpoint[None, :]]
            f0 = amp.vert.shape[0] - 1
            # Add in each face using adjacent vertices in loop
            for f1, f2 in zip(vInd, np.roll(vInd, 1)):
                amp.faces = np.r_[amp.faces, [[f1, f0, f2]]]
            # Update structure and check if any more holes (algorithm keeps going until all holes filled)
            amp.calcStruct()
        if overwrite is True:
            self.vert = amp.vert
            self.faces = amp.faces
            self.calcStruct()
        else:
            return amp


    @staticmethod
    def rotMatrix(rot, ang='rad'):
        r"""
        Calculate the rotation matrix from three angles, the order is assumed 
        as around the x, then y, then z axis
        
        Parameters
        ----------
        rot: array_like
            Rotation around [x, y, z]
        ang: str, default 'rad'
            Specify if the Euler angles are in degrees or radians
        
        Returns
        -------
        R: array_like
            The calculated 3x3 rotation matrix 
    
        """

        # Check that rot is valid
        if not isinstance(rot, (tuple, list, np.ndarray)):
            raise TypeError("Expecting array-like rotation, but found: "+type(rot))
        elif len(rot) != 3:
            raise ValueError("Expecting 3 arguments but found: {}".format(len(rot)))

        # Check that ang is valid
        if ang not in ('rad', 'deg'):
            raise ValueError("Ang expected 'rad' or 'deg' but {} was found".format(ang))

        if ang == 'deg':
            rot = np.deg2rad(rot)

        [angx, angy, angz] = rot
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
    
    def flip(self, axis=1):
        r"""
        Flip the mesh in a plane
        
        Parameters
        ----------
        axis: int, default 1
            The axis in which to flip the mesh

        """
        if isinstance(axis, int):
            if 0 <= axis < 3:  # Check axis is between 0-2
                self.vert[:, axis] *= -1.0
                # Switch face order to normals face same direction
                self.faces[:, [1, 2]] = self.faces[:, [2, 1]]
                self.calcNorm()
                self.calcVNorm()
            else:
                raise ValueError("Expected axis to be within range 0-2 but found: {}".format(axis))
        else:
            raise TypeError("Expected axis to be int, but found: {}".format(type(axis)))
