from sys import exit as _exit

from PyQt6.QtWidgets import QApplication

from management.logger.logger import Log
from management.objects.objects_manager import ObjectsManager


class MainClass:

    def __init__(self):

        self.__app = ObjectsManager.create_object(QApplication, [])
        self.__window = ObjectsManager.create_object(MainServerWindow)

    def run(self):

        try:

            _exit(self.__app.exec())

        except SystemExit:
            Log.info("Quitting Application...")

        ObjectsManager.delete_object("MainServerWindow")
        ObjectsManager.delete_object("QApplication")
