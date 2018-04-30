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
        self.vtkWidget.setBackground(color=[1,1,1])
        self.setCentralWidget(self.mainWidget)
        self.createActions()
        self.createMenus()
        self.Layout = QGridLayout()
        self.splineWin = dragSpline(self.splineWidget, self.mplChange)
        self.mplChange.connect(self.plotRect)
        self.Layout.addWidget(self.splineWin, 0, 1, 1, 4)
        self.Layout.addWidget(self.vtkWidget, 0, 0, 1, 1)
        self.mainWidget.setLayout(self.Layout)
        self.setWindowTitle("AmpScan Visualiser")
        self.resize(1200, 800)
        self.show()

    def plotRect(self):
        if self.AmpObj is None:
            return
        self.AmpObj.TSBSocket(self.splineWin.B, stype='reglimb')
        self.AmpObj.actors['reglimb'].setRect(self.AmpObj.reglimb['values'])
        self.vtkWidget.iren.Render()

    def chooseOpenFile(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',
                                                 filter="Meshes (*.stl)")
        self.AmpObj = AmpObject(self.fname[0], 'reglimb')
        self.AmpObj.centre()
        self.AmpObj.TSBSocket(self.splineWin.B, stype='reglimb')
        self.AmpObj.addActor(stype='reglimb', CMap=self.CMap)
        self.AmpObj.actors['reglimb'].setScalarRange(0, 6)
        self.vtkWidget.renderActors(self.AmpObj.actors, dispActors=['reglimb', ])
        self.vtkWidget.setScalarBar(self.AmpObj.actors['reglimb'])

    def createActions(self):
        self.openFile = QAction(QIcon('open.png'), 'Open', self,
                                shortcut='Ctrl+O',
                                triggered=self.chooseOpenFile)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openFile)


def socketDesignGUI():
#    if __name__ == "__main__":
        app = QApplication(sys.argv)
        mainWin = GUI()
        mainWin.show()
        sys.exit(app.exec_())