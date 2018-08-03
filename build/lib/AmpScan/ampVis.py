# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 13:19:18 2017

@author: js22g12

Functions that deal with the visualisation of the limb and data

Includes interfaces to deal 
"""

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class vtkRenWin(vtk.vtkRenderWindow):
    """
    Sample docstring to see what's what...
    """
    def __init__(self):
        super(vtkRenWin, self).__init__()
        self.rens = [vtk.vtkRenderer(),]
#        self.cams = [vtk.vtkCamera(),]
        self.axes = []
        self.AddRenderer(self.rens[0])
#        self.setView()
        self.scalar_bar = None
#        self.cams.append(vtk.vtkCamera())
#        self.setView()
#        self.rens.append(vtkRender())
#        self.rens[0].SetBackground(0.1, 0.2, 0.4)
#        self.rens[0].SetBackground(1.0,1.0,1.0)
        #self.rens[0].SetActiveCamera(self.cams[0])
#        self.axes.append(vtk.vtkCubeAxesActor())
        
    def renderActors(self, actors, viewport=0, 
                     shading=True, zoom=1):
        """
        Render the required AmpObj actor in the vtk viewport
        """
        for actor in self.rens[viewport].GetActors():
            self.rens[viewport].RemoveActor(actor)
        for actor in actors:
            actor.setShading(shading)
            self.rens[viewport].AddActor(actor)
        self.rens[viewport].ResetCamera()
        self.rens[viewport].GetActiveCamera().Zoom(zoom)

    def setScalarBar(self, actor, title=''):
        """
        Set scalar bar based upon lookup table
        """
        if self.scalar_bar is not None:
            self.rens[0].RemoveActor(self.scalar_bar)
        self.scalar_bar = vtk.vtkScalarBarActor()
#        self.scalar_bar.AnnotationTextScalingOff()
#        self.scalar_bar.SetTitle('Interfacial Pressure, kPa')
        self.scalar_bar.SetLookupTable(actor.lut)
        self.scalar_bar.UnconstrainedFontSizeOn()
        self.scalar_bar.SetOrientationToVertical()
        self.scalar_bar.SetPosition(0.8, 0.15)
        self.scalar_bar.SetPosition2(0.1, 0.7)
        self.scalar_bar.SetLabelFormat('%-#3.1f')
        self.scalar_bar.GetLabelTextProperty().SetFontFamilyToArial()
        self.scalar_bar.GetLabelTextProperty().BoldOff()
        self.scalar_bar.GetLabelTextProperty().ShadowOff()
        self.scalar_bar.GetLabelTextProperty().SetColor(0, 0, 0)
        self.scalar_bar.GetLabelTextProperty().SetFontSize(18)
        self.scalar_bar.GetLabelTextProperty().ItalicOff()
        self.scalar_bar.SetTitle(title)
        self.scalar_bar.GetTitleTextProperty().SetFontFamilyToArial()
        self.scalar_bar.GetTitleTextProperty().BoldOff()
        self.scalar_bar.GetTitleTextProperty().ShadowOff()
        self.scalar_bar.GetTitleTextProperty().SetColor(0, 0, 0)
        self.scalar_bar.GetTitleTextProperty().SetFontSize(20)
        self.scalar_bar.GetTitleTextProperty().ItalicOff()
        self.rens[0].AddActor(self.scalar_bar)

    def setView(self, view = [0, -1, 0], viewport=0):
        #self.cams[viewport].SetPosition(view[0], view[1], view[2])
        #self.cams[viewport].SetViewUp(-0.0, 1.0, 0.0)
        cam = self.rens[viewport].GetActiveCamera()
        cam.Elevation(-90)
    
    def setBackground(self, color=[0.1, 0.2, 0.4]):
        """
        Set the background colour of the renderer
        """
        for ren in self.rens:
            ren.SetBackground(color)
    
    def setProjection(self, perspective=False, viewport=0):
        """
        Set the projection of the camera to either parallel or perspective 
        
        """
        self.cams[viewport].SetParallelProjection(perspective)
        
            
    def addAxes(self, actors, viewport=0, color = [1.0, 1.0, 1.0], font=None):
        lim = []
        for actor in actors:
            lim.append(actor.GetBounds())
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
#        self.axes[viewport].SetGridLineLocation(self.axes[viewport].VTK_GRID_LINES_FURTHEST)
#        self.axes[viewport].XAxisMinorTickVisibilityOff()
#        self.axes[viewport].YAxisMinorTickVisibilityOff()
#        self.axes[viewport].ZAxisMinorTickVisibilityOff()
#        self.rens[viewport].AddActor(self.axes[viewport])


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
                self.rens.append(vtk.vtkRenderer())
                self.axes.append(vtk.vtkCubeAxesActor())
                self.AddRenderer(self.rens[-1])
                if len(self.cams) < len(self.rens):
                    self.cams.append(vtk.vtkCamera())
                self.rens[-1].SetActiveCamera(self.cams[len(self.rens)-1])
        for i, ren in enumerate(self.rens):
            ren.SetViewport(float(i)/n, 0, float(i+1)/n, 1)
        self.setBackground()
        
    
    def getImage(self):
        vtkRGB = vtk.vtkUnsignedCharArray()
        self.GetPixelData(0, 0, self.winWidth-1, self.winHeight-1,
                          1, vtkRGB)
        vtkRGB.Squeeze()
        self.im =  np.flipud(np.resize(np.array(vtkRGB),
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


class qtVtkWindow(QVTKRenderWindowInteractor):
    """
    Create a vtk window to be embeded within a qt GUI
    Inherites the QVTKRenderWindowInteractor class and the 
    
    Fix issue with SetInteractorStyle 
    """
    
    def __init__(self):
        super(qtVtkWindow, self).__init__(rw=vtkRenWin())
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(self.style)
        self.iren = self._RenderWindow.GetInteractor()
        self.iren.Initialize()        

class visMixin(object):
    """
    Visualisation methods that act upon the AmpObj itself
    Methods for generating the custom AmpObj actor to interface with vtk
    """

    def genIm(self, actor=['limb'], winWidth=512, winHeight=512,
              views=[[0, -1, 0]], background=[1.0, 1.0, 1.0], projection=True,
              shading=True, mag=10, out='im', name='test.tiff'):
        """
        Output an image of an actor either as an array or a saved png file
        
        
        """
        # Generate a renderer window
        win = vtkRenWin(False, winWidth, winHeight)
        # Set the number of viewports
        win.setnumViewports(len(views))
        # Set the background colour
        win.setBackground(background)
        # Set camera projection 
        win.setProjection(projection)
        win.SetSize(winWidth, winHeight)
        win.OffScreenRenderingOn()
        for i, view in enumerate(views):
            win.addAxes(self.actors, color=[0.0, 0.0, 0.0], viewport=i)
            win.setView(view, i)
            win.setProjection(projection, viewport=i)
            win.renderActors(self.actor, viewport=i, shading=shading, zoom=1.3)
        win.Render()
        if out == 'im':
            win.getImage()
            return win.im
        elif out == 'fh':
            win.getScreenshot(name)
            return
        
    def display(self):
        """
        Function to display the mesh in a vtk window
        """
        if not hasattr(self, 'actor'):
            self.addActor()
        # Generate a renderer window
        win = vtkRenWin()
        # Set the number of viewports
        win.setnumViewports(1)
        # Set the background colour
        win.setBackground([1,1,1])
        # Set camera projection 
        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(win)
        renderWindowInteractor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        # Set camera projection 
        win.setView()
        win.renderActors([self.actor,], shading=True)
        win.Render()
        win.rens[0].GetActiveCamera().Azimuth(180)
        win.rens[0].GetActiveCamera().SetParallelProjection(True)
        win.Render()
        return win


    def addActor(self, CMap=None, bands=128, sRange=[0,8]):
        """
        Function to insert a vtk actor into the actors dictionary within 
        the AmpObject 
        
        """
        self.actor = self.ampActor()
        #self._v = numpy_support.numpy_to_vtk(self.vert, deep=0)
        self.actor.setVert(self.vert)
        self.actor.setFaces(self.faces)
        #self.actor.setNorm()
        # Test if values array is non-zero
        if self.values.any():
            self.actor.setValues(self.values)
            self.actor.setCMap(CMap, bands)
            self.actor.setScalarRange(sRange)
            self.actor.Mapper.SetLookupTable(self.actor.lut)
        

    class ampActor(vtk.vtkActor):
        """
        Class that inherits methods from vtk actor
        Contains functions to set vertices, faces, scalars and color map
        from numpy arrays 
        """

        def __init__(self, CMap=None, bands=128):
            self.mesh = vtk.vtkPolyData()
            self.points = vtk.vtkPoints()
            self.polys = vtk.vtkCellArray()
            self.Mapper = vtk.vtkPolyDataMapper()
            #self.setVert(data['vert'])
            #self.setFaces(data['faces'])
            #self.setNorm()
            #if CMap is not None:
            #    self.setRect(data['values'])
            #    self.setCMap(CMap, bands)
            self.Mapper.InterpolateScalarsBeforeMappingOn()
            self.Mapper.SetInputData(self.mesh)
            #if CMap is not None:
            #    self.setScalarRange()
            #    self.Mapper.SetLookupTable(self.lut)
            self.SetMapper(self.Mapper)
            

        def setVert(self, vert, deep=0):
            self._v = numpy_support.numpy_to_vtk(vert, deep=deep)
            self.points.SetData(self._v)
#            self.points.SetData(vert)
            self.mesh.SetPoints(self.points)
            
        def setFaces(self, faces, deep=0):
            self._faces = np.c_[np.tile(faces.shape[1], faces.shape[0]),
                                faces].flatten().astype(np.int64)
            self._f = numpy_support.numpy_to_vtkIdTypeArray(self._faces, deep=deep)
            self.polys.SetCells(len(faces), self._f)
            self.mesh.SetPolys(self.polys)
        
        def setNorm(self, split=False, norm=None, deep=0):
            """
            Check if deepcopy is neededin this function
            """
            if norm is not None:
                self._n = numpy_support.numpy_to_vtk(norm, deep=deep)
                self.mesh.GetPointData().SetNormals(self._n)
            else:
                self.norm = vtk.vtkPolyDataNormals()
                self.norm.ComputePointNormalsOn()
                self.norm.ComputeCellNormalsOff()
                self.norm.SetFeatureAngle(30.0)
                self.norm.SetInputData(self.mesh)
                self.norm.Update()
                self.mesh.DeepCopy(self.norm.GetOutput())
            self.GetProperty().SetInterpolationToGouraud()

        def setValues(self, values, deep=0):
            self._values = numpy_support.numpy_to_vtk(values, deep=deep)
            self.mesh.GetPointData().SetScalars(self._values)
            
        def setOpacity(self, opacity=1.0):
            self.GetProperty().SetOpacity(opacity)
            
        def setColor(self, color=[1.0, 1.0, 1.0]):
            self.GetProperty().SetColor(color)
            
        def setScalarRange(self, sRange):
            self.Mapper.SetScalarRange(sRange[0], sRange[1])
            

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

        
        