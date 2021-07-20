from gui_preprod import Ui_MainWindow
import sys
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow(MainWindow)
MainWindow.show()
ui.ask_load_config()
sys.exit(app.exec_())

