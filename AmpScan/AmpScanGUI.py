import sys
import numpy as np
from core import AmpObject
from registration import regObject
from ampVis import qtVtkWindow
from pressSens import pressSense
from PyQt5.QtCore import QPoint, QSize, Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import (QColor, QFontMetrics, QImage, QPainter, QIcon,
                         QOpenGLVersionProfile)
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout,
                             QMainWindow, QMessageBox,
                             QOpenGLWidget, QFileDialog,
                             QSlider, QWidget)

        
class AmpScanGUI(QMainWindow):

    def __init__(self, parent = None):
        super(AmpScanGUI, self).__init__()
        self.vtkWidget = qtVtkWindow()
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
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Meshes (*.stl)")
        if self.AmpObj is not None:
            self.vtkWidget.renderActors(self.AmpObj.actors, [])
        self.AmpObj = AmpObject(self.fname[0], 'limb')
        self.AmpObj.addActor(stype='limb')
        self.AmpObj.lp_smooth(stype='limb')
        self.vtkWidget.setnumViewports(1)
        self.vtkWidget.setProjection()
        self.vtkWidget.renderActors(self.AmpObj.actors, ['limb',])
        
    def chooseSocket(self):
        self.sockfname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Meshes (*.stl)")
        self.AmpObj.addData(self.sockfname[0], stype='socket')
        self.AmpObj.addActor(stype='socket')
        self.AmpObj.lp_smooth(stype='socket')
        
    def align(self):
        self.vtkWidget.setnumViewports(2)
        self.vtkWidget.setView(view=[-1, 0, 0], viewport=1)
        self.vtkWidget.setProjection(True, 0)
        self.vtkWidget.setProjection(True, 1)
#        self.vtkWidget.render(self.AmpObj.actors, dispActors=['limb',])
#        self.vtkWidget.render(self.AmpObj.actors, dispActors=['socket',],
#                              viewport=1)
        self.vtkWidget.renderActors(self.AmpObj.actors,
                              dispActors=['limb', 'socket'],
                              viewport=0)
        self.vtkWidget.renderActors(self.AmpObj.actors,
                              dispActors=['limb', 'socket'],
                              viewport=1)
        self.AmpObj.actors['limb'].setColor([1.0, 0.0, 0.0])
        self.AmpObj.actors['limb'].setOpacity(0.5)
        self.AmpObj.actors['socket'].setColor([0.0, 0.0, 1.0])
        self.AmpObj.actors['socket'].setOpacity(0.5)
        
    def register(self):
        self.vtkWidget.setnumViewports(1)
        self.vtkWidget.setProjection()
        self.RegObj = regObject(self.AmpObj)
        self.RegObj.registration(steps=5, baseline='socket', target='limb', 
                                 reg = 'reglimb', direct=True)
        self.RegObj.addActor(stype='reglimb', CMap=self.AmpObj.CMapN2P)
        self.vtkWidget.renderActors(self.AmpObj.actors, ['reglimb',], shading=False)
        self.vtkWidget.setScalarBar(self.AmpObj.actors['reglimb'])
    
    def analyse(self):
        self.RegObj.plot_slices()

    def chooseFE(self):
        FEname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="FE results (*.npy)")
        self.vtkWidget.setnumViewports(1)
        self.AmpObj.addFE([FEname[0],])
        self.AmpObj.lp_smooth('FE', n=1)
        self.AmpObj.addActor(stype='FE', CMap=self.AmpObj.CMap02P, bands=5)
        self.AmpObj.actors['FE'].setScalarRange(smin=0.0, smax=50)
        self.vtkWidget.renderActors(self.AmpObj.actors, ['FE',])
        self.vtkWidget.setScalarBar(self.AmpObj.actors['FE'])
        
    def choosePress(self):
        vName = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Sensor vertices (*.csv)")
        pName = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Sensor pressures (*.csv)")
        self.vtkWidget.setnumViewports(1)
        self.pSense = pressSense()
        self.pSense.calcFaces(d=5)
        self.pSense.importVert(vName[0])
        self.pSense.importPress(pName[0])
        self.pSense.addActor(CMap=self.AmpObj.CMap02P)
        self.AmpObj.actors['antS'] = self.pSense.actors['antS']
        self.AmpObj.actors['socket'].setColor([1.0, 1.0, 1.0])
        self.AmpObj.actors['socket'].setOpacity(1.0)
        self.vtkWidget.renderActors(self.AmpObj.actors, ['socket', 'antS'])
        self.vtkWidget.setScalarBar(self.AmpObj.actors['antS'])
        
    def createActions(self):
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