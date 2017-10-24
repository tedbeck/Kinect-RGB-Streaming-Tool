# PyQt5 application to house an animated matplotlib bar graph
# bar graph changes in respect to streamed data pulled from a
# local TCP/IP socket which is buffering data from an XBox 360
# Kinect

import sys, os

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from TCPListener import TCPListener

class MyCanvas(FigureCanvas):
    # initializes canvas for placement in PyQt window
    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = plt.figure()

        plt.tick_params(axis = 'x', colors = 'black')
        plt.tick_params(axis = 'y', colors = 'black')
        
        position = np.arange(3) + 0.5 
        plt.xticks(position, ('r', 'g', 'b'))
        plt.xlabel('color stream', color = 'black')
        plt.ylabel('average strength in frame', color = 'black')
        plt.ylim((0, 255))
        plt.xlim((0, 3))
        plt.grid(True)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

class AnimationWidget(QWidget):
    # defines start and stop buttons for animation; animation function pulls
    # data from local TCP/IP socket
    def __init__(self):
        QMainWindow.__init__(self)

        vbox = QVBoxLayout()
        self.setWindowTitle('RGB Stream Pixel Color Strength')
        self.canvas = MyCanvas(self, width = 5, height = 4, dpi = 100)
        vbox.addWidget(self.canvas)

        hbox = QHBoxLayout()
        self.start_button = QPushButton('Start', self)
        self.stop_button = QPushButton('Stop', self)
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.stop_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.playing = False
        
        position = np.arange(3) + 0.5 
        heights = [0, 0, 0]
        cols = ['r', 'g', 'b']
        rects = plt.bar(position, heights, align = 'center', color = cols) 
        self.rs = [r for r in rects]
        # creates TCP/IP stream through TCPListener module
        self.listener = TCPListener()

    def animate(self, i):
        # pulls data from TCP/IP stream; data stream is raw binary (/x00) feed
        # four bytes are transmitted for each pixel: R, G, and B values, then a fourth
        # saturation value which is zero in RGB mode
        byte_stream = self.listener.receive_bytes()
        current_colors = [0, 0, 0, 0]
        stream_length = len(byte_stream)
        # add each color value to the appropriate list index
        for x in range(stream_length):
            current_colors[x % 4] += byte_stream[x]
        # divide the sums by the count of pixels in the stream
        current_colors[0] = int(current_colors[0] / (stream_length / 4))
        current_colors[1] = int(current_colors[1] / (stream_length / 4))
        current_colors[2] = int(current_colors[2] / (stream_length / 4))
        # animate the bar graphs by setting each height to the average color strength
        counter = 0
        for r in self.rs:
            r.set_height(current_colors[counter])
            counter += 1
        return self.rs

    def on_start(self):
        if self.playing:
            pass
        else:
            self.playing = True
            self.anim = animation.FuncAnimation(self.canvas.figure, self.animate, blit = True, interval = 25)

    def on_stop(self):
        if self.playing:
            self.playing = False
            self.anim._stop()
        else:
            pass

if __name__ == '__main__':
    App = QApplication(sys.argv)
    widg = AnimationWidget()
    widg.show()
    sys.exit(App.exec_())