# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 16:21:12 2017

@author: js22g12
"""

import sys
import numpy as np
from .core import AmpObject
from .ampVis import qtVtkWindow
from .tsbSocketDesign import dragSpline
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout,
                             QMainWindow, QFileDialog, QWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal


class GUI(QMainWindow):
    mplChange = pyqtSignal()
    def __init__(self, parent=None):
        super(GUI, self).__init__()
        self.AmpObj = None
        self.CMap = np.array([[212.0, 221.0, 225.0],
                              [31.0, 73.0, 125.0]])/255.0
        self.splineWidget = QWidget()
        self.mainWidget = QWidget()
        self.vtkWidget = qtVtkWindow()
        self.renWin = self.vtkWidget._RenderWindow
        self.renWin.setBackground()
        self.setCentralWidget(self.mainWidget)
        self.createActions()
        self.createMenus()
        self.Layout = QGridLayout()
        self.splineWin = dragSpline(self.splineWidget, self.mplChange)
        self.mplChange.connect(self.plotPress)
        self.Layout.addWidget(self.splineWin, 0, 1, 1, 4)
        self.Layout.addWidget(self.vtkWidget, 0, 0, 1, 1)
        self.mainWidget.setLayout(self.Layout)
        self.setWindowTitle("AmpScan Visualiser")
        self.resize(1200, 800)
        self.show()

    def plotPress(self):
        if self.AmpObj is None:
            return
        points = self.splineWin.points[:, 1]/8.0
        points = np.clip(points, 0, 1)
        self.AmpObj.surrPred(points)
        self.AmpObj.actor.setValues(self.AmpObj.values)
        self.renWin.Render()
        

    def chooseOpenFile(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',
                                                 filter="FE Mesh (*.npy)")
        self.AmpObj = AmpObject(self.fname[0], stype='FE')
        self.AmpObj.centre()
        self.sname = QFileDialog.getOpenFileName(self, 'Open surrogate',
                                                 filter="surrogate (*.npy)")
        self.AmpObj.addSurrogate(self.sname[0])
        points = self.splineWin.points[:, 1]/8.0
        self.AmpObj.surrPred(points)
        self.AmpObj.addActor(CMap=self.CMap)
        self.AmpObj.actor.setNorm()
        self.AmpObj.actor.setScalarRange([0, 60])
        self.renWin.renderActors([self.AmpObj.actor,])
        self.renWin.setScalarBar(self.AmpObj.actor)
    

    def createActions(self):
        self.openFile = QAction(QIcon('open.png'), 'Open', self,
                                shortcut='Ctrl+O',
                                triggered=self.chooseOpenFile)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openFile)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = GUI()
    mainWin.show()
    sys.exit(app.exec_())