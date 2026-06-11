# main file - run this
import sys
from PyQt6.QtWidgets import QApplication
from logic import AppLogic
from gui import MainWindow
from web_server import start_server

def main():
    start_server()  # start web first
    app_logic = AppLogic()
    qt = QApplication(sys.argv)
    win = MainWindow(app_logic)
    win.show()
    sys.exit(qt.exec())

if __name__ == "__main__":
    main()
