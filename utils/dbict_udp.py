import socket
from PySide6.QtCore import QThread, Signal

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
    
    message = header + body + [lrc_code, 0x03]
    message = bytearray(message)

    return message

def cal_lrc(msg):

    lrc = 0

    for v in msg:
        lrc ^= v
    
    return lrc

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
                    print(pickle.loads(data))
                else:
                    ...

                if self.enable_send:
                    ...
                    s.sendto()

