# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 12:21:37 2017

@author: js22g12
"""

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class pressSense(object):

    def __init__(self):
        self.actors = {}
        self.antS = {}
        
    def importVert(self, fname, pos='ant'):
        self.antS['vert'] = np.loadtxt(fname, delimiter=',')
        self.antS['vert'][:, 1] += -1.0
    
    def importPress(self, fname):
        sF = self.antS['sF']
        val = np.loadtxt(fname, delimiter=',').flatten()
        self.antS['values']  = np.zeros(len(self.antS['faces']))
        self.antS['values'][sF] = val.flatten()[:, None]

    def calcVert(self, mesh, cLine, sensePos='ant', limbSide='L', d=3):
        """
        Function to compute vertex position of pressure sensors 
        
        Parameters
        ----------
        vert: numpy array
            vertices for mesh to project the pressure sensor onto
        CLine: numpy array
            vertices of the begining and end of the sensor centre line on the 
            socket 
        sensePos: str
            Aspect of socket the sensor was positioned
        limbSide: 
        """
        vert = mesh['vert']
        faces = mesh['faces']
        if sensePos == 'ant':
            plane = np.array([0, -1, 0])
        elif sensePos == 'lat' and limbSide == 'L':
            plane = np.array([1, 0, 0])
        elif sensePos == 'lat' and limbSide == 'R':
            plane = np.array([-1, 0, 0])
        rows, cols = [15*d + 1, 3*d + 1]
        planeInd = [i for i, p in enumerate(plane) if p == 0]
        lim = cLine[:, planeInd]
        h = np.linspace(0, lim[1, 0]- lim[0, 0], 100)
        v = np.linspace(0, lim[1, 1]- lim[0, 1], 100)
        # Define co-ordinate transformation to translate to bottom 
        # of sensor and rotate around y axis
        trans = np.zeros([4,4])
        trans[planeInd, 3] = lim[0, :]
        xTheta = -np.arctan((lim[0, 0] - lim[1, 0])/(lim[0, 1] - lim[1, 1]))
        trans = np.identity(4) - trans
        # rotation matrix 
        R = np.array([[np.cos(xTheta), 0, np.sin(xTheta),0],
                       [0, 1, 0, 0],
                       [-np.sin(xTheta), 0, np.cos(xTheta), 0],
                       [0, 0, 0, 1]])
        M = np.dot(R, trans)
        # Apply transformation 
        vertT = np.dot(M, np.transpose(np.c_[vert, np.ones(len(vert))]))
        vertT = np.transpose(vertT[:-1, :])
        # get faceCentroids )
        # Equation of line 
        # Find nearest 10 centroids to line 
        # Test if line intersects faces using barycentric technique 
        # Intersection between line and face plane
    
    def calcFaces(self, d=5):
        """
        Function to compute face array for pressure sensor 
        
        FIX SO USE QUAD FACES
        """
        # define no of rows and columns in sensors
        rows, cols = [15*d, 3*d]
        # Create face array
        f = np.zeros([rows*cols*2, 3], dtype=np.int64)
        # Create array to mapy from sensor data to face colour
        sF = np.zeros([45, 2*d**2], dtype=np.int64)
        # Define face 
        f0 = np.array([[0, cols+1, 1],
                       [1, cols+1, cols+2]])
        for row in range(rows):
            for col in range(cols):
                ind = row*cols*2 + col*2
                ind2 = row*(cols+1) + col
                f[[ind, ind+1], :] = f0 + ind2
        ind = np.arange(0, cols*2*d, cols*2)[:, None]
        for row in range(15):
            inds = np.array([np.arange(2*d) + d*row*cols*2]*d)
            inds += np.arange(0, cols*2*d, cols*2)[:, None]
            for col in range(3):
                sF[row*3 + col, :] = inds.flatten()
                inds += 2*d
        self.antS['faces'] = f
        self.antS['sF'] = sF
        
    def calcFacesHex(self, d=5):
        """
        Function to compute face array for pressure sensor 
        
        FIX SO USE QUAD FACES
        """
        # define no of rows and columns in sensors
        rows, cols = [15*d, 3*d]
        # Create face array
        f = np.zeros([rows*cols*2, 3], dtype=np.int64)
        # Create array to mapy from sensor data to face colour
        sF = np.zeros([45, 2*d**2], dtype=np.int64)
        f0 = np.array([[0, cols+1, 1],
                       [1, cols+1, 2]])
        for row in range(rows):
            for col in range(cols):
                ind = row*cols*2 + col*2
                ind2 = row*(cols+1) + col
                f[[ind, ind+1], :] = f0 + ind2
        ind = np.arange(0, cols*2*d, cols*2)[:, None]
        for row in range(15):
            inds = np.array([np.arange(2*d) + d*row*cols*2]*d)
            inds += np.arange(0, cols*2*d, cols*2)[:, None]
            for col in range(3):
                sF[row*3 + col, :] = inds.flatten()
                inds += 2*d
        self.antS['faces'] = f
        self.antS['sF'] = sF
    
    def intersectLineMesh(line, v, f):
        """
        Function to calculate intersection between line and mesh 
        """
        
    def addActor(self, pos ='antS', CMap=None, connect=3):
        """
        Function to insert a vtk actor into the actors dictionary within 
        the AmpObject 
        
        """
        self.actors[pos] = self.pressActor(self.antS, CMap=CMap, connect=connect)

    class pressActor(vtk.vtkActor):
        """
        Class that inherits methods from vtk actor
        Contains functions to set vertices, faces, scalars and color map
        from numpy arrays 
        
        Add functions to add vert, add faces, cmap and make LUT
        """

        def __init__(self, data, CMap=None, bands=None, connect=3):
            self.mesh = vtk.vtkPolyData()
            self.points = vtk.vtkPoints()
            self.polys = vtk.vtkCellArray()
            self.setVert(data['vert'])
            self.setFaces(data['faces'], connect)
            if CMap is not None:
                self.setPress(data['values'])
                self.setCMap(CMap)
            self.Mapper = vtk.vtkPolyDataMapper()
            self.Mapper.SetInputData(self.mesh)
            if CMap is not None:
                self.setScalarRange()
                self.Mapper.SetLookupTable(self.lut)
            self.SetMapper(self.Mapper)

        def setVert(self, vert):
            self.points.SetData(numpy_support.numpy_to_vtk(vert, deep=1))
            self.mesh.SetPoints(self.points)
            
        def setFaces(self, faces, connect=3):
            f = np.c_[np.tile(connect, len(faces)), faces].flatten()
            self.polys.SetCells(len(faces), 
                                numpy_support.numpy_to_vtkIdTypeArray(f, deep=1))
            self.mesh.SetPolys(self.polys)

        def setPress(self, press):
            self.scalars = numpy_support.numpy_to_vtk(press, deep=1)
            self.mesh.GetCellData().SetScalars(self.scalars)
            
        def setScalarRange(self, smin=0.0, smax=100.0):
            self.Mapper.SetScalarRange(smin, smax)
            

        def setCMap(self, CMap, bands=128):
            self.ctf = vtk.vtkColorTransferFunction()
            self.ctf.SetColorSpaceToDiverging()
            for ind, point in zip(np.linspace(0, 1, len(CMap)), CMap):
                self.ctf.AddRGBPoint(ind, point[0], point[1], point[2])
            self.lut = vtk.vtkLookupTable()
            self.lut.SetNumberOfTableValues(bands)
            self.lut.Build()
            for i in range(bands):
                rgb = list(self.ctf.GetColor(float(i) / bands)) + [1]
                self.lut.SetTableValue(i, rgb)



def func1():
    path = r'J:\Shared Resources\AmpScan IfLS Team\101 ImpAmp\Upgrade'
    sockets = ['B_PTB.stl', 'B_TSB.stl', 'B_KBM.stl']
    pressure = ['161108_Sub02_T001', '161108_Sub02_T002', '161108_Sub02_T006']
    files = ['B_PTB_LOC', 'B_TSB_LOC', 'B_KBM_LOC']
    
    LimbSide = 'L'
    d = 5
    i = 1
    
    socket = path + '\\' + sockets[0]
    
    Data = AmpObject(socket, 'limb')
    vert = Data.limb['vert']
    posData = np.genfromtxt(path + '\\' + files[0] + '.csv', 
                            delimiter=',', skip_header=1)[:, 1::]
    antData = np.loadtxt(path + '\\' + pressure[0] + '_ant.csv', delimiter = ',')
    latData = np.loadtxt(path + '\\' + pressure[0] + '_lat.csv', delimiter = ',')
    cLine = posData[[0,1], :]
    
def func2():
    CMap = np.array([[212.0, 221.0, 225.0],
                     [31.0, 73.0, 125.0]])/255.0
    vfname = (r'C:\Users\js22g12\OneDrive - University of Southampton'
              r'\Documents (OneDrive)\AmpScan\Code\2017_09'
              r'\02_Code\AmpScan\PTB_AntVert.csv')
    pfname = (r'J:\Shared Resources\AmpScan IfLS Team\101 ImpAmp\Upgrade'
              r'\161108_Sub02_T001_ant.csv')
    pressData = pressSense()
    pressData.calcFaces(d=5)
    pressData.importVert(vfname)
    pressData.importPress(pfname)
    pressData.addActor(CMap=CMap)
