# -*- coding: utf-8 -*-
"""
This example demonstrates the use of RemoteGraphicsView to improve performance in
applications with heavy load. It works by starting a second process to handle
all graphics rendering, thus freeing up the main process to do its work.

In this example, the update() function is very expensive and is called frequently.
After update() generates a new set of data, it can either plot directly to a local
plot (bottom) or remotely via a RemoteGraphicsView (top), allowing speed comparison
between the two cases. IF you have a multi-core CPU, it should be obvious that the
remote case is much faster.
"""

import sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.widgets.RemoteGraphicsView
import numpy as np
import time
import sys
import numpy as np


class magictable_monitor_window():
    def __init__(self):
        # try what is in "PlotSpeedTest.py"
        self.app = QtGui.QApplication([])

        # pg.setConfigOption('background', 'w')

        self.win = pg.GraphicsWindow() # so far so good.
        self.win.resize(600, 1000)

        # self.layO = pg.GraphicsLayout()


        self.xObject = 0
        self.yObject = 0
        self.xObject_pr = 0
        self.yObject_pr = 0
        self.ax = 0
        # self.vx_pr = 0
        # self.v_pr = 0
        self.theta_pr = 0
        self.xObject_ball = 0
        self.yObject_ball = 0


        # self.p = pg.plot()
        self.p = self.win.addPlot(row=0, col=0, title='cupX')
        self.p2 = self.win.addPlot(row=1, col=0, title='ballX')
        self.p3 = self.win.addPlot(row=2, col=0, title='te_ball')
        self.p4 = self.win.addPlot(row=3, col=0, title='acc')
        self.p5 = self.win.addPlot(row=4, col=0, title='EM')

        self.p5.setYRange(-3, 2, padding=0)


        #self.p.setWindowTitle('pyqtgraph example: PlotSpeedTest')

        #self.p.setRange(QtCore.QRectF(0, -10, 5000, 20))
        #self.p.setLabel('bottom', 'Index', units='B')
        self.curve =self.p.plot(pen=pg.mkPen(width=3))
        self.curve2 =self.p2.plot(pen=pg.mkPen(width=3))
        self.curve3 = self.p3.plot(pen=pg.mkPen(width=3))
        self.curve4 = self.p4.plot(pen=pg.mkPen(width=3))
        self.curve5 = self.p5.plot(pen=pg.mkPen(width=3))

        # self.data = np.random.normal(size=(50, 5000))
        self.ptr = 0
        self.lastTime = time.time()
        self.fps = None
        self.data =  np.random.normal(size=300)
        self.data2 = np.random.normal(size=300)
        self.data3 = np.random.normal(size=300)
        self.data4 = np.random.normal(size=300)
        self.data5 = np.random.normal(size=300)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)

    def deriv(self, a, a_p, dt):
        return (a - a_p) / dt

    def lookupTB(self, ball_amp): # change to 2D
        # np.sqrt(x, y)
        # ball_amp (ball amplitude) range:  0 to 4?
        theta= (np.pi/6)*ball_amp
        return theta

    def update(self):
        # global curve, data, ptr, p, lastTime, fps
        self.data[:-1] = self.data[1:]  # shift data in the array one sample left
        self.data2[:-1] = self.data2[1:]  # shift data in the array one sample left
        self.data3[:-1] = self.data3[1:]  # shift data in the array one sample left
        self.data4[:-1] = self.data4[1:]  # shift data in the array one sample left
        self.data5[:-1] = self.data5[1:]  # shift data in the array one sample left

        # (see also: np.roll)
        ## energy margin calc
        dt = 0.03 # TODO: do with time.time()
        l = 0.1  # pendulum length (m)
        m = 0.07  # ball mass kg
        g = 9.81
        # v = self.deriv(self.xObject, self.xObject_pr, dt)
        # v = v*0.01/8 # need to map px to (m).  8px = 0.01m, roughly.
        # v= self.vx*0.01/8
        # a = self.deriv(v, self.v_pr, dt)
        """ unit conversion px to m """
        self.xObject = self.xObject * 0.0013  # 640 px = 0.8m.    m/px
        self.xObject_ball = self.xObject_ball * 0.0013  # 640 px = 0.8m.    m/px
        self.yObject = self.yObject * 0.0013  # 640 px = 0.8m.    m/px
        self.yObject_ball = self.yObject_ball * 0.0013  # 640 px = 0.8m.    m/px

        # Filter the data, and plot both the original and filtered signals.
        filteredx = butter_lowpass_filter(self.xObject, cutoff, fs, order)
        filtered_xb = butter_lowpass_filter(self.xObject_ball, cutoff, fs, order)
        filteredy = butter_lowpass_filter(self.yObject, cutoff, fs, order)
        filtered_yb = butter_lowpass_filter(self.yObject_ball, cutoff, fs, order)

        theta_esc = np.pi / 6  # (try 45 deg)
        ball_ampx = filtered_xb - filteredx
        ball_ampy = filtered_yb - filteredy
        ball_amp = np.sqrt(np.power(ball_ampx, 2) + np.power(ball_ampy, 2))

        l = 0  # dummy
        if i == 0 or i == 1:  # ID1, 2
            l = 0.1
        else:
            l = 0.2

        theta1 = np.arcsin(ball_amp / (l))
        filtered_theta1 = butter_lowpass_filter(theta1, cutoff, fs, order)
        theta2 = np.arctan2(ball_ampy, ball_ampx)
        filtered_theta2 = butter_lowpass_filter(theta2, cutoff, fs, order)

        theta1_deg = filtered_theta1 * 180 / np.pi
        theta2_deg = filtered_theta2 * 180 / np.pi
        # filtered_theta1 = filtered_theta1 * 180 / np.pi
        # filtered_theta2 = filtered_theta2 * 180 / np.pi

        omega1 = np.gradient(theta1, dt)
        omega2 = np.gradient(theta2, dt)  ## will not be used.
        omega1_deg = omega1 * 180 / np.pi
        omega2_deg = omega2 * 180 / np.pi  ## will not be used

        filtered_omega1 = np.gradient(omega1, dt)
        filtered_omega2 = np.gradient(omega2, dt)  ## will not be used

        # omega = self.deriv(theta, self.theta_pr, dt)

        pse = pseudo_energy_ball_2d(theta1, theta2, ax, ay, l)
        ke = KE_2D(theta1, theta2, v, ax, ay, l)
        pe = PE(theta1, l)
        te = total_energy_2d(theta1, theta2, v, filteredax, filtereday, l)
        e_esc = escape_energy_2d(theta_esc, theta2, filteredax, filtereday, l)

        em = energy_margin_2d(theta1, theta2, v, theta_esc, filteredax, filtereday, l)

        # a = self.ax*0.01/8
        # e_esc = m*g*l*(1-np.cos(theta_esc))+ m*abs(a)*l*np.sin(theta_esc) + m*abs(a)*l # escape energy
        # pse_ball = m*a*l*np.sin(theta) + m*a*l if a>=0 else m*a*l*np.sin(theta)- m*a*l
        # pse_ball = m*a*l*np.sin(theta) + m*abs(a)*l
        #
        # te_ball = 0.5*m*np.power((l*omega),2) + m*g*l*(1-np.cos(theta)) + pse_ball # total energy
        # em = (e_esc - te_ball) / e_esc;

        # print("xcup, xball:", self.xObject, self.xObject_ball)

        self.data[-1] =  self.xObject #np.random.normal()
        self.data2[-1] = self.xObject_ball - self.xObject # np.random.normal()
        self.data3[-1] = te  # np.random.normal()
        self.data4[-1] = e_esc # np.random.normal()
        self.data5[-1] = em
        self.curve.setData(self.data)
        self.curve2.setData(self.data2)
        self.curve3.setData(self.data3)
        self.curve4.setData(self.data4)
        self.curve5.setData(self.data5)
        # self.curve.setData(self.data[self.ptr % 10])
        self.ptr += 1
        self.curve.setPos(self.ptr, 0)
        self.curve2.setPos(self.ptr, 0)
        self.curve3.setPos(self.ptr, 0)
        self.curve4.setPos(self.ptr, 0)
        self.curve5.setPos(self.ptr, 0)

        now = time.time()
        dt = now - self.lastTime
        self.lastTime = now
        if self.fps is None:
            self.fps = 1.0 / dt
        else:
            s = np.clip(dt * 3., 0, 1)
            self.fps = self.fps * (1 - s) + (1.0 / dt) * s
        # self.p.setTitle('%0.2f fps' % self.fps)
        self.app.processEvents()  ## force complete redraw for every plot

        # variable update
        self.xObject_pr = self.xObject
        self.yObject_pr = self.yObject
        # self.vx_pr = self.vx
        # self.v_pr = v
        self.theta_pr = theta

    def updateCoordinate(self, x, y, ax, ay, x_b, y_b):
        self.xObject = x
        self.yObject = y
        self.ax = ax
        self.xObject_ball = x_b
        self.yObject_ball = y_b

    # def quit_this(self):
    #     sys.exit(self.app.exec_())


    #
    #     self.xObject= 0
    #     self.yObject= 0
    #     self.view1 = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
    #     pg.setConfigOptions(antialias=True)  ## this will be expensive for the local plot
    #     self.view1.pg.setConfigOptions(antialias=True)  ## prettier plots at no cost to the main process!
    #     self.view1.setWindowTitle('pyqtgraph example: RemoteSpeedTest')
    #
    #
    #     self.label = QtGui.QLabel()
    #     self.rcheck = QtGui.QCheckBox('plot remote')
    #     self.rcheck.setChecked(True)
    #     # self.lcheck = QtGui.QCheckBox('plot local')
    #     # self.lplt = pg.PlotWidget()
    #     self.layout = pg.LayoutWidget()
    #     # self.layout.addWidget(self.rcheck)
    #     # self.layout.addWidget(self.lcheck)
    #     self.layout.addWidget(self.label)
    #     self.layout.addWidget(self.view1, row=1, col=0, colspan=3)
    #
    #     # self.layout.addWidget(self.lplt, row=2, col=0, colspan=3)
    #     self.layout.resize(800, 800)
    #     self.layout.show()
    #
    #     ## Create a PlotItem in the remote process that will be displayed locally
    #     self.rplt = self.view1.pg.PlotItem()
    #     self.rplt._setProxyOptions(deferGetattr=True)  ## speeds up access to rplt.plot
    #     self.view1.setCentralItem(self.rplt)
    #
    #     self.lastUpdate = pg.ptime.time()
    #     self.avgFps = 0.0
    #
    #
    #
    #
    #     # win = pg.GraphicsWindow()
    #     # win.setWindowTitle('pyqtgraph example: Scrolling Plots')
    #
    #
    #     # 1) Simplest approach -- update data in the array such that plot appears to scroll
    #     #    In these examples, the array size is fixed.
    #     self.layout.addWidget(self.view1)
    #
    #     self.data1 = np.random.normal(size=300)
    #     #self.data1= np.zeros((300,))
    #     self.curve1 = self.rplt.plot(self.data1)
    #     # curve2 = p2.plot(data1)
    #     self.ptr1 = 0
    #
    #
    #     self.timer = QtCore.QTimer()
    #     self.timer.timeout.connect(self.update1)
    #     self.timer.start(0)
    #
    # def updateCoordinate(self, x, y):
    #     self.xObject = x
    #     self.yObject = y
    #
    # def update1(self):
    #     self.data1[:-1] = self.data1[1:]  # shift data in the array one sample left
    #     # (see also: np.roll)
    #     self.data1[-1] =  self.xObject #np.random.normal()
    #     self.curve1.setData(self.data1)
    #     #self.curve1.setXRange(0, 350)
    #     self.ptr1 += 1
    #     self.curve1.setPos(self.ptr1, 0)


