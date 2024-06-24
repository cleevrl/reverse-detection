import time
import socket

from PySide6.QtCore import QThread, Signal

def cal_lrc(msg):

    lrc = 0

    for v in msg:
        lrc ^= v
    
    return lrc

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

    finished = Signal()

    def __init__(self):
        super().__init__()

        self.host = '192.168.1.20'
        self.port = 5000

        self.cl = None

    def run(self):

        try:
            self.cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cl.settimeout(5)
            self.cl.connect()
            print(f"TCP connected. ---> {self.host}:{self.port} ")

            while True:
                recv_data = self.cl.recv(1024)
                print(f"{recv_data.decode()}")
                time.sleep(1)
        
        except Exception as e:
            print(f"Exception: {e}")

        finally:
            if self.cl:
                self.cl.close()
            
            self.finished.emit()

    def sendMessage(self, reversed):

        if self.cl:

            self.cl.send(vms_message(reversed))
            print(f"TCP Send ---> Reversed : {reversed}")

        else:
            print("NO TCP socket connected.")