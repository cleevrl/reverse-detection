import cv2
import numpy as np
import time

import multiprocessing

from datetime import datetime, timedelta
import os

# 김제한우 앞 한화 열영상
# url = "http://59.14.95.196:1188/cam"

# 김제한우 앞 TBT 일반영상 http
# url = "http://admin:dongbuict0@59.14.95.196:6480/ISAPI/Streaming/channels/102/httpPreview"

# 김제한우 앞 TBT 일반영상 rtsp
# url = "rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaing/channels/102/httpPreview"

# 내부 네트워크 TBT 일반영상 http
url = "http://admin:qwer1234@192.168.1.11:80/ISAPI/Streaming/channels/102/httpPreview"

# uart 통신 확인으로 재부팅을 하는 경우 True 활성화
is_watchdog = False

save_dir = "video"
location_id = "loc"

os.makedirs(save_dir, exist_ok=True)

def run():

    hour = -1
    minute = -1
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 10

    cap = cv2.VideoCapture(url)

    ret, frame = cap.read()

    while not ret:
        ret, frame = cap.read()
        print("none")

    shape = frame.shape
    print(shape)

    pre_time = time.time()

    for i in range(10):

        ret, frame = cap.read()
        cur_time = time.time()
        delta = cur_time - pre_time

        pre_time= cur_time
        print(1/delta)


    while True:
        
        cur_time = datetime.now()

        if cur_time.hour != hour:
        # if cur_time.minute != minute:

            str_time = cur_time.strftime("%Y-%m-%d_%H:%M")
            # writer.release()
            writer = cv2.VideoWriter(f'{save_dir}/{location_id}_{str_time}.mp4', fourcc, fps, (int(shape[1]), int(shape[0])))
            
            hour = cur_time.hour
            minute = cur_time.minute

            if hour == 0:
                break

        ret, frame = cap.read()

        writer.write(frame)
        cv2.imshow("frame", frame)

        key = cv2.waitKey(10)

        if key == 27:
            break
        

if __name__ == "__main__":

    run()
    print("closed!")
