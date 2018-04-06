# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 13:19:18 2017

@author: js22g12

Functions that deal with the visualisation of the limb and data
"""

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QWidget

class vtkRender(vtk.vtkRenderer):
    """
    Minor modification to the vtkRenderer class to allow easy access to 
    the currently displayed actors within each vtkRenderer object
    """

    def __init__(self):
        super(vtkRender, self).__init__()
        self.actors = []
        
class ampVTK(object):
    """
    Methods for display of the AmpObj within a vtk window
    """
    
    def __init__(self):
        self.rens = []
        self.cams = []
        self.axes = []
        self.scalar_bar = None
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.cams.append(vtk.vtkCamera())
        self.setView()
        self.rens.append(vtkRender())
        self.rens[0].SetBackground(0.1, 0.2, 0.4)
        self.rens[0].SetActiveCamera(self.cams[0])
        self.axes.append(vtk.vtkCubeAxesActor())
        
    def renderActors(self, actors, dispActors=['limb'], viewport=0, 
                     shading=True, zoom=1):
        """
        Render the required AmpObj actor in the vtk viewport
        """
        for actor in self.rens[viewport].actors:
            self.rens[viewport].RemoveActor(actors[actor])
        for actor in dispActors:
            actors[actor].setShading(shading)
            self.rens[viewport].AddActor(actors[actor])
        self.rens[viewport].actors = dispActors
        self.rens[viewport].ResetCamera()
        self.cams[viewport].Zoom(zoom)

    def setScalarBar(self, actor):
        """
        Set scalar bar based upon lookup table
        """
        if self.scalar_bar is not None:
            self.rens[0].RemoveActor(self.scalar_bar)
        self.scalar_bar = vtk.vtkScalarBarActor()
        self.scalar_bar.SetLookupTable(actor.lut)
        self.scalar_bar.SetOrientationToVertical()
        self.scalar_bar.SetPosition(0.85, 0.7)
        self.scalar_bar.SetPosition2(0.1, 0.3)
        self.rens[0].AddActor(self.scalar_bar)


            
    def setView(self, view = [0, -1, 0], viewport=0):
        self.cams[viewport].SetPosition(view[0], view[1], view[2])
        self.cams[viewport].SetViewUp(-0.0, 0.0, 1.0)
    
    def setBackground(self, color=[0.1, 0.2, 0.4]):
        for ren in self.rens:
            ren.SetBackground(color)
    
    def setProjection(self, perspective=False, viewport=0):
            self.cams[viewport].SetParallelProjection(perspective)
        
            
    def addAxes(self, actors, viewport=0, color = [1.0, 1.0, 1.0], font=None):
        lim = []
        for actor in actors:
            lim.append(actors[actor].GetBounds())
        lim = np.array(lim)
        self.axes[viewport].SetBounds(tuple(lim.max(axis=0)))
        self.axes[viewport].SetCamera(self.cams[viewport])
        self.axes[viewport].SetFlyModeToClosestTriad()
        for axes in range(3):
            self.axes[viewport].GetTitleTextProperty(axes).SetColor(color)
            self.axes[viewport].GetLabelTextProperty(axes).SetColor(color)
            self.axes[viewport].GetTitleTextProperty(axes).SetFontFamilyToCourier()
            self.axes[viewport].GetLabelTextProperty(axes).SetFontFamilyToCourier()
             
#        self.axes[viewport].GetXAxesLinesProperty().SetColor(color)
#        self.axes[viewport].GetYAxesLinesProperty().SetColor(color)
#        self.axes[viewport].GetZAxesLinesProperty().SetColor(color)
#
#        self.axes[viewport].SetGridLineLocation(self.axes[viewport].VTK_GRID_LINES_FURTHEST)
#        
#        self.axes[viewport].XAxisMinorTickVisibilityOff()
#        self.axes[viewport].YAxisMinorTickVisibilityOff()
#        self.axes[viewport].ZAxisMinorTickVisibilityOff()
#        self.rens[viewport].AddActor(self.axes[viewport])


class qtVtkWindow(QVTKRenderWindowInteractor, ampVTK):
    
    def __init__(self):
        super(qtVtkWindow, self).__init__()
        self.SetInteractorStyle(self.style)
        self.GetRenderWindow().AddRenderer(self.rens[0])
        self.iren = self.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        
    def setnumViewports(self, n):
        """
        Function to set multiple viewports within the vtkWindow

        Parameters
        ------------
        n: int
            number of viewports required
        """
        dif = n - len(self.rens)
        if dif == 0:
            return
        elif dif < 0:
            for ren in self.rens[n:]:
                self.GetRenderWindow().RemoveRenderer(ren)
            self.rens = self.rens[:n]
        elif dif > 0:
            for i in range(dif):
                self.rens.append(vtkRender())
                self.axes.append(vtk.vtkCubeAxesActor())
                self.GetRenderWindow().AddRenderer(self.rens[-1])
                if len(self.cams) < len(self.rens):
                    self.cams.append(vtk.vtkCamera())
                self.rens[-1].SetActiveCamera(self.cams[len(self.rens)-1])
        for i, ren in enumerate(self.rens):
            ren.SetViewport(float(i)/n, 0, float(i+1)/n, 1)
        self.setBackground()
        
        
class vtkRenWin(vtk.vtkRenderWindow, ampVTK):
    
    def __init__(self, winWidth=512, winHeight=512):
        super(vtkRenWin, self).__init__()
        self.winWidth = winWidth
        self.winHeight = winHeight
        self.SetSize(self.winWidth, self.winHeight)
        self.OffScreenRenderingOn()
        self.AddRenderer(self.rens[0])
        self.Render()

    def setnumViewports(self, n):
        """
        Function to set multiple viewports within the vtkWindow

        Parameters
        ------------
        n: int
            number of viewports required
        """
        dif = n - len(self.rens)
        if dif == 0:
            return
        elif dif < 0:
            for ren in self.rens[n:]:
                self.RemoveRenderer(ren)
            self.rens = self.rens[:n]
        elif dif > 0:
            for i in range(dif):
                self.rens.append(vtkRender())
                self.axes.append(vtk.vtkCubeAxesActor())
                self.AddRenderer(self.rens[-1])
                if len(self.cams) < len(self.rens):
                    self.cams.append(vtk.vtkCamera())
                self.rens[-1].SetActiveCamera(self.cams[len(self.rens)-1])
        for i, ren in enumerate(self.rens):
            ren.SetViewport(float(i)/n, 0, float(i+1)/n, 1)
        self.setBackground()
        
    
    def getImage(self):
        self.vtkRGB = vtk.vtkUnsignedCharArray()
        self.GetPixelData(0, 0, self.winWidth-1, self.winHeight-1,
                          1, self.vtkRGB)
        self.vtkRGB.Squeeze()
        self.im =  np.flipud(np.resize(np.array(self.vtkRGB),
                                       [self.winWidth, self.winHeight, 3])) / 255.0
                                       
    def getScreenshot(self, fname, mag=10):
        self.SetAlphaBitPlanes(1)
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self)
        w2if.SetScale(mag)
        w2if.SetInputBufferTypeToRGBA()
        w2if.Update()
        
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(fname)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()


class visMixin(object):

    def genIm(self, actor=['limb'], winWidth=512, winHeight=512,
              views=[[0, -1, 0]], background=[1.0, 1.0, 1.0], projection=True,
              shading=True, mag=10, out='im', name='test.tiff'):
        """
        
        """
        win = vtkRenWin(winWidth, winHeight)
        win.setnumViewports(len(views))
        win.setBackground(background)
        win.setProjection(projection)
        for i, view in enumerate(views):
            win.addAxes(self.actors, color=[0.0, 0.0, 0.0], viewport=i)
            win.setView(view, i)
            win.setProjection(projection, viewport=i)
            win.renderActors(self.actors, actor, viewport=i, shading=shading, zoom=1.3)
        win.Render()
        win.getImage()
        if out == 'im':
            return win.im
        elif out == 'fh':
            win.getScreenshot(name)
            return
#        win.getScreenshot('test.tiff')
#        return win.im

    def addActor(self, stype=0, CMap=None):
        """
        Function to insert a vtk actor into the actors dictionary within 
        the AmpObject 
        
        """
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        self.actors[stype] = self.ampActor(data, CMap=CMap)

    class ampActor(vtk.vtkActor):
        """
        Class that inherits methods from vtk actor
        Contains functions to set vertices, faces, scalars and color map
        from numpy arrays 
        
        Add functions to add vert, add faces, cmap and make LUT
        """

        def __init__(self, data, CMap=None, bands=None):
            self.mesh = vtk.vtkPolyData()
            self.points = vtk.vtkPoints()
            self.polys = vtk.vtkCellArray()
            self.setVert(data['vert'])
            self.setFaces(data['faces'])
            if CMap is not None:
                self.setRect(data['values'])
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
            
        def setFaces(self, faces):
            f = np.c_[np.tile(faces.shape[1], faces.shape[0]), faces].flatten().astype(np.int64)
            self.polys.SetCells(len(faces), 
                                numpy_support.numpy_to_vtkIdTypeArray(f, deep=1))
            self.mesh.SetPolys(self.polys)

        def setRect(self, rect):
            self.scalars = numpy_support.numpy_to_vtk(rect, deep=1)
            self.mesh.GetPointData().SetScalars(self.scalars)
            
        def setOpacity(self, opacity=1.0):
            self.GetProperty().SetOpacity(opacity)
            
        def setColor(self, color=[1.0, 1.0, 1.0]):
            self.GetProperty().SetColor(color)
            
        def setScalarRange(self, smin=-8.0, smax=8.0):
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
        
        def setShading(self, shading=True):
            if shading is True:
                self.GetProperty().LightingOn()
            if shading is False:
                self.GetProperty().LightingOff()

        
        