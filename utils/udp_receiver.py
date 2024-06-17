import socket
from PySide6.QtCore import QThread, Signal


class UDPThread(QThread):

    def __init__(self):
        super().__init__()
        self.enable_recv = False
        self.enable_send = False

        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def run(self):

        host = '0.0.0.0'
        port = 1234
        udp_message_received = Signal(str)

        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

            s.bind((host, port))

            while True:
                
                if self.enable_recv:
                    data, addr = s.recvfrom(1024)
                else:
                    ...

                if self.enable_send:
                    ...
                    s.sendto()

