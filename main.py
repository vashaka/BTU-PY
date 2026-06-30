# main file - run this
import sys
from PyQt6.QtWidgets import QApplication
from logic import AppLogic
from gui import MainWindow
from web_server import start_server


def main():
    # იწყება სერვერი
    start_server()
    # სერვერი დაიწყება, შემდეგ გამოიყენება ლოგიკა
    app_logic = AppLogic()
    # გამოიყენება პირდაპირ კონტროლერებზე
    qt = QApplication(sys.argv)
    win = MainWindow(app_logic)
    win.show()
    sys.exit(qt.exec())


if __name__ == "__main__":
    main()
