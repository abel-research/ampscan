# -*- coding: utf-8 -*-
"""
Created on Wed May  2 20:21:07 2018

@author: Josh
"""

import AmpScan as ampS
from PyQt5.QtWidgets import QApplication
import sys
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ampS.AmpScanGUI()
    mainWin.show()
    sys.exit(app.exec_())