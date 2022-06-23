from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow


class MainServerWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.__window = uic.loadUi("path")
