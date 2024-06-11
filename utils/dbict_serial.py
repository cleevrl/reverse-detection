import time
from serial import Serial

def cal_lrc(msg):
    lrc = 0
    for v in msg:
        lrc ^= msg
    
    return lrc

def run_serial():

    frame_num = 0
    ser = Serial("/dev/ttyTHS0", baudrate=115200)

    header = [0x7E, 0x7E]
    msg_info = [10, 1, 0x00, frame_num]
    status_code = [0x00, 0x00, 0x00 ,0x00, 0x00]
    data_array = msg_info + status_code
    lrc_code = cal_lrc(data_array)
    send_array = header + data_array + [lrc_code, 0x7F]


    while True:

        ser.write(send_array)

        time.sleep(0.2)
        frame_num += 1

        if frame_num == 0x40:
            frame_num = 0x00
