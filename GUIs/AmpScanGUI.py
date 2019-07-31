import sys
import numpy as np
import vtk
from AmpScan import AmpObject
from AmpScan.registration import registration
from AmpScan.align import align
from AmpScan.ampVis import qtVtkWindow, vtkRenWin
from PyQt5.QtCore import QPoint, QSize, Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import (QColor, QFontMetrics, QImage, QPainter, QIcon,
                         QOpenGLVersionProfile)
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout, QHBoxLayout,
                             QMainWindow, QMessageBox, QComboBox, QButtonGroup,
                             QOpenGLWidget, QFileDialog, QLabel, QPushButton,
                             QSlider, QWidget, QTableWidget, QTableWidgetItem,
                             QAbstractButton, QCheckBox, QErrorMessage)

        
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
        self.renWin.setBackground([1,1,1])
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
        self.pnt = None
        
    def chooseOpenFile(self):
        """
        Handles importing of stls into the GUI.
        
        More writing...


        """
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Meshes (*.stl)")
        if fname[0] == '':
            return
        name = fname[0][:-4].split('/')[-1]
        self.files[name] = AmpObject(fname[0], 'limb')
        amp = self.files[name]
        amp.addActor()
        amp.tform = vtk.vtkTransform()
        amp.tform.PostMultiply()
        amp.actor.SetUserTransform(amp.tform)
#        amp.centre()
        self.fileManager.addRow(name, amp)
        self.display()
        self.filesDrop.append(name)
        if hasattr(self, 'alCont'):
            self.alCont.getNames()
        if hasattr(self, 'regCont'):
            self.regCont.getNames()
#        self.AmpObj.lp_smooth()
        
    def chooseSaveFile(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file',
                                            filter="Meshes (*.stl)")
        if fname[0] == '':
            return
        moving = str(self.alCont.moving.currentText())
        self.files[moving].save(fname[0])
        try:
            f = open(fname[0]+'.txt','w+')
            f.write('{}'.format(self.pnt))
        except AttributeError:
            print('A point has not been selected')

    
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
        if self.objectsReady(1):
            self.alCont = AlignControls(self.filesDrop, self)
            self.alCont.show()
            self.alCont.centre.clicked.connect(self.centreMesh)
            self.alCont.icp.clicked.connect(self.runICP)
            self.alCont.xrotButton.buttonClicked[QAbstractButton].connect(self.rotatex)
            self.alCont.yrotButton.buttonClicked[QAbstractButton].connect(self.rotatey)
            self.alCont.zrotButton.buttonClicked[QAbstractButton].connect(self.rotatez)
            self.alCont.xtraButton.buttonClicked[QAbstractButton].connect(self.transx)
            self.alCont.ytraButton.buttonClicked[QAbstractButton].connect(self.transy)
            self.alCont.ztraButton.buttonClicked[QAbstractButton].connect(self.transz)
        else:
            show_message("Must be at least 1 object loaded to run align")
    
    def Point_Pick(self):
        """
        Waits for a point click to occur before calling further functions
        TODO: Create 'Picker controls'? Similar to Alignment controls, but where
        user can enter the name of the point they select - this can allow
        multiple landmark locations to be stored and marked?
        """
        self.vtkWidget.iren.AddObserver('RightButtonPressEvent', self.pick_loc)
        self.renWin.Render()
    
    def pick_loc(self, event, x):
        """
        calcs the location of click in GUI (x,y)
        calls function in ampVis.py which converts from GUI coordinates to
        mesh coordinates and marks the point
        """
        #print(event, x)
        self.vtkWidget.iren.RemoveObservers('RightButtonPressEvent')
        loc = event.GetEventPosition()
        self.pnt = vtkRenWin.Pick_point(self.renWin, loc)
        #vtkRenWin.mark(self.renWin,self.pnt[0],self.pnt[1],self.pnt[2])
        print(self.pnt)
    
    def removePick(self):
        """
        delete all marked points and labels
        TODO: be able to delete individual points?
        """
        self.pnt = None
        vtkRenWin.delMarker(self.renWin)
        
    def rotatex(self, button):
        moving = str(self.alCont.moving.currentText())
        ang = float(button.text())
        idx = [1, 0, 0]
        self.files[moving].rotateAng([ang*i for i in idx], 'deg')
        self.files[moving].tform.RotateX(ang)
        self.renWin.Render()
