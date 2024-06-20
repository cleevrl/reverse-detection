from kwse import run
import time
import subprocess

#src="rtsp://210.99.70.120:1935/live/cctv005.stream"
#src='http://admin:dongbuict0@192.168.1.11:80/ISAPI/Streaming/channels/102/httpPreview'
src='rtsp://admin:dongbuict0@192.168.1.11:554/ISAPI/Streaming/channels/102/httpPreview'

cmd= f'yolo track source={src} model=./yolov8n.engine save=false  classes=[2,5,7] save_txt'
subprocess.call(cmd, shell=True)