#
# class magictable_monitor_window():
#     def __init__(self):
#         app = pg.mkQApp() # must be here. but dont know how to exit.
#         self.xObject= 0
#         self.yObject= 0
#         self.view1 = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
#         pg.setConfigOptions(antialias=True)  ## this will be expensive for the local plot
#         self.view1.pg.setConfigOptions(antialias=True)  ## prettier plots at no cost to the main process!
#         self.view1.setWindowTitle('pyqtgraph example: RemoteSpeedTest')
#
#
#         self.label = QtGui.QLabel()
#         self.rcheck = QtGui.QCheckBox('plot remote')
#         self.rcheck.setChecked(True)
#         # self.lcheck = QtGui.QCheckBox('plot local')
#         # self.lplt = pg.PlotWidget()
#         self.layout = pg.LayoutWidget()
#         # self.layout.addWidget(self.rcheck)
#         # self.layout.addWidget(self.lcheck)
#         self.layout.addWidget(self.label)
#         self.layout.addWidget(self.view1, row=1, col=0, colspan=3)
#
#         # self.layout.addWidget(self.lplt, row=2, col=0, colspan=3)
#         self.layout.resize(800, 800)
#         self.layout.show()
#
#         ## Create a PlotItem in the remote process that will be displayed locally
#         self.rplt = self.view1.pg.PlotItem()
#         self.rplt._setProxyOptions(deferGetattr=True)  ## speeds up access to rplt.plot
#         self.view1.setCentralItem(self.rplt)
#
#         self.lastUpdate = pg.ptime.time()
#         self.avgFps = 0.0
#
#
#
#
#         # win = pg.GraphicsWindow()
#         # win.setWindowTitle('pyqtgraph example: Scrolling Plots')
#
#
#         # 1) Simplest approach -- update data in the array such that plot appears to scroll
#         #    In these examples, the array size is fixed.
#         self.layout.addWidget(self.view1)
#
#         self.data1 = np.random.normal(size=300)
#         #self.data1= np.zeros((300,))
#         self.curve1 = self.rplt.plot(self.data1)
#         # curve2 = p2.plot(data1)
#         self.ptr1 = 0
#
#
#         self.timer = QtCore.QTimer()
#         self.timer.timeout.connect(self.update1)
#         self.timer.start(0)
#
#     def updateCoordinate(self, x, y):
#         self.xObject = x
#         self.yObject = y
#
#     def update1(self):
#         self.data1[:-1] = self.data1[1:]  # shift data in the array one sample left
#         # (see also: np.roll)
#         self.data1[-1] =  self.xObject #np.random.normal()
#         self.curve1.setData(self.data1)
#         #self.curve1.setXRange(0, 350)
#         self.ptr1 += 1
#         self.curve1.setPos(self.ptr1, 0)
#
#     # def update1(self):
#     #     #global check, plt, rpltfunc
#     #     self.data = np.random.normal(size=(10000, 50)).sum(axis=1)
#     #     #self.data += 5 * np.sin(np.linspace(0, 10, self.data.shape[0]))
#     #
#     #     #self.data = self.xObject
#     #
#     #     if self.rcheck.isChecked():
#     #         self.rplt.plot(self.data, clear=True, _callSync='off')  ## We do not expect a return value.
#     #         ## By turning off callSync, we tell
#     #         ## the proxy that it does not need to
#     #         ## wait for a reply from the remote
#     #         ## process.
#     #     # if self.lcheck.isChecked():
#     #     #     self.lplt.plot(self.data, clear=True)
#     #
#     #     now = pg.ptime.time()
#     #     fps = 1.0 / (now - self.lastUpdate)
#     #     self.lastUpdate = now
#     #     self.avgFps = self.avgFps * 0.8 + fps * 0.2
#     #     self.label.setText("Generating %0.2f fps" % self.avgFps)


def run(): # only reached through __main__
    app = pg.mkQApp()
    win=magictable_monitor_window()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    import initExample  ## Add path to library (just for examples; you do not need this)
    from pyqtgraph.Qt import QtGui, QtCore
    import pyqtgraph as pg
    import pyqtgraph.widgets.RemoteGraphicsView
    import numpy as np

    run()
    #
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #     win = magictable_monitor_window()
    #     win.app.exec_()
    #     # QtGui.QApplication.instance().exec_()

