import subprocess

src="rtsp://210.99.70.120:1935/live/cctv005.stream"
#src='http://admin:dongbuict0@192.168.1.11:80/ISAPI/Streaming/channels/102/httpPreview'
#src='rtsp://admin:dongbuict0@192.168.1.11:554/ISAPI/Streaming/channels/102/httpPreview'

cmd= f'yolo predict source={src} model=./yolov8s.engine save=True classes=[2,5,7] save_txt'
subprocess.call(cmd, shell=True)