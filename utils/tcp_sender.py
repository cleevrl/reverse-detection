import time
import socket

from PySide6.QtCore import QThread

def cal_lrc(msg):

    lrc = 0

    for v in msg:
        lrc ^= v
    
    return lrc


def is_socket_connected(sock):
    
    error = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    
    if error == 0:
        res = True
    else:
        print(f"TCP Conection error : {error}")
        res = False

    return res


def vms_message(reversed):

    device_id = 0x01
    size_high = 0x00
    size_low = 0x08
    op_code = 0x27
    control = 0x80

    if reversed:
        data = 0x01
    else:
        data = 0x00

    header = [0x01, device_id]
    body = [0x02, size_high, size_low, op_code, control, data]
    lrc_code = cal_lrc(body)
    
    #message = header + body + [lrc_code, 0x03]
    message = body + [lrc_code, 0x03]
    message = bytearray(message)

    return message


class TCPThread(QThread):

    def __init__(self):
        super().__init__()

        self.host = '192.168.1.20'
        self.port = 5000

        self.cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cl.settimeout(5)
        self.connect()


    def connect(self):

        try:
            self.cl.connect((self.host, self.port))
            print(f"TCP Socket connected. ---> {self.host}:{self.port}")
            self.connected = True
        except:
            print("TCP Connection Failed.")
            self.connected = False
    
    def run(self):

        while True:

            self.connected = is_socket_connected(self.cl)
            
            if self.connected:    
                print("Waiting message from server ...")
                time.sleep(1)
            else:
                print("Trying to connect TCP server. (Every 5 secs)")
                time.sleep(5)
                self.connect()

    def sendMessage(self, reversed):

        if self.connected:

            self.cl.send(vms_message(reversed))
            print(f"TCP Send ---> Reversed : {reversed}")

        else:
            print("NO TCP socket connected.")