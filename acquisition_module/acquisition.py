import pyvisa
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import time
import seaborn as sns
import numpy as np
import pandas as pd
import os
import datetime

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class Connection:
    def __init__(self, _logger, _config):
        self.logger = _logger
        self.config = _config
        self.logger.log('Opened a new connection instance', logging.info)
        try:
            self.rm = pyvisa.ResourceManager()
            self.logger.log('ressource manager created', logging.info)

            self.inst = self.rm.open_resource(self.rm.list_resources()[0])
            time.sleep(1)
            device = self.inst.query("*IDN?")
            self.logger.log(f"Connected to , {device.split(',')[0]} {device.split(',')[1]}", logging.info)
            self.configure()
        except Exception as e:
            self.logger.log('Connection Failed', logging.error)
            # raise TimeoutError('Device is not found')

    def configure(self):
        """
        configure the acquisition_module measures
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
        self.inst.write("ROUTE:SCAN " + scan_list)
        self.logger.log('Configuration is done', logging.info)


class MyMplCanvas(FigureCanvas, TimedAnimation):
    def __init__(self, parent=None, config=None, conn=None,table_window=None):
        self.table_window = table_window
        #self.table_window.win.show()
        self.config = config
        self.conn = conn
        self.fig = Figure(figsize=(15, 10), dpi=100)
        self.axes = []
        self.lines = []
        self.create_axes()
        self.data_final = {}
        for i in self.config['sensors']:
            self.data_final[f'time_{i[0]}_{i[1]}'] = []
            self.data_final[f'value_{i[0]}_{i[1]}'] = []
        self.data = [[[], []] for i in range(len(self.axes))]
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=1000 * self.config['delay'], repeat=False)
        self.setParent(parent)
        self.start = time.time()
        self.filename = self.config["file"]
        try:
            with open(self.filename) as f:
                pass
            dummy = self.filename.split('.')
            self.filename = dummy[0]+f'-{datetime.datetime.now().strftime("%d-%m-%Y--%Hh%M")}.'+dummy[1]
        except IOError:
            pass

    def create_axes(self):
        nbr = len(self.config['sensors'])
        color_palette = list(sns.color_palette(None, nbr))
        val = str(nbr) + "1"
        for i in range(nbr):
            print(int(val + str(i + 1)))
            ax = self.fig.add_subplot(int(val + str(i + 1)))
            ax.set_xlabel('time')
            ax.set_ylabel(self.config['sensors'][i][0] + " @" + self.config['sensors'][i][1])
            ax.set_xlim(0, 20)
            ax.set_ylim(-5, 5)
            line = Line2D([], [], color=color_palette[i])
            ax.add_line(line)
            self.lines.append(line)
            self.axes.append(ax)

    def data_gen(self):
        t = time.time() - self.start
        # self.conn.inst.write("INIT;")
        # self.conn.inst.write(":FETCH?;")
        # result=self.conn.inst.read()
        result = str(np.random.random() * 20) + "," + str(np.random.random() * 40) + "," + str(np.random.random() * 30)
        y = result.split(',')[:len(self.axes)]
        for i, val in enumerate(self.config['sensors']):
            self.data[i][0].append(t)
            self.data_final[f'time_{val[0]}_{val[1]}'].append(t)
            self.data[i][1].append(val[2][1]*float(y[i])+val[2][0])
            self.data_final[f'value_{val[0]}_{val[1]}'].append(val[2][1]*float(y[i])+val[2][0])
        self.save()
        self.table_window.add_row(self.data)

    def _draw_frame(self, framedata):
        i = framedata
        self.data_gen()
        for i in range(len(self.lines)):
            self.lines[i].set_data(self.data[i][0], self.data[i][1])
            # Auto scale X_lim up
            if max(self.data[i][0]) > self.axes[i].get_xlim()[1] - 5:
                self.axes[i].set_xlim(0, max(self.data[i][0]) + 10)
            # Auto Scale y_lim up
            if max(self.data[i][1]) > self.axes[i].get_ylim()[1] - 5:
                self.axes[i].set_ylim(self.axes[i].get_ylim()[0], max(self.data[i][1]) + 2)
            if min(self.data[i][1]) < self.axes[i].get_ylim()[0] + 5:
                self.axes[i].set_ylim(min(self.data[i][1]) - 2, self.axes[i].get_ylim()[1])
        self._drawn_artists = self.lines

    def save(self):
        data = pd.DataFrame(self.data_final)
        if self.filename.endswith('csv'):
            data.to_csv(self.filename)
        else:
            data.to_excel(self.filename)

    def new_frame_seq(self):
        return iter(range(self.config['scans']))

    def _init_draw(self):
        for line in self.lines:
            line.set_data([], [])


class Ui_Table_Window(object):
    def __init__(self, MainWindow, sensors_config):
        self.sensors = sensors_config
        self.win = MainWindow
        self.win.setWindowTitle("Real Time Table")
        self.win.resize(1413, 1018)
        self.table = QTableWidget(self.win)
        self.table.setFixedWidth(1413)
        self.table.setFixedHeight(1018)
        self.table.setColumnCount(len(self.sensors)+1)
        self.table.setRowCount(0)
        header = self.table.horizontalHeader()
        for i in range(len(self.sensors)+1):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        self.add_row([(["Time"],[self.sensors[i][0]+" @"+self.sensors[i][1]]) for i in range(len(self.sensors))],False)

    def add_row(self,data,is_numeric=True):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        if is_numeric :
            item = QTableWidgetItem(str(np.round(data[0][0][-1],2)))
        else:
            item = QTableWidgetItem(str(data[0][0][-1]))
        item.setTextAlignment(Qt.AlignHCenter)
        self.table.setItem(row_count,0,item)
        for i in range(len(self.sensors)):
            if is_numeric:
                item = QTableWidgetItem(str(np.round(data[i][1][-1],2)))
            else:
                item = QTableWidgetItem(str(data[i][1][-1]))
            item.setTextAlignment(Qt.AlignHCenter)
            self.table.setItem(row_count, i+1, item)


class Ui_OtherWindow(object):
    def __init__(self, MainWindow, config, conn, style,ui_table_window):
        self.config = config
        self.sensors = self.config['sensors']
        self.conn = conn
        self.style = style
        self.win = MainWindow
        self.win.setWindowTitle("Real Time Plot")
        self.win.resize(1413, 1018)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.table = QTableWidget(self.win)
        self.table.setColumnCount(len(self.sensors) + 1)
        self.table.setRowCount(0)
        self.table.setMinimumWidth(500)
        header = self.table.horizontalHeader()
        for i in range(len(self.sensors) + 1):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.add_row([(["Time"], [self.sensors[i][0] + " @" + self.sensors[i][1]]) for i in range(len(self.sensors))],
                     False)
        font = QtGui.QFont()
        font.setBold(True)
        for i in range(len(self.sensors)+1):
            self.table.item(0, i).setFont(font)
        self.mplCanvas_widget = MyMplCanvas(self.win, config=self.config, conn=self.conn, table_window=self)
        self.gridLayout_2.addWidget(self.table, 1, 0, 1, 3)
        self.gridLayout_2.addWidget(self.mplCanvas_widget, 0, 3, 2, 2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.button_start = QtWidgets.QPushButton('RUNNING')
        self.button_start.setStyleSheet(style)
        self.gridLayout_2.addWidget(self.button_start,0,0,1,1)
        self.button_start.setDisabled(True)
        self.button_stop = QtWidgets.QPushButton('STOP')
        self.button_stop.setStyleSheet(style)
        self.gridLayout_2.addWidget(self.button_stop,0,1,1,1)
        self.button_pause = QtWidgets.QPushButton('PAUSE')
        self.button_pause.setStyleSheet(style)
        self.gridLayout_2.addWidget(self.button_pause, 0, 2, 1, 1)
        self.button_pause.clicked.connect(self.pause)
        self.button_stop.clicked.connect(self.stop)
        self.button_start.clicked.connect(self.start)
        self.filename = self.mplCanvas_widget.filename
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def stop(self):
        data = pd.DataFrame(self.mplCanvas_widget.data_final)
        if self.filename.endswith('csv'):
            data.to_csv(self.filename)
        else:
            data.to_excel(self.filename)
        self.mplCanvas_widget.pause()
        self.button_start.deleteLater()
        self.button_pause.deleteLater()
        self.button_stop.deleteLater()
        self.table.deleteLater()
        os.startfile(self.filename)

    def pause(self):
        self.mplCanvas_widget.pause()
        self.button_start.setDisabled(False)
        self.button_start.setText('RESUME')
        self.button_pause.setDisabled(True)
        self.button_pause.setText('PAUSED')

    def start(self):
        self.button_start.setText('RUNNING')
        self.button_pause.setText('PAUSE')
        self.button_start.setDisabled(True)
        self.button_pause.setDisabled(False)
        self.mplCanvas_widget.resume()

    def add_row(self,data,is_numeric=True):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        if is_numeric :
            item = QTableWidgetItem(str(np.round(data[0][0][-1],2)))
        else:
            item = QTableWidgetItem(str(data[0][0][-1]))
        item.setTextAlignment(Qt.AlignHCenter)
        self.table.setItem(row_count,0,item)
        for i in range(len(self.sensors)):
            if is_numeric:
                item = QTableWidgetItem(str(np.round(data[i][1][-1],2)))
            else:
                item = QTableWidgetItem(str(data[i][1][-1]))
            item.setTextAlignment(Qt.AlignHCenter)
            self.table.setItem(row_count, i+1, item)