#        print('rotate x by %.1f' % ang)

    def rotatey(self, button):
        moving = str(self.alCont.moving.currentText())
        ang = float(button.text())
        idx = [0, 1, 0]
        self.files[moving].rotateAng([ang*i for i in idx], 'deg')
        self.files[moving].tform.RotateY(ang)
        self.renWin.Render()
#        print('rotate y by %.1f' % ang)

    def rotatez(self, button):
        moving = str(self.alCont.moving.currentText())
        ang = float(button.text())
        idx = [0, 0, 1]
        self.files[moving].rotateAng([ang*i for i in idx], 'deg')
        self.files[moving].tform.RotateZ(ang)
        self.renWin.Render()

    def transx(self, button):
        moving = str(self.alCont.moving.currentText())
        t = [float(button.text()),0, 0]
        self.files[moving].translate(t)
        self.files[moving].tform.Translate(t)
        self.renWin.Render()
#        print('rotate x by %.1f' % ang)

    def transy(self, button):
        moving = str(self.alCont.moving.currentText())
        t = [0, float(button.text()), 0]
        self.files[moving].translate(t)
        self.files[moving].tform.Translate(t)
        self.renWin.Render()
#        print('rotate y by %.1f' % ang)

    def transz(self, button):
        moving = str(self.alCont.moving.currentText())
        t = [0, 0, float(button.text())]
        self.files[moving].translate(t)
        self.files[moving].tform.Translate(t)
        self.renWin.Render()
