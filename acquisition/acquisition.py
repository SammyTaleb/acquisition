import time
import pandas as pd
import pyvisa
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QWidget, QLabel
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from gui_preprod import *
import seaborn as sns
import numpy as np
import pandas as pd
import os

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class Connection:
    def __init__(self, _logger, _config):
        self.config = _config
        self.logger = _logger
        try:
            self.rm = pyvisa.ResourceManager()
            # self.logger.log('ressource manager created', logging.info)

            self.inst = self.rm.open_resource(self.rm.list_resources()[0])
            time.sleep(1)
            device = self.inst.query("*IDN?")
            self.logger.log(f"Connected to , {device.split(',')[0]} {device.split(',')[1]}", logging.info)
        except Exception as e:
            self.logger.log('Connection Failed', logging.error)
        try:
            self.logger.log(f"Trying to configure the device", logging.info)
            self.configure()
        except Exception as e:
            self.logger.log(f'Configuration of the device has failed : {e}', logging.error)

    def configure(self):
        """
        configure the acquisition measures
        :return:
        """
        self.inst.timeout = 5000  # set a delay
        self.inst.write("*CLS")  # clear
        self.inst.write("*RST")  # reset
        for sensor in self.config['sensors']:
            if sensor[0] == 'TC':
                query = f"CONF:TEMP TC,K,(@{sensor[1]})"
                print(query)
                self.inst.write(query)
        scan_list = "(@" + ','.join([sensor[1] for sensor in self.config['sensors']]) + ')'
        print(scan_list)
        self.inst.write("ROUTE:SCAN " + scan_list)
        # self.logger.log('Configuration is done', logging.info)


class MyMplCanvas(FigureCanvas, TimedAnimation):
    def __init__(self, parent=None, config=None, conn=None):
        self.config = config
        self.conn = conn
        self.fig = Figure(figsize=(15, 10), dpi=100)
        self.axes = []
        self.lines = []
        self.create_axes()
        self.data_final = {}
        self.data_final[f'time'] = []
        for i in self.config['sensors']:
            self.data_final[f'value_{i[0]}_{i[1]}'] = []
        self.data = [[[], []] for i in range(len(self.axes))]
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=1000 * self.config['delay'], repeat=False, blit=True)
        self.setParent(parent)
        self.start = time.time()

    def create_axes(self):
        nbr_sensors = len(self.config['sensors'])
        color_palette = list(sns.color_palette(None, nbr_sensors))
        val = str(nbr_sensors) + "1"
        for i in range(nbr_sensors):
            print(int(val + str(i + 1)))
            #  add_subplot(abc) where a is the number of plots, b is the column index (1,2,...), c is the row index
            ax = self.fig.add_subplot(int(val + str(i + 1)))
            ax.set_xlabel('time')

            ax.set_ylabel(self.config['sensors'][i][0]+" @"+self.config['sensors'][i][1])
            ax.set_xlim(0, 100) #demander à l'utilisateur
            ax.set_ylim(10, 40) #demander à l'utilisateur
            line = Line2D([], [], color=color_palette[i])
            ax.add_line(line)
            self.lines.append(line)
            self.axes.append(ax)

    def data_gen(self):
        t = time.time() - self.start
        self.conn.inst.write("INIT;")
        self.conn.inst.write(":FETCH?;")
        result = self.conn.inst.read()
        y = result.split(',')[:len(self.axes)]
        self.data_final[f'time'].append(t)
        for i, val in enumerate(self.config['sensors']):
            self.data[i][0].append(t)
            self.data[i][1].append(float(y[i]))
            self.data_final[f'value_{val[0]}_{val[1]}'].append(float(y[i]))

    def _draw_frame(self, framedata):
        i = framedata
        print(i)
        self.data_gen()
        for i in range(len(self.lines)):
            self.lines[i].set_data(self.data[i][0], self.data[i][1])
        self._drawn_artists = self.lines

    def new_frame_seq(self):
        return iter(range(self.config['scans']))

    def _init_draw(self):
        for line in self.lines:
            line.set_data([], [])


