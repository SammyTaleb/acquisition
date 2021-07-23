# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from acquisition_module.acquisition import Connection, MyMplCanvas, Ui_OtherWindow
import logging, json, time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.INFO)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)

    def log(self, msg, func):
        func(msg)


class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        self.sensor_limit = True
        self.sensors = {"sensors": [], "sensor_labels": [], "channels": [], "channel_labels": []}
        self.config = {}
        self.palette_text_color = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(102, 0, 51))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.palette_text_color.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        self.font = QtGui.QFont()
        self.font.setFamily("Sitka Subheading")
        self.checkbox_style_sheet = self.get_style_sheet('checkbox')
        self.label_style_sheet = self.get_style_sheet('label')
        self.combobox_style_sheet = self.get_style_sheet('combobox')
        self.push_button_style_sheet = self.get_style_sheet('push_button')
        self.spinbox_style_sheet = self.get_style_sheet('spinbox')
        self.setupUi(MainWindow)

    def remove_sensor(self):
        if len(self.sensors['sensor_labels']) == 0:
            self.critical_message("There is no sensor anymore !")
        else:
            self.gridLayout_2.removeWidget(self.sensors['sensor_labels'][-1])
            self.sensors['sensor_labels'][-1].deleteLater()
            self.sensors['sensor_labels'] = self.sensors['sensor_labels'][:-1]
            self.gridLayout_2.removeWidget(self.sensors['sensors'][-1])
            self.sensors['sensors'][-1].deleteLater()
            self.sensors['sensors'] = self.sensors['sensors'][:-1]
            self.gridLayout_2.removeWidget(self.sensors['channel_labels'][-1])
            self.sensors['channel_labels'][-1].deleteLater()
            self.sensors['channel_labels'] = self.sensors['channel_labels'][:-1]
            self.gridLayout_2.removeWidget(self.sensors['channels'][-1])
            self.sensors['channels'][-1].deleteLater()
            self.sensors['channels'] = self.sensors['channels'][:-1]

    def add_sensor_decorator(self, func):
        def run():
            func()

        return run

    def add_sensor(self, sensor='TC', channel='101'):
        if len(self.sensors['sensor_labels']) >= 6 and self.sensor_limit:
            msgbox = QMessageBox(QMessageBox.Question, "Sensors Limit Reached",
                                 "More than six sensors have been registered, press yes to remove the sensor number limit. ?")
            msgbox.addButton(QMessageBox.Yes)
            msgbox.addButton(QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                self.sensor_limit = False
        else:
            self.font.setPointSize(12)
            labels = []
            for i in range(2):
                label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
                label.setPalette(self.palette_text_color)
                label.setFont(self.font)
                label.setStyleSheet(self.label_style_sheet)
                label.setAlignment(QtCore.Qt.AlignCenter)
                labels.append(label)
            labels[0].setText("Sensor")
            labels[1].setText("Channel")

            combo_sensor = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
            combo_sensor.setFont(self.font)
            combo_sensor.setStyleSheet(self.combobox_style_sheet)
            for i in ['TC', 'Temp K', 'Temp L', 'Pressure']:
                combo_sensor.addItem(i)

            combo_channel = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
            combo_channel.setFont(self.font)
            combo_channel.setStyleSheet(self.combobox_style_sheet)
            for i in ['101', '102', '103', '201', '202', '203']:
                combo_channel.addItem(i)

            index = combo_channel.findText(channel, QtCore.Qt.MatchFixedString)
            if index >= 0:
                combo_channel.setCurrentIndex(index)
            index = combo_sensor.findText(sensor, QtCore.Qt.MatchFixedString)
            if index >= 0:
                combo_sensor.setCurrentIndex(index)

            self.sensors['sensor_labels'].append(labels[0])
            self.sensors['channel_labels'].append(labels[1])
            self.sensors['sensors'].append(combo_sensor)
            self.sensors['channels'].append(combo_channel)

            self.gridLayout_2.addWidget(self.sensors['sensor_labels'][-1], len(self.sensors['sensor_labels']), 0, 1, 1)
            self.gridLayout_2.addWidget(self.sensors['sensors'][-1], len(self.sensors['sensors']), 1, 1, 1)
            self.gridLayout_2.addWidget(self.sensors['channel_labels'][-1], len(self.sensors['channel_labels']), 2, 1,
                                        1)
            self.gridLayout_2.addWidget(self.sensors['channels'][-1], len(self.sensors['channels']), 3, 1, 1)

    def get_sensors_configuration(self):
        self.dialog.log('Started Sensors configuration', logging.info)
        if len(self.sensors['sensor_labels']) == 0:
            self.critical_message("There is no sensor to configure !")
            self.dialog.log('Sensors configuration failed : No sensor to configure', logging.error)
            return
        dict_sensors = {
            'sensors': list(map(lambda x: str(x.currentText()), self.sensors['sensors'])),
            'channels': list(map(lambda x: str(x.currentText()), self.sensors['channels']))
        }
        if len(set(dict_sensors['channels'])) < len(dict_sensors['channels']):
            self.critical_message("A channel has been attributed twice !")
            self.dialog.log('Sensors configuration failed : A channel has been attributed twice', logging.error)
            return
        else:
            self.config['sensors'] = list(zip(dict_sensors['sensors'], dict_sensors['channels']))
            self.dialog.log('Sensors configuration ended successfully', logging.info)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Sensors configuration saved")
            msg.setWindowTitle("Saved")
            msg.exec_()

    def get_measure_configuration(self):
        # scans
        self.dialog.log('Started measures configuration', logging.info)
        if self.radio_infinite.isChecked():
            self.config['scans'] = 'infinite'
        elif self.radio_finite.isChecked():
            if self.spinbox_nbr_scan.value() == 0:
                self.critical_message("The number of scans cannot be null")
                self.dialog.log('Number of scans configuration failed : null number of scans', logging.error)
                return
            self.config['scans'] = self.spinbox_nbr_scan.value()
        else:
            self.critical_message("The number of scans have not been properly set")
            self.dialog.log('Number of scans configuration failed : number of scans not properly set', logging.error)
            return
        # delay
        if self.spin_delay_value.value() == 0:
            self.critical_message("The delay between scans cannot be null")
            self.dialog.log('Delay configuration failed: null delay', logging.error)
            return
        self.config['delay'] = self.spin_delay_value.value()
        # filename
        if self.csv_file.isChecked():
            self.config['file'] = {'type': 'csv'}
        elif self.xlsx_file.isChecked():
            self.config['file'] = {'type': 'xlsx'}
        else:
            self.critical_message("A file type should be selected")
            self.dialog.log('Filename configuration failed: no filetype selected', logging.error)
            return
        if self.filename_input.text() == '':
            self.critical_message("The filename cannot be null")
            self.dialog.log('Filename configuration failed: no filename provided', logging.error)
            return

        self.config['file']['filename'] = self.filename_input.text()
        self.dialog.log('Measure configuration done successfully', logging.info)
        if self.save_check.isChecked():
            with open('data/config/settings_config.json', 'w') as f:
                json.dump(self.config, f)

            self.dialog.log('Configuration saved for future starts', logging.info)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Measures configuration saved")
        msg.setWindowTitle("Saved")
        msg.exec_()

    @staticmethod
    def critical_message(text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.exec_()

    @staticmethod
    def get_style_sheet(name: str):
        with open(f'data/style_sheets/{name}_style_sheet.txt', 'r') as file:
            sheet = file.read()
        return sheet

    def ask_load_config(self):
        time.sleep(0.5)
        msgbox = QMessageBox(QMessageBox.Question, "Load Configuration",
                             "Do you want to load the previous configuration ?")
        msgbox.addButton(QMessageBox.Yes)
        msgbox.addButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.No)
        reply = msgbox.exec()
        if reply == QMessageBox.Yes:
            self.load_config()
        print(self.config)

    def apply_loaded_configuration(self):
        # sensors:
        for i in range(3):
            self.remove_sensor()

        for couple in self.config['sensors']:
            self.add_sensor(sensor=couple[0], channel=couple[1])
        # scans
        if self.config['scans'] == 'infinite':
            self.radio_infinite.setChecked(True)
        else:
            self.radio_finite.setChecked(True)
            self.spinbox_nbr_scan.setValue(self.config['scans'])
        # delay
        self.spin_delay_value.setValue(self.config['delay'])
        # file
        if self.config['file']['type'] == 'csv':
            self.csv_file.setChecked(True)
        else:
            self.xlsx_file.setChecked(True)
        self.filename_input.setText(self.config['file']['filename'])

    def load_config(self):
        try:
            with open('data/config/settings_config.json', 'r') as f:
                self.config = json.load(f)
            self.dialog.log('Loaded previous configuration', logging.info)
            self.apply_loaded_configuration()
        except FileNotFoundError:
            self.critical_message("There is no previous configuration available")

    def start_acquisition(self):
        text = f"Sensors:\n"
        for value in self.config['sensors']:
            text += f"- {value[0]} on channel @{value[1]}\n"
        text += f"\nNumber of scans: {self.config['scans']}\n\nDelay between scans: {self.config['delay']} seconds\n\n"
        text += f"Saving in data/save/{self.config['file']['filename']}.{self.config['file']['type']}"
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Start Measure")
        msg.setText("Do you want to start the measure ?")
        msg.setDetailedText(text)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.setStyleSheet("QPushButton{ width:120px;}");
        details = msg.buttons()[1]
        details.click()
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            """
            self.otherwindow = QtWidgets.QMainWindow()
            conn = Connection(self.dialog, self.config)
            QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
            self.ui_canvas = Ui_OtherWindow(self.otherwindow, self.config, conn, self.push_button_style_sheet)
            self.otherwindow.show()
            """
            try:
                conn = Connection(self.dialog, self.config)
                QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
                self.ui_canvas = Ui_OtherWindow(self.otherwindow, self.config, conn, self.push_button_style_sheet)
                self.otherwindow.show()
            except TimeoutError as exc:
                self.critical_message(str(exc))

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1213, 1018)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setPalette(self.palette_text_color)
        self.font.setPointSize(14)
        self.font.setBold(True)
        self.font.setWeight(75)
        self.label_title.setFont(self.font)
        self.label_title.setFrameShape(QtWidgets.QFrame.Box)
        self.label_title.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_title.setLineWidth(3)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label_title)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.frame_sensors = QtWidgets.QFrame(self.widget)
        self.frame_sensors.setPalette(self.palette_text_color)

        self.font.setPointSize(8)
        self.frame_sensors.setFont(self.font)
        self.frame_sensors.setStyleSheet("background-color: #eeeeee")
        self.frame_sensors.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_sensors.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_sensors.setLineWidth(5)
        self.frame_sensors.setMidLineWidth(0)
        self.gridLayout = QtWidgets.QGridLayout(self.frame_sensors)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setSpacing(10)
        self.label_sensor_title = QtWidgets.QLabel(self.frame_sensors)
        self.label_sensor_title.setPalette(self.palette_text_color)
        self.font.setPointSize(12)
        self.label_sensor_title.setFont(self.font)
        self.label_sensor_title.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_sensor_title, 0, 0, 1, 2)
        self.scroll_sensors = QtWidgets.QScrollArea(self.frame_sensors)
        self.scroll_sensors.setStyleSheet("""
            border: 1px solid #660033;
            border-radius: 5px;
        """)
        self.scroll_sensors.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 951, 189))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)

        for i in range(3):
            self.add_sensor()

        self.scroll_sensors.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scroll_sensors, 1, 0, 1, 1)
        self.group_right = QtWidgets.QGroupBox(self.frame_sensors)
        self.font.setPointSize(8)
        self.group_right.setFont(self.font)
        self.group_right.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.group_right.setStyleSheet("""
            border: 2px solid #660033;
            border-radius: 5px;
        """)
        self.group_right.setInputMethodHints(QtCore.Qt.ImhNone)
        self.group_right.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_7 = QtWidgets.QGridLayout(self.group_right)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem1, 0, 3, 1, 1)

        self.button_add_sensor = QtWidgets.QPushButton(self.group_right)
        self.button_add_sensor.setStyleSheet(self.push_button_style_sheet)
        self.button_add_sensor.clicked.connect(self.add_sensor_decorator(self.add_sensor))
        self.gridLayout_7.addWidget(self.button_add_sensor, 0, 1, 1, 1)

        self.button_remove_sensor = QtWidgets.QPushButton(self.group_right)
        self.button_remove_sensor.setStyleSheet(self.push_button_style_sheet)
        self.button_remove_sensor.clicked.connect(self.remove_sensor)
        self.gridLayout_7.addWidget(self.button_remove_sensor, 1, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem2, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.group_right, 1, 1, 1, 1)
        self.grid_bottom_sensors = QtWidgets.QGridLayout()
        self.button_save_sensor = QtWidgets.QPushButton(self.frame_sensors)
        self.button_save_sensor.setMinimumSize(QtCore.QSize(84, 0))
        self.button_save_sensor.setMaximumSize(QtCore.QSize(300, 16777215))
        self.font.setPointSize(10)
        self.button_save_sensor.setFont(self.font)
        self.button_save_sensor.setStyleSheet(self.push_button_style_sheet)
        self.button_save_sensor.clicked.connect(self.get_sensors_configuration)
        self.grid_bottom_sensors.addWidget(self.button_save_sensor, 1, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(300, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.grid_bottom_sensors.addItem(spacerItem3, 1, 2, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(300, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.grid_bottom_sensors.addItem(spacerItem4, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.grid_bottom_sensors, 2, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.frame_sensors)
        spacerItem5 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem5)
        self.frame_measure = QtWidgets.QFrame(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_measure.sizePolicy().hasHeightForWidth())
        self.frame_measure.setSizePolicy(sizePolicy)
        self.font.setPointSize(12)
        self.frame_measure.setFont(self.font)
        self.frame_measure.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_measure.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_measure.setLineWidth(5)
        self.gridLayout_8 = QtWidgets.QGridLayout(self.frame_measure)
        self.gridLayout_8.setContentsMargins(10, 10, 10, 10)
        self.label_measure_title = QtWidgets.QLabel(self.frame_measure)
        self.label_measure_title.setPalette(self.palette_text_color)
        self.label_measure_title.setFont(self.font)
        self.label_measure_title.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_8.addWidget(self.label_measure_title, 0, 0, 1, 1)
        self.grid_button = QtWidgets.QGridLayout()
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.grid_button.addItem(spacerItem6, 0, 0, 1, 1)
        self.button_save_measure = QtWidgets.QPushButton(self.frame_measure)
        self.button_save_measure.setMaximumSize(QtCore.QSize(300, 16777215))
        self.font.setPointSize(10)
        self.button_save_measure.setFont(self.font)
        self.button_save_measure.setStyleSheet(self.push_button_style_sheet)
        self.button_save_measure.clicked.connect(self.get_measure_configuration)
        self.grid_button.addWidget(self.button_save_measure, 0, 1, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.grid_button.addItem(spacerItem7, 0, 2, 1, 1)
        self.gridLayout_8.addLayout(self.grid_button, 2, 0, 1, 1)
        self.scroll_measure = QtWidgets.QScrollArea(self.frame_measure)
        self.scroll_measure.setStyleSheet("""
            border: 1px solid #660033;
            border-radius: 5px;
            """)
        self.scroll_measure.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 1139, 189))
        self.gridLayout_5 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_3)

        self.line_1 = QtWidgets.QFrame(self.scrollAreaWidgetContents_3)
        self.line_1.setStyleSheet("""
            background-color: #660033;
            border: 1px;
            """)
        self.line_1.setLineWidth(1)
        self.line_1.setFrameShape(QtWidgets.QFrame.VLine)
        self.gridLayout_5.addWidget(self.line_1, 1, 1, 2, 1)
        self.line_2 = QtWidgets.QFrame(self.scrollAreaWidgetContents_3)
        self.line_2.setStyleSheet("""
            background-color: #660033;
            border: 1px;
            """)
        self.line_2.setLineWidth(1)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.gridLayout_5.addWidget(self.line_2, 1, 3, 2, 1)
        self.grid_scans_2 = QtWidgets.QGridLayout()
        self.grid_scans_2.setContentsMargins(0, -1, -1, -1)
        self.radio_finite = QtWidgets.QRadioButton(self.scrollAreaWidgetContents_3)
        self.radio_finite.setStyleSheet(self.label_style_sheet)

        self.grid_scans_2.addWidget(self.radio_finite, 0, 0, 1, 1)

        self.radio_infinite = QtWidgets.QRadioButton(self.scrollAreaWidgetContents_3)
        self.radio_infinite.setStyleSheet(self.label_style_sheet)
        nbr_scans_group = QtWidgets.QButtonGroup(self.scrollAreaWidgetContents_3)
        nbr_scans_group.addButton(self.radio_infinite)
        nbr_scans_group.addButton(self.radio_finite)

        self.grid_scans_2.addWidget(self.radio_infinite, 2, 0, 1, 1)
        self.spinbox_nbr_scan = QtWidgets.QSpinBox(self.scrollAreaWidgetContents_3)
        self.spinbox_nbr_scan.setStyleSheet(self.spinbox_style_sheet)
        self.spinbox_nbr_scan.setMaximum(10000)

        self.grid_scans_2.addWidget(self.spinbox_nbr_scan, 1, 0, 1, 1)
        self.gridLayout_5.addLayout(self.grid_scans_2, 2, 0, 1, 1)
        self.grid_delay_1 = QtWidgets.QGridLayout()
        self.label_delay_title = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_delay_title.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_delay_title.sizePolicy().hasHeightForWidth())
        self.label_delay_title.setSizePolicy(sizePolicy)
        self.label_delay_title.setMaximumSize(QtCore.QSize(1000, 50))
        self.label_delay_title.setPalette(self.palette_text_color)
        self.font.setPointSize(10)
        self.label_delay_title.setFont(self.font)
        self.label_delay_title.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_delay_title.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_delay_title.setLineWidth(10)
        self.label_delay_title.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_delay_1.addWidget(self.label_delay_title, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.grid_delay_1, 1, 2, 1, 1)
        self.grid_scans_1 = QtWidgets.QGridLayout()
        self.grid_scans_1.setContentsMargins(0, 0, 0, 0)
        self.label_scans_title = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_scans_title.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_scans_title.sizePolicy().hasHeightForWidth())
        self.label_scans_title.setSizePolicy(sizePolicy)
        self.label_scans_title.setMaximumSize(QtCore.QSize(10000, 50))
        self.label_scans_title.setPalette(self.palette_text_color)
        self.label_scans_title.setFont(self.font)
        self.label_scans_title.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_scans_title.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_scans_title.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_scans_1.addWidget(self.label_scans_title, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.grid_scans_1, 1, 0, 1, 1)
        self.grid_save_1 = QtWidgets.QGridLayout()
        self.label_save_title = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_save_title.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_save_title.sizePolicy().hasHeightForWidth())
        self.label_save_title.setSizePolicy(sizePolicy)
        self.label_save_title.setMaximumSize(QtCore.QSize(1000, 50))
        self.label_save_title.setPalette(self.palette_text_color)
        self.label_save_title.setFont(self.font)
        self.label_save_title.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_save_title.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_save_title.setLineWidth(10)
        self.label_save_title.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_save_1.addWidget(self.label_save_title, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.grid_save_1, 1, 4, 1, 1)
        self.grid_delay_2 = QtWidgets.QGridLayout()
        self.grid_delay_2.setContentsMargins(0, -1, -1, -1)
        self.spin_delay_value = QtWidgets.QDoubleSpinBox(self.scrollAreaWidgetContents_3)
        self.spin_delay_value.setStyleSheet(self.spinbox_style_sheet)
        self.spin_delay_value.setMaximum(10000)
        self.grid_delay_2.addWidget(self.spin_delay_value, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.grid_delay_2, 2, 2, 1, 1)
        self.grid_save_2 = QtWidgets.QGridLayout()
        self.filename_input = QtWidgets.QLineEdit(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filename_input.sizePolicy().hasHeightForWidth())
        self.filename_input.setSizePolicy(sizePolicy)
        self.grid_save_2.addWidget(self.filename_input, 0, 0, 1, 1)
        self.save_check = QtWidgets.QCheckBox("Save Configuration")
        self.save_check.setToolTip('Check this box to save this configuration and load it later.')
        self.save_check.setChecked(False)
        self.save_check.setStyleSheet(self.checkbox_style_sheet)
        self.grid_save_2.addWidget(self.save_check, 1, 0, 1, 2)
        self.vertical_layour_radio_save = QtWidgets.QVBoxLayout()
        self.csv_file = QtWidgets.QRadioButton(self.scrollAreaWidgetContents_3)
        self.csv_file.setStyleSheet(self.label_style_sheet)
        self.csv_file.setObjectName('file')
        self.vertical_layour_radio_save.addWidget(self.csv_file)
        self.xlsx_file = QtWidgets.QRadioButton(self.scrollAreaWidgetContents_3)
        self.xlsx_file.setStyleSheet(self.label_style_sheet)
        file_group = QtWidgets.QButtonGroup(self.scrollAreaWidgetContents_3)
        file_group.addButton(self.csv_file)
        file_group.addButton(self.xlsx_file)
        self.vertical_layour_radio_save.addWidget(self.xlsx_file)
        self.grid_save_2.addLayout(self.vertical_layour_radio_save, 0, 1, 1, 1)
        self.gridLayout_5.addLayout(self.grid_save_2, 2, 4, 1, 1)
        self.scroll_measure.setWidget(self.scrollAreaWidgetContents_3)
        self.gridLayout_8.addWidget(self.scroll_measure, 1, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.frame_measure)
        self.frame_buttons = QtWidgets.QFrame(self.widget)
        self.frame_buttons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_buttons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout_9 = QtWidgets.QGridLayout(self.frame_buttons)
        spacerItem9 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem9, 1, 4, 1, 1)
        self.button_start = QtWidgets.QPushButton(self.frame_buttons)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_start.sizePolicy().hasHeightForWidth())
        self.button_start.setSizePolicy(sizePolicy)
        self.button_start.setMinimumSize(QtCore.QSize(86, 50))
        self.button_start.setStyleSheet(self.push_button_style_sheet)
        self.button_start.clicked.connect(self.start_acquisition)
        self.gridLayout_9.addWidget(self.button_start, 1, 1, 1, 1)
        spacerItem12 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem12, 1, 6, 1, 1)
        self.verticalLayout_2.addWidget(self.frame_buttons)
        self.verticalLayout.addWidget(self.widget)
        self.dialog = MyDialog()
        self.dialog.setFixedHeight(150)
        self.verticalLayout.addWidget(self.dialog)
        self.dialog.log('Welcome to this acquisition_module platform', logging.info)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1213, 26))
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.menuFile.addAction(self.actionExit)
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.dialog.log('Widgets have been created', logging.info)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_title.setText(_translate("MainWindow", "ACQUISITION PLATFORM"))
        self.label_sensor_title.setText(_translate("MainWindow", "Sensors Settings"))
        self.button_add_sensor.setText(_translate("MainWindow", "Add sensor"))
        self.button_remove_sensor.setText(_translate("MainWindow", " Remove sensor "))
        self.button_save_sensor.setText(_translate("MainWindow", "Save sensors\' configuration"))
        self.label_measure_title.setText(_translate("MainWindow", "Measurement Settings"))
        self.button_save_measure.setText(_translate("MainWindow", "Save measures\' configuration"))
        self.radio_finite.setText(_translate("MainWindow", "Finite"))
        self.radio_infinite.setText(_translate("MainWindow", "Infinite"))
        self.label_delay_title.setText(_translate("MainWindow", "Delay between scans (sec)"))
        self.label_scans_title.setText(_translate("MainWindow", "Number of scans"))
        self.label_save_title.setText(_translate("MainWindow", "Save"))
        self.filename_input.setPlaceholderText(_translate("MainWindow", "file_name"))
        self.csv_file.setText(_translate("MainWindow", ".csv"))
        self.xlsx_file.setText(_translate("MainWindow", ".xlsx"))
        self.button_start.setText(_translate("MainWindow", "START"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
