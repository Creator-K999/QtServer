from json import loads

from PyQt6 import uic
from PyQt6.QtCore import QFile
from PyQt6.QtNetwork import QNetworkInterface, QAbstractSocket, QHostAddress, QTcpServer
from PyQt6.QtWidgets import QMainWindow, QTextEdit, QProgressBar, QMessageBox

from management.logger.logger import Log


class MainServerWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.__server = None
        self.__connections = []
        self.__window = uic.loadUi("Dep\\ui\\main_server_window.ui", self)
        self.__text_log = self.findChild(QTextEdit, "textLog")
        self.__recv_progress = self.findChild(QProgressBar, "recvProgress")

        self.__local_ip = MainServerWindow.get_local_ip()
        self.__init_tcp_server()

    @staticmethod
    def get_local_ip():

        try:
            for addr in QNetworkInterface.allAddresses():

                if addr.protocol() == QAbstractSocket.NetworkLayerProtocol.IPv4Protocol \
                        and addr != QHostAddress.SpecialAddress.LocalHost:

                    address = addr.toString()

                    if address[:3] == "192" and address.split('.')[-1] != '1':
                        return address

            return "0.0.0.0"

        except Exception as E:
            Log.exception(E)

    def __init_tcp_server(self):

        self.__server = QTcpServer(self)
        self.__server.newConnection.connect(self.__on_new_connection)
        if not self.__server.listen(QHostAddress(self.__local_ip), 10000):
            self.__text_log.setText(self.__server.errorString())

    def __on_new_connection(self):
        conn = self.__server.nextPendingConnection()
        conn.totalBytesToReceive = 0
        conn.bytesReceived = 0
        conn.readyRead.connect(lambda: self.__on_tcp_server_ready_read(conn))
        conn.disconnected.connect(lambda: self.__on_disconnected(conn))

        self.__text_log.setText(f"Connected with address {conn.peerAddress().toString()}, port {conn.peerPort()}")
        self.__connections.append(conn)

    def __on_disconnected(self, conn):

        self.__text_log.setText(f"Disconnected with address {conn.peerAddress().toString()}, port {conn.peerPort()}")
        conn.close()

    def __on_tcp_server_ready_read(self, conn):

        bytes_size = conn.bytesAvaiable()
        bytes_data = conn.read(bytes_size)

        if conn.totalBytesToReceive == 0:
            dt = loads(bytes_data.decode("utf-8"))
            conn.dt = dt
            conn.totalBytesToReceive = dt["size"]
            conn.toFile = QFile(dt["msg"])

            if self.__is_ready_to_recv_file(dt):
                conn.write(b"ready")

            else:
                conn.write(b"declined")
                conn.close()
                return

            if not conn.toFile.open(QFile.OpenModeFlag.WriteOnly):
                self.__text_log.setText(f"Unable to store file {dt['msg']}:{conn.toFile.errorString()}")
                conn.close()
                return

        else:
            conn.bytesReceived += bytes_size
            conn.toFile.write(bytes_data)
            self.__recv_progress.setValue(int(conn.bytesRecieved / conn.totalBytesToReceive * 100))

        if conn.bytesReceived == conn.totalBytesToReceive:
            conn.toFile.close()
            self.__text_log.setText(f"{conn.dt}")
            conn.close()

    def __is_ready_to_recv_file(self, dt):

        file_size = MainServerWindow.__get_file_size(dt["size"])

        reply = QMessageBox.question(
            self, "Confirmation", f"{dt['from']} is trying to send a doc, confirm ? ({dt['msg']}, {file_size})",
            QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)

        return reply == QMessageBox.StandardButton.Yes

    @staticmethod
    def __get_file_size(size):

        units_list = ["Byte", "KB", "MB", "GB", "TB"]

        i = 0
        while size >= 1024 and i < len(units_list):
            size /= 1024
            i += 1

        return f"{size:.2f} {units_list[i]}"
