import AmpScan
import sys
import numpy as np
from vtk.util import numpy_support
from AmpScan.core import AmpObject
from AmpScan.registration import registration
from AmpScan.ampVis import qtVtkWindow
from AmpScan.pressSens import pressSense
from PyQt5.QtCore import QPoint, QSize, Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import (QColor, QFontMetrics, QImage, QPainter, QIcon,
                         QOpenGLVersionProfile)
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout,
                             QMainWindow, QMessageBox,
                             QOpenGLWidget, QFileDialog,
                             QSlider, QWidget)

        
class AmpScanGUI(QMainWindow):
    """
    Generates an GUI for handling stl data. Window is derived from QT.
    
    More detailed description...
    
    Example
    -------
    Perhaps an example implementation:

    >>> from AmpScan.AmpScanGUI import AmpScanGUI

    """

    def __init__(self, parent = None):
        super(AmpScanGUI, self).__init__()
        self.vtkWidget = qtVtkWindow()
        self.renWin = self.vtkWidget._RenderWindow
        self.renWin.setBackground()
        self.mainWidget = QWidget()
        self.AmpObj = None
#        self.CMap = np.array([[212.0, 221.0, 225.0],
#                              [31.0, 73.0, 125.0]])/255.0
        self.setCentralWidget(self.mainWidget)
        self.createActions()
        self.createMenus()
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.vtkWidget, 0, 0)
        self.mainWidget.setLayout(self.Layout)
        self.setWindowTitle("AmpScan Visualiser")
        self.resize(800, 800)
        self.show()
        
    def chooseOpenFile(self):
        """
        Handles importing of stls into the GUI.
        
        More writing...

        Note
        ----

        @Josh_Steer if no stl is selected then the window crashes!

        """
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Meshes (*.stl)")
        if self.AmpObj is not None:
            self.renWin.renderActors([self.AmpObj.actor,])
        self.AmpObj = AmpObject(self.fname[0], 'limb')
        self.AmpObj.addActor()
#        self.AmpObj.lp_smooth()
        self.renWin.setnumViewports(1)
        self.renWin.setProjection()
        self.renWin.renderActors([self.AmpObj.actor,])
        
    def chooseSocket(self):
        """
        Button in GUI.

        """
        self.sockfname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Meshes (*.stl)")
        self.socket = AmpObject(self.sockfname[0], stype='socket')
        self.socket.addActor()
        self.socket.lp_smooth()
        
    def align(self):
        """
        Numpy style docstring.

        """
        self.renWin.setnumViewports(2)
        self.renWin.setView(view=[-1, 0, 0], viewport=1)
        self.renWin.setProjection(True, 0)
        self.renWin.setProjection(True, 1)
#        self.renWin.render(self.AmpObj.actors, dispActors=['limb',])
#        self.renWin.render(self.AmpObj.actors, dispActors=['socket',],
#                              viewport=1)
        self.renWin.renderActors([self.AmpObj.actor, self.socket.actor],
                                 viewport=0)
        self.renWin.renderActors([self.AmpObj.actor, self.socket.actor],
                                 viewport=1)
        self.AmpObj.actor.setColor([1.0, 0.0, 0.0])
        self.AmpObj.actor.setOpacity(0.5)
        self.socket.actor.setColor([0.0, 0.0, 1.0])
        self.socket.actor.setOpacity(0.5)
        
    def register(self):
        """
        Numpy style docstring.

        """
        
        self.renWin.setnumViewports(1)
        self.renWin.setProjection()
        self.RegObj = registration(self.socket, self.AmpObj)
        self.RegObj.addActor(CMap=self.AmpObj.CMapN2P)
        self.renWin.renderActors([self.RegObj.actor,])
        self.renWin.setScalarBar(self.RegObj.actor)
    
    def analyse(self):
        """
        Numpy style docstring.

        """

        #self.RegObj.plot_slices()
        self.AmpObj.vert[:, 0] *= 2
        self.AmpObj.actor.points.Modified()
        #self.renWin.renderActors([self.AmpObj.actor,])
        #self.AmpObj.vert[0,0] = 1
        #self.AmpObj._v = numpy_support.numpy_to_vtk(self.AmpObj.vert)

    def chooseFE(self):
        """
        Numpy style docstring.

        """
        FEname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="FE results (*.npy)")
        self.renWin.setnumViewports(1)
        self.FE = AmpObject([FEname[0],], stype='FE')
        self.AmpObj.lp_smooth()
        self.AmpObj.addActor(CMap=self.AmpObj.CMap02P, bands=5)
        self.AmpObj.actor.setScalarRange(smin=0.0, smax=50)
        self.renWin.renderActors(self.FE.actor, shading=True)
        self.renWin.setScalarBar(self.FE.actor)
        
    def choosePress(self):
        """
        Numpy style docstring.

        """
        vName = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Sensor vertices (*.csv)")
        pName = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Sensor pressures (*.csv)")
        self.renWin.setnumViewports(1)
        self.pSense = pressSense()
        self.pSense.calcFaces(d=5)
        self.pSense.importVert(vName[0])
        self.pSense.importPress(pName[0])
        self.pSense.addActor(CMap=self.AmpObj.CMap02P)
        self.AmpObj.actors['antS'] = self.pSense.actors['antS']
        self.AmpObj.actors['socket'].setColor([1.0, 1.0, 1.0])
        self.AmpObj.actors['socket'].setOpacity(1.0)
        self.renWin.renderActors(self.AmpObj.actors, ['socket', 'antS'])
        self.renWin.setScalarBar(self.AmpObj.actors['antS'])
        
    def createActions(self):
        """
        Numpy style docstring.

        """
        self.openFile = QAction(QIcon('open.png'), 'Open', self,
                                shortcut='Ctrl+O',
                                triggered=self.chooseOpenFile)
        self.openSocket = QAction(QIcon('open.png'), 'Open Socket', self,
                                triggered=self.chooseSocket)
        self.openFE = QAction(QIcon('open.png'), 'Open FE', self,
                                triggered=self.chooseFE)
        self.openPress = QAction(QIcon('open.png'), 'Open Press', self,
                                triggered=self.choosePress)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                               triggered=self.close)
        self.align = QAction(QIcon('open.png'), 'Align', self,
                                triggered=self.align)
        self.rect = QAction(QIcon('open.png'), 'Register', self,
                                triggered=self.register)
        self.analyse = QAction(QIcon('open.png'), 'Analyse', self,
                                triggered=self.analyse)

    def createMenus(self):
        """
        Numpy style docstring.

        """
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openFile)
        self.fileMenu.addAction(self.openSocket)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.alignMenu = self.menuBar().addMenu("&Align")
        self.alignMenu.addAction(self.align)
        self.regMenu = self.menuBar().addMenu("&Registration")
        self.regMenu.addAction(self.rect)
        self.feMenu = self.menuBar().addMenu("&FE Analysis")
        self.feMenu.addAction(self.openFE)
        self.analyseMenu = self.menuBar().addMenu("&Analyse")
        self.analyseMenu.addAction(self.analyse)
        self.kineticMenu = self.menuBar().addMenu("&Kinetic Measurements")
        self.kineticMenu.addAction(self.openPress)
           
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = AmpScanGUI()
    mainWin.show()
    sys.exit(app.exec_())