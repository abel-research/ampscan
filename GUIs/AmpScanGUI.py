import sys
import numpy as np
from vtk.util import numpy_support
from AmpScan import AmpObject
from AmpScan.registration import registration
from AmpScan.ampVis import qtVtkWindow
from AmpScan.pressSens import pressSense
from PyQt5.QtCore import QPoint, QSize, Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import (QColor, QFontMetrics, QImage, QPainter, QIcon,
                         QOpenGLVersionProfile)
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout,
                             QMainWindow, QMessageBox, QComboBox,
                             QOpenGLWidget, QFileDialog,QLabel,QPushButton,
                             QSlider, QWidget, QTableWidget, QTableWidgetItem)

        
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
        self.files = {}
        self.filesDrop = list(self.files.keys())
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
        self.fileManager = fileManager(self)
        self.fileManager.show()
        self.fileManager.table.itemChanged.connect(self.display)
        
    def chooseOpenFile(self):
        """
        Handles importing of stls into the GUI.
        
        More writing...

        Note
        ----

        @Josh_Steer if no stl is selected then the window crashes!

        """
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Meshes (*.stl)")
        if fname[0] == '':
            return
        name = fname[0][:-4].split('/')[-1]
        self.files[name] = AmpObject(fname[0], 'limb')
        amp = self.files[name]
        amp.addActor()
        self.fileManager.addRow(name, amp)
        self.display()
        self.filesDrop.append(name)
        if hasattr(self, 'alCont'):
            self.alCont.getNames()
        if hasattr(self, 'regCont'):
            self.regCont.getNames()
#        self.AmpObj.lp_smooth()
        
    def display(self):
        render = []
        for r in range(self.fileManager.n):
            [name, _, color, opacity, display] = self.fileManager.getRow(r)
            if display == 2:
                render.append(self.files[name].actor)
            color = color[1:-1].split(',')
            color = [float(c) for c in color]
            self.files[name].actor.setColor(color)
            self.files[name].actor.setOpacity(float(opacity))
            self.renWin.renderActors(render)
        
        
    def align(self):
        """
        Numpy style docstring.

        """
        self.alCont = AlignControls(self.filesDrop, self)
        self.alCont.show()
        self.alCont.icp.clicked.connect(self.runICP)
#        self.renWin.setnumViewports(2)
#        self.renWin.setView(view=[-1, 0, 0], viewport=1)
#        self.renWin.setProjection(True, 0)
#        self.renWin.setProjection(True, 1)
##        self.renWin.render(self.AmpObj.actors, dispActors=['limb',])
##        self.renWin.render(self.AmpObj.actors, dispActors=['socket',],
##                              viewport=1)
#        self.renWin.renderActors([self.AmpObj.actor, self.socket.actor],
#                                 viewport=0)
#        self.renWin.renderActors([self.AmpObj.actor, self.socket.actor],
#                                 viewport=1)
#        self.AmpObj.actor.setColor([1.0, 0.0, 0.0])
#        self.AmpObj.actor.setOpacity(0.5)
#        self.socket.actor.setColor([0.0, 0.0, 1.0])
#        self.socket.actor.setOpacity(0.5)
    
    def runICP(self):
        static = str(self.alCont.static.currentText())
        moving = str(self.alCont.moving.currentText())
        print('Run the ICP code between %s and %s' % (static, moving))

    def runRegistration(self):
        baseline = str(self.regCont.baseline.currentText())
        target = str(self.regCont.target.currentText())
        print('Run the Registration code between %s and %s' % (baseline, target))
        
    def register(self):
        """
        Numpy style docstring.

        """
        self.regCont = RegistrationControls(self.filesDrop, self)
        self.regCont.show()
        self.regCont.reg.clicked.connect(self.runRegistration)
        
#        self.renWin.setnumViewports(1)
#        self.renWin.setProjection()
#        self.RegObj = registration(self.socket, self.AmpObj)
#        self.RegObj.addActor(CMap=self.AmpObj.CMapN2P)
#        self.renWin.renderActors([self.RegObj.actor,])
#        self.renWin.setScalarBar(self.RegObj.actor)
    
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
        
