import time
from serial import Serial
from PySide6.QtCore import QThread

reset_dict = {
    'Disable' : 0x00,
    '1M' : 0x01,
    '5M' : 0x02,
    '10M' : 0x03,
    '30M' : 0x04,
    '1H' : 0x05,
    'reset' : 0xff
}

def cal_lrc(msg):
    lrc = 0
    for v in msg:
        lrc ^= v
    
    return lrc

def reset_message(frame_cnt, reset_mode):

    header = [0x7E, 0x7E]
    body = [0x06, 0x01, 0x00, frame_cnt, reset_dict[reset_mode]]
    lrc_code = cal_lrc(body)

    msg_list = header + body + [lrc_code, 0x7F]
    # print(msg_list)

    return bytes(msg_list)

class SerialBroker(QThread):

    def __init__(self):

        super().__init__()
        self.frame_cnt = 0
        self.reset_mode = '1H'

        self.connect()


    def run(self):

        while True:

            if self.connected:
                self.ser.write(reset_message(self.frame_cnt, self.reset_mode))
                self.frame_up_count()
                time.sleep(0.1)

                if self.ser.in_waiting > 0:
                    recv_data = self.ser.read(10)   

                # print(recv_data)

            else:
                print("Trying to connect Serial Port. (Every 5 secs)")
                time.sleep(5)
                self.connect()

    def frame_up_count(self):
        self.frame_cnt = self.frame_cnt + 1
        if self.frame_cnt == 256:
            self.frame_cnt = 0

    def connect(self):

        try:
            self.ser = Serial("/dev/ttyTHS1", baudrate=115200)
            self.connected = True
        except:
            print("Serial connection Failed.")
            self.connected = False
