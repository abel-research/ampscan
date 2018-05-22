# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 09:05:19 2017

@author: js22g12

Backend for matplotlib to create a moveable spline figure 
"""

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl
from PyQt5.QtWidgets import QSizePolicy
import numpy as np
from scipy.special import binom

mpl.rcParams['axes.labelsize'] = 20
mpl.rcParams['lines.linewidth'] = 3
mpl.rcParams['xtick.labelsize'] = 15
mpl.rcParams['ytick.labelsize'] = 15

class socketDesignMixin(object):

    def TSBSocket(self, B, stype=0):
        if isinstance(stype, int):
            stype = self.stype[stype]
        data = getattr(self, stype)
        rho = np.sqrt(data['vert'][:, 0]**2 + data['vert'][:,1]**2)
        zRange = data['vert'][:, 2].max() - data['vert'][:, 2].min()
        zB = (B[:, 0] * zRange) + data['vert'][:, 2].min()
        perRed = np.interp(data['vert'][:, 2], zB, B[:, 1])
        data['values'] = rho * (perRed * 0.01)


class mplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=8, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        fig.patch.set_facecolor((0.9, 0.9, 0.9))
        self.axes.set_facecolor((0.9, 0.9, 0.9))

        self.compute_initial_figure()
        super(mplCanvas, self).__init__(fig)
#        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class dragSpline(mplCanvas):

    lock = None  #only one can be animated at a time

    def __init__(self, parent, Signal=None):
        super(dragSpline, self).__init__(parent)
        self.Signal = Signal
        self.points = np.array([[0.0, 8.0],
                                [0.5, 4.0],
                                [1.0, 0.0]])
        self.weights = np.array([1.0, 5.0, 1.0])
#        self.axes.set_ylim([0, 1])
#        self.axes.set_xlim([0, 8])
        self.axes.set_ylabel('Normalised distance along socket')
        self.axes.set_xlabel('Percentage reduction in volume')
        self.point = self.axes.plot(self.points[:, 1],
                                    self.points[:, 0],
                                    'ob', markersize=15,
                                    picker=50)[0]
        self.spline = self.axes.plot(0, 0)[0]
        self.bezierCurve()
        self.press = None
        self.background = None
        self.connect()

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.point.axes: return
        if dragSpline.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.press = self.point.get_xydata(), attrd['ind'][0], event.xdata, event.ydata
        dragSpline.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        self.spline.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)
        axes.draw_artist(self.spline)
        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if dragSpline.lock is not self:
            return
        if event.inaxes != self.point.axes: return
#        self.point.set_xdata, self.point._y, xpress, ypress = self.press
        self.point.set_xdata(self.press[0][:, 0])
        self.point.set_ydata(self.press[0][:, 1])

        xpress = self.press[2]
        ypress = self.press[3]
        
        self.points[:, 1] = self.point.get_xdata() 
        self.points[self.press[1], 1] += event.xdata - xpress
        self.points[:, 1] = np.clip(self.points[:, 1], 0, 8)
#        if self.press[1] == 1:
#            self.points[:, 1] = self.point.get_xdata() 
#            self.points[self.press[1], 1] += event.xdata - xpress
        

        self.point.set_xdata(self.points[:, 1])
        self.point.set_ydata(self.points[:, 0])
        
        self.bezierCurve()

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)
        axes.draw_artist(self.spline)
        # blit just the redrawn area
        canvas.blit(axes.bbox)
        if self.Signal is not None:
            self.Signal.emit()


    def on_release(self, event):
        'on release we reset the press data'
        if dragSpline.lock is not self:
            return

        self.press = None
        dragSpline.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        self.spline.set_animated(False)
        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
        
    def bezierCurve(self):
        t = np.linspace(0, 1, 101)
        num = np.zeros([101, 2])
        dem = np.zeros([101, 2])
        n = self.points.shape[0] - 1
        for (i, point), weight in zip(enumerate(self.points), self.weights):
            biCoeff = binom(n, i)
            num = num + ((biCoeff*t**i) * ((1-t)**(n-i)))[:, None] * point * weight
            dem = dem + ((biCoeff*t**i) * ((1-t)**(n-i)))[:, None] * weight
        self.B = num/dem
        self.spline.set_xdata(self.B[:, 1])
        self.spline.set_ydata(self.B[:, 0])