class fileManager(QMainWindow):
    """
    Controls to manage the displayed 
    
    Example
    -------
    Perhaps an example implementation:

    >>> from AmpScan.AmpScanGUI import AmpScanGUI

    """

    def __init__(self, parent = None):
        super(fileManager, self).__init__(parent)
        self.main = QWidget()
        self.table = QTableWidget()
        self.setCentralWidget(self.main)
        self.layout = QGridLayout()
        self.layout.addWidget(self.table, 0, 0)
        self.main.setLayout(self.layout)
        self.setWindowTitle("AmpObject Manager")
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Name', 'Type', 'Colour', 'Opacity', 'Display'])
        self.n = self.table.rowCount()
        
    def addRow(self, name, amp):
        self.table.insertRow(self.n)
        self.table.setItem(self.n, 0, QTableWidgetItem(name))
        self.table.setItem(self.n, 1, QTableWidgetItem(amp.stype))
        self.table.setItem(self.n, 2, QTableWidgetItem(str(amp.actor.GetProperty().GetColor())))
        self.table.setItem(self.n, 3, QTableWidgetItem(str(amp.actor.GetProperty().GetOpacity())))
        chkBoxItem = QTableWidgetItem()
        chkBoxItem.setTextAlignment(Qt.AlignCenter)
        chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        chkBoxItem.setCheckState(Qt.Checked)       
        
        self.table.setItem(self.n,4,chkBoxItem)
        self.n = self.table.rowCount()
        
    def getRow(self, i):
        row = []
        for r in range(self.table.columnCount() - 1):
            row.append(self.table.item(i, r).text())
        row.append(self.table.item(i, r+1).checkState())
        return row 

class AlignControls(QMainWindow):
    """
    Pop up for controls to align the 
    
    Example
    -------
    Perhaps an example implementation:

    >>> from AmpScan.AmpScanGUI import AmpScanGUI

    """

    def __init__(self, names, parent = None):
        super(AlignControls, self).__init__(parent)
        self.main = QWidget()
        self.names = names
        self.static = QComboBox()
        self.moving = QComboBox()
        self.icp = QPushButton("Run ICP")
        self.setCentralWidget(self.main)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Static'), 0, 0)
        self.layout.addWidget(QLabel('Moving'), 1, 0)
        self.layout.addWidget(self.static, 0, 1)
        self.layout.addWidget(self.moving, 1, 1)
        self.layout.addWidget(self.icp, 2, 0, 1, -1)
        self.main.setLayout(self.layout)
        self.setWindowTitle("Alignment Manager")
        self.getNames()
    
    def getNames(self):
        """
        """
        self.static.clear()
        self.static.addItems(self.names)
        self.moving.clear()
        self.moving.addItems(self.names)
           
        
class RegistrationControls(QMainWindow):
    """
    Pop up for controls to align the 
    
    Example
    -------
    Perhaps an example implementation:

    >>> from AmpScan.AmpScanGUI import AmpScanGUI

    """

    def __init__(self, names, parent = None):
        super(RegistrationControls, self).__init__(parent)
        self.main = QWidget()
        self.names = names
        self.baseline = QComboBox()
        self.target = QComboBox()
        self.reg = QPushButton("Run Registration")
        self.setCentralWidget(self.main)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Baseline'), 0, 0)
        self.layout.addWidget(QLabel('Target'), 1, 0)
        self.layout.addWidget(self.baseline, 0, 1)
        self.layout.addWidget(self.target, 1, 1)
        self.layout.addWidget(self.reg, 2, 0, 1, -1)
        self.main.setLayout(self.layout)
        self.setWindowTitle("Alignment Manager")
        self.getNames()
    
    def getNames(self):
        """
        """
        self.baseline.clear()
        self.baseline.addItems(self.names)
        self.target.clear()
        self.target.addItems(self.names)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = AmpScanGUI()
    mainWin.show()
    sys.exit(app.exec_())