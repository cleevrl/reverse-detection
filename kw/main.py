import subprocess

#src='rtsp://210.99.70.120:1935/live/cctv005.stream'
src='rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaming/channels/102/httpPreview'
#src='rtsp://admin:dongbuict0@192.168.1.11:554/ISAPI/Streaming/channels/102/httpPreview'
#src='rtsp://admin:dongbuict0@dongbuict3.mooo.com:10001/ISAPI/Streaming/channels/102/httpPreview'

#src='/home/det-nano/reverse-detection/kw/res4sskip3_3/rawhttpPreview.avi'

cmd= f'yolo predict source={src} model=./yolov8s.engine  save=False classes=[2,5,7] save_txt'
subprocess.call(cmd, shell=True)
