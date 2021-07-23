from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem,QHeaderView
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np

class TableWindow(object):
    def __init__(self, MainWindow, sensors=None):
        self.sensors = sensors
        self.win = MainWindow
        self.win.setFixedSize(1400, 1000)
        self.tableWidget = QTableWidget(parent=self.win)
        self.tableWidget.sizePolicy().setVerticalPolicy(QSizePolicy.Expanding)
        self.tableWidget.sizePolicy().setHorizontalPolicy(QSizePolicy.Expanding)
        self.tableWidget.sizePolicy().setHorizontalPolicy(QSizePolicy.Expanding)
        self.tableWidget.setMinimumWidth(1400)
        self.tableWidget.setMinimumHeight(1000)
        self.tableWidget.setColumnCount(len(self.sensors) + 1)
        self.tableWidget.setRowCount(1)
        time_item = QTableWidgetItem("time")
        time_item.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(0, 0, time_item)
        for i in range(len(self.sensors)):
            item = QTableWidgetItem(self.sensors[i][0] + " @" + self.sensors[i][1])
            item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(0, i + 1, item)

        header = self.tableWidget.horizontalHeader()
        for i in range(len(self.sensors)+1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def append_row(self,data):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        time = QTableWidgetItem(str(np.round(data[0][0][-1],2)))
        time.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(rowPosition, 0, time)
        for i in range(len(self.sensors)):
            value = QTableWidgetItem(str(np.round(data[i][1][-1],2)))
            value.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(rowPosition, i+1, value)