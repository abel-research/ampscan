# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 16:21:12 2017

@author: js22g12
"""

import sys
import os
os.chdir('C:\\Local\\Documents (Local)\\Code\\AmpScan\\')
import numpy as np
from AmpScan.core import AmpObject
from AmpScan.ampVis import qtVtkWindow
from PyQt5.QtWidgets import (QAction, QApplication, QGridLayout,
                             QMainWindow, QFileDialog, QWidget, QSlider,
                             QGroupBox, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt


class GUI(QMainWindow):
    def __init__(self, parent=None):
        super(GUI, self).__init__()
        self.points = np.zeros([5])
        self.AmpObj = None
        self.mainWidget = QWidget()
        self.limbWidget = qtVtkWindow()
        self.limbRen = self.limbWidget._RenderWindow
        self.limbRen.setBackground([0.9,0.9,0.9])
        self.socketWidget = qtVtkWindow()
        self.socketRen = self.socketWidget._RenderWindow
        self.socketRen.setBackground([0.9,0.9,0.9])
        self.setCentralWidget(self.mainWidget)
        self.createActions()
        self.createMenus()
        self.Layout = QGridLayout()
        self.sl = self.sliders()
        self.Layout.addWidget(self.limbWidget, 0, 0, -1, 1)
        self.Layout.addWidget(self.sl, 0, 1, 1, 1)
        self.Layout.addWidget(self.socketWidget, 1, 1, 3, 1)
        self.mainWidget.setLayout(self.Layout)
        self.setWindowTitle("AmpScan Visualiser")
        self.resize(1200, 800)
        self.show()

    def plotPress(self):
        for i, s in enumerate(self.sliders):
            self.points[i] = s.value()/100
        if self.AmpObj is None:
            return
        self.AmpObj.surrPred(self.points[2:])
        self.AmpObj.actor.setValues(self.AmpObj.values)
        self.limbRen.Render()
        
    def sliders(self):
        variables = ['Residuum Length', 'Residuum Bulk', 'Proximal Reduction', 
                     'Mid Reduction', 'Distal Reduction']
        values = [50, 50, 0, 0, 0]
        groupBox = QGroupBox('Model Variables')
        box = QGridLayout()
        self.sliders = []
        for v, (i, t) in zip(values, enumerate(variables)):
            self.sliders.append(QSlider(Qt.Horizontal))
            self.sliders[-1] = QSlider(Qt.Horizontal)
            self.sliders[-1].setFocusPolicy(Qt.StrongFocus)
            self.sliders[-1].setTickPosition(QSlider.TicksBothSides)
            self.sliders[-1].setTickInterval(10)
            self.sliders[-1].setSingleStep(1)
            self.sliders[-1].setMinimum(0)
            self.sliders[-1].setMaximum(100)
            self.sliders[-1].setValue(v)
            self.sliders[-1].valueChanged.connect(self.plotPress)
            tx = QLabel(t)
            box.addWidget(tx, i, 0)
            box.addWidget(self.sliders[-1], i, 1)        
        groupBox.setLayout(box)
        return groupBox

    def chooseOpenFile(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',
                                                 filter="Surrogate Model (*.npy)")
        data = np.load(self.fname[0]).item()
        self.AmpObj = AmpObject(data['limb'], stype='FE')
        self.AmpObj.centre()
        self.AmpObj.addSurrogate(data['surr'])
        self.socket = AmpObject(data['socket'])
        for i, s in enumerate(self.sliders):
            self.points[i] = s.value()/100
        self.AmpObj.surrPred(self.points[2:])
        c1 = [212.0, 221.0, 225.0]
        c2 = [31.0, 73.0, 125.0]
        CMap = np.c_[[np.linspace(st, en) for (st, en) in zip(c1, c2)]]
        CMap = np.transpose(CMap)/255.0
        self.AmpObj.addActor(CMap=CMap, bands = 10)
        self.AmpObj.actor.setNorm()
        self.AmpObj.actor.setScalarRange([0, 60])
        self.socket.addActor(CMap=CMap, bands = 10)
        self.socket.actor.setNorm()
        self.socket.actor.setScalarRange([0, 6])
        self.limbRen.renderActors([self.AmpObj.actor,], shading=False)
        self.limbRen.setScalarBar(self.AmpObj.actor)
        self.limbRen.setView()
        self.socketRen.renderActors([self.socket.actor,], shading=True)
        self.socketRen.setScalarBar(self.socket.actor)
        self.socketRen.setView()


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