class Ui_OtherWindow(object):
    def __init__(self, MainWindow, config, conn, style):
        self.config = config
        self.conn = conn
        self.style = style
        self.win = MainWindow
        self.win.setObjectName("MainWindow")
        self.win.resize(1413, 1018)
        self.central_widget = MyMplCanvas(self.win, config=self.config, conn=self.conn)
        self.button_start = QtWidgets.QPushButton('RUNNING', self.central_widget)
        self.button_start.setStyleSheet(style)
        self.button_start.setFixedHeight(30)
        self.button_start.setFixedWidth(200)
        self.button_start.move(50, 300)
        self.button_start.setDisabled(True)
        self.button_stop = QtWidgets.QPushButton('STOP', self.central_widget)
        self.button_stop.setStyleSheet(style)
        self.button_stop.setFixedHeight(30)
        self.button_stop.setFixedWidth(200)
        self.button_stop.move(50, 900)
        self.button_pause = QtWidgets.QPushButton('PAUSE', self.central_widget)
        self.button_pause.setStyleSheet(style)
        self.button_pause.setFixedHeight(30)
        self.button_pause.setFixedWidth(200)
        self.button_pause.move(50, 600)
        self.button_pause.clicked.connect(self.pause)
        self.button_stop.clicked.connect(self.stop)
        self.button_start.clicked.connect(self.start)

    def stop(self):
        data = pd.DataFrame(self.central_widget.data_final)
        print(data)
        filename = self.config['file']['filename']
        filetype = self.config['file']['type']
        if filetype == 'csv':
            data.to_csv(f'data/saved/{filename}.{filetype}')
        else:
            data.to_excel(f'data/saved/{filename}.{filetype}')
        self.central_widget.pause()
        self.button_start.deleteLater()
        self.button_pause.deleteLater()
        self.button_stop.deleteLater()
        print(os.getcwd())
        os.startfile(f'{os.getcwd()}\data\saved\{filename}.{filetype}')

    def pause(self):
        self.central_widget.pause()
        self.button_start.setDisabled(False)
        self.button_start.setText('RESUME')
        self.button_pause.setDisabled(True)
        self.button_pause.setText('PAUSED')

    def start(self):
        self.button_start.setText('RUNNING')
        self.button_pause.setText('PAUSE')
        self.button_start.setDisabled(True)
        self.button_pause.setDisabled(False)
        self.central_widget.resume()


"""
class Animation:
    def __init__(self, nbr_scan, _logger, _config, canvas):
        self.conn = Connection(_logger, _config)
        self.conn.configure()
        self.start = time.time()
        self.nbr_scan = nbr_scan
        self.canvas = canvas

    def data_gen(self):
        cnt = 0
        self.start = time.time()
        while cnt < self.nbr_scan:
            cnt += 1
            t = time.time() - self.start
            self.conn.inst.write("INIT;")
            self.conn.inst.write(":FETCH?;")
            y1, y2 = self.conn.inst.read().split(',')[:2]
            # adapted the data generator to yield both sin and cos
            yield t, float(y1), float(y2)

    @staticmethod
    def save(data):
        t, y1, y2 = data
        df = pd.DataFrame(
            {"time": t, "Temp @101": y1, "Temp @102": y2},
            columns=['time', "Temp @101", "Temp @102"]
        )
        print(df)
        return df

    def loop(self):
        fig = self.canvas.fig
        ax1 = self.canvas.ax1
        ax2 = self.canvas.ax2
        # intialize two line objects (one in each axes)
        line1, = ax1.plot([], [], lw=2)
        line2, = ax2.plot([], [], lw=2, color='r')
        line = [line1, line2]
        self.conn.inst.write("INIT;")
        self.conn.inst.write(":FETCH?;")
        # Read temperature (Celsius) from TMP102
        result = self.conn.inst.read()
        print(result)
        y1_start, y2_start = list(map(lambda x: float(x), result.split(',')[:2]))
        ax1.set_ylim(y1_start - 1, y1_start + 1)
        ax1.set_xlim(0, 10)
        ax1.grid()
        ax2.set_ylim(y2_start - 1, y2_start + 1)
        ax2.set_xlim(0, 10)
        ax2.grid()
        ax1.set_title('Channel 101')
        ax2.set_title('Channel 102')
        ax1.set_xlabel('time (seconds)')
        ax2.set_xlabel('time (seconds)')
        ax1.set_ylabel('Temperature (°C)')
        ax2.set_ylabel('Temperature (°C)')
        # initialize the data arrays
        xdata, y1data, y2data = [], [], []

        def run(data):
            # update the data
            t, y1, y2 = data
            xdata.append(t)
            y1data.append(y1)
            y2data.append(y2)

            # axis limits checking. Same as before, just for both axes
            for ax in [ax1, ax2]:
                xmin, xmax = ax.get_xlim()
                if t >= xmax:
                    ax.set_xlim(xmin, 2 * xmax)
                    ax.figure.canvas.draw()
            ymin, ymax = ax1.get_ylim()
            if y1 >= ymax or y1 <= ymin:
                ax1.set_ylim(min(y1data) - 2, max(y1data) + 2)
                ax1.figure.canvas.draw()
            ymin, ymax = ax2.get_ylim()
            if y2 >= ymax or y2 <= ymin:
                ax2.set_ylim(min(y2data) - 2, max(y2data) + 2)
                ax2.figure.canvas.draw()

            # update the data of both line objects
            line[0].set_data(xdata, y1data)
            line[1].set_data(xdata, y2data)

            return line

        self.ani = animation.FuncAnimation(fig, run, self.data_gen, blit=False, interval=1000 * self.conn.config['delay'],
                                      repeat=False)
        self.ani._start()
        df = Animation.save(data=(xdata, y1data, y2data))
        df.to_excel(f'acquisition.xlsx', sheet_name="acquisition")
"""