#        print('rotate z by %.1f' % ang)
#        self.files[moving].rotateAng(ang, 'deg')

    def centreMesh(self):
        moving = str(self.alCont.moving.currentText())
        c = -1 * self.files[moving].vert.mean(axis=0)
        t = c.tolist()
        self.files[moving].centre()
        self.files[moving].tform.Translate(t)
        self.renWin.Render()
    
    def runICP(self):
        if self.objectsReady(1):
            static = str(self.alCont.static.currentText())
            moving = str(self.alCont.moving.currentText())
            al = align(self.files[moving], self.files[static],
                       maxiter=10, method='linPoint2Plane').m
            al.tform = vtk.vtkTransform()
            al.tform.PostMultiply()
            al.addActor()
            al.actor.SetUserTransform(al.tform)
            alName = moving + '_al'
            self.files[alName] = al
            self.filesDrop.append(alName)
            self.fileManager.addRow(alName, self.files[alName])
            self.fileManager.setTable(static, [1,0,0], 0.5, 2)
            self.fileManager.setTable(moving, [1,1,1], 1, 0)
            self.fileManager.setTable(alName, [0,0,1], 0.5, 2)
            if hasattr(self, 'alCont'):
                self.alCont.getNames()
            if hasattr(self, 'regCont'):
                self.regCont.getNames()
        else:
            show_message("Must be at least 2 objects loaded to run ICP")

    def runRegistration(self):
        if self.objectsReady(2):
            c1 = [31.0, 73.0, 125.0]
            c3 = [170.0, 75.0, 65.0]
            c2 = [212.0, 221.0, 225.0]
            CMap1 = np.c_[[np.linspace(st, en) for (st, en) in zip(c1, c2)]]
            CMap2 = np.c_[[np.linspace(st, en) for (st, en) in zip(c2, c3)]]
            CMap = np.c_[CMap1[:, :-1], CMap2]
            self.CMapN2P = np.transpose(CMap)/255.0
            self.CMap02P = np.flip(np.transpose(CMap1)/255.0, axis=0)
            baseline = str(self.regCont.baseline.currentText())
            target = str(self.regCont.target.currentText())
            self.fileManager.setTable(baseline, [1,0,0], 0.5, 0)
            self.fileManager.setTable(target, [0,0,1], 0.5, 0)
            reg = registration(self.files[baseline], self.files[target], steps = 5,
                               smooth=1).reg
            #reg.addActor(CMap = self.CMap02P)
            reg.addActor(CMap = self.CMapN2P)
            regName = target + '_reg'
            self.files[regName] = reg
            self.filesDrop.append(regName)
            self.fileManager.addRow(regName, self.files[regName])
            if hasattr(self, 'alCont'):
                self.alCont.getNames()
            if hasattr(self, 'regCont'):
                self.regCont.getNames()
            #im = []
            if self.regCont.tick.isChecked() is True:
                reg.actor.setScalarRange([-10,10])
                reg.actor.setShading(False)
                reg.CMapOut(colors=self.CMapN2P)
                reg.plotResults(name="distributionofshapevariance.png")
            print('Run the Registration code between %s and %s' % (baseline, target))
        else:
            show_message("Must be at least 2 objects loaded to run registration")
        
    def register(self):
        """
        Numpy style docstring.

        """
        self.regCont = RegistrationControls(self.filesDrop, self)
        self.regCont.show()
        self.regCont.reg.clicked.connect(self.runRegistration)
        

    
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
        if FEname[0] != "":  # Check that there was a file selected
            print(FEname)
            self.renWin.setnumViewports(1)
            self.FE = AmpObject([FEname[0],], stype='FE') # TODO check this is correct - AmpObject expects dicts or strings
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
        if vName[0] == "":  # If no file selected, exit
            return
        pName = QFileDialog.getOpenFileName(self, 'Open file',
                                            filter="Sensor pressures (*.csv)")
        if pName[0] == "":  # If no file selected, exit
            return
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
        
    def measure(self):
        #if no point selected condition move to analyse.py
        if self.pnt is None:
            print("Please select a reference point first.")
        else:
            [name, _, color, opacity, display] = self.fileManager.getRow(0)
            self.files[name].MeasurementsOut(self.pnt)
    
    def createActions(self):
        """
        Numpy style docstring.

        """
        self.openFile = QAction(QIcon('open.png'), 'Open', self,
                                shortcut='Ctrl+O',
                                triggered=self.chooseOpenFile)
        self.saveFile = QAction(QIcon('open.png'), 'Save', self,
                                shortcut='Ctrl+S',
                                triggered=self.chooseSaveFile)
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
        self.pick = QAction(QIcon('open.png'), 'Pick', self,
                                triggered=self.Point_Pick)
        self.removePick = QAction(QIcon('open.png'), 'Clear all picked points', self,
                                triggered = self.removePick)
        self.Measure = QAction(QIcon('open.png'), 'Generate Measurements', self,
                                triggered = self.measure)
        self.openObjectManager = QAction(QIcon('open.png'), 'Show Object Manager', self,
                                triggered=self.openAmpObjectManager)

    def createMenus(self):
        """
        Numpy style docstring.

        """
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openFile)
        self.fileMenu.addAction(self.saveFile)
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
        self.PointMenu = self.menuBar().addMenu("&Pick Point")
        self.PointMenu.addAction(self.pick)
        self.PointMenu.addAction(self.removePick)
        self.measureMenu = self.menuBar().addMenu("Measure")
        self.measureMenu.addAction(self.Measure)
        self.viewMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(self.openObjectManager)

    def openAmpObjectManager(self):
        self.fileManager.show()

    def objectsReady(self, num):
        return len(self.files) >= num


class fileManager(QMainWindow):
    """
    Controls to manage the displayed 
    
    Example
    -------
    Perhaps an example implementation:

    >>> from AmpScan.AmpScanGUI import AmpScanGUI
*
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
        # Set the minimum table size to when it is fully expanded
        self.table.setMinimumWidth(self.table.frameWidth()*2
                                   + self.table.horizontalHeader().length()
                                   + self.table.verticalHeader().width())
        
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
    
    def setTable(self, name, color = [1.0, 1.0, 1.0], opacity=1.0, display=2):
        for i in range(self.n):
            if self.table.item(i, 0).text() == name:
                self.table.item(i, 2).setText(str(color))
                self.table.item(i, 3).setText(str(opacity))
                self.table.item(i, 4).setCheckState(display)

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
        self.centre = QPushButton("Centre")
        self.setCentralWidget(self.main)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Static'), 0, 0)
        self.layout.addWidget(QLabel('Moving'), 1, 0)
        self.layout.addWidget(self.static, 0, 1)
        self.layout.addWidget(self.moving, 1, 1)
        self.layout.addWidget(self.centre, 2, 0, 1, -1)
        self.layout.addWidget(self.icp, 3, 0, 1, -1)
        rots = ['x', 'y', 'z']
        vals = ['-5', '-0.5', '+0.5', '+5']
        for i, r in enumerate(rots):
            setattr(self, r + 'rotBox', QHBoxLayout())
            setattr(self, r + 'rotButton', QButtonGroup())
            lab = QLabel(r + ' rotation')
            getattr(self, r + 'rotBox').addWidget(lab)
            for v in vals:
                button = QPushButton(v)
                getattr(self, r + 'rotBox').addWidget(button)
                getattr(self, r + 'rotButton').addButton(button)
            self.layout.addLayout(getattr(self, r + 'rotBox'), i+4, 0, 1, -1)
        for i, r in enumerate(rots):
            setattr(self, r + 'traBox', QHBoxLayout())
            setattr(self, r + 'traButton', QButtonGroup())
            lab = QLabel(r + ' translation')
            getattr(self, r + 'traBox').addWidget(lab)
            for v in vals:
                button = QPushButton(v)
                getattr(self, r + 'traBox').addWidget(button)
                getattr(self, r + 'traButton').addButton(button)
            self.layout.addLayout(getattr(self, r + 'traBox'), i+7, 0, 1, -1)
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
        self.tick = QCheckBox("Generate Output File for Comparison?")
        self.setCentralWidget(self.main)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel('Baseline'), 0, 0)
        self.layout.addWidget(QLabel('Target'), 1, 0)
        self.layout.addWidget(self.baseline, 0, 1)
        self.layout.addWidget(self.target, 1, 1)
        self.layout.addWidget(self.tick, 2,1)
        self.layout.addWidget(self.reg, 3, 0, 1, -1)
        self.main.setLayout(self.layout)
        self.setWindowTitle("Registration Manager")
        self.getNames()
    
    def getNames(self):
        """
        """
        self.baseline.clear()
        self.baseline.addItems(self.names)
        self.target.clear()
        self.target.addItems(self.names)


def show_message(message, message_type="err", title="An Error Occured..."):
    """
    Parameters
    ----------
    message : string
        The message to be displayed
    message_type : string
        The type of message e.g. "err" or "info"
    title : string
        The title of the dialog window

    Examples
    --------
    >>> show_message("test")
    >>> show_message("test2", "info", "test")

    """
    dialog = QMessageBox()
    dialog.setText(message)
    dialog.setWindowTitle(title)
    icons = {
        "err": QMessageBox.Critical,
        "info": QMessageBox.Information
    }
    dialog.setIcon(icons[message_type])
    dialog.setStandardButtons(QMessageBox.Ok)

    # Makes sure doesn't close until user closes it
    dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
#    mainWin = AlignControls([''])
    mainWin = AmpScanGUI()
    mainWin.show()
    sys.exit(app.exec_())