from sys import exit as _exit

from PyQt6.QtWidgets import QApplication

from management.logger.logger import Log
from management.objects.objects_manager import ObjectsManager
from source.window.main_server_controller import MainServerWindow


class MainClass:

    def __init__(self):

        self.__app = ObjectsManager.create_object(QApplication, [])
        self.__window = ObjectsManager.create_object(MainServerWindow)

    def run(self):

        try:

            self.__window.show()
            _exit(self.__app.exec())

        except SystemExit:
            Log.info("Quitting Application...")

        ObjectsManager.delete_object("MainServerWindow")
        ObjectsManager.delete_object("QApplication")
