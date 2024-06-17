import socket
from PySide6.QtCore import QThread


class EventHandler(QThread):

    def __init__(self):

        super().__init__()

        self.host = '0.0.0.0'
        self.port = 1234

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.host, self.port))
    

    def run(self):

        while True:

            data, addr = self.udp_socket.recvfrom(1024)
            print(data)