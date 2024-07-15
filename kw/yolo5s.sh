#!/bin/bash

#src='rtsp://210.99.70.120:1935/live/cctv005.stream'
#src='rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaming/channels/102/httpPreview'
#src='rtsp://admin:dongbuict0@192.168.1.11:554/ISAPI/Streaming/channels/102/httpPreview'

yolo predict source=rtsp://210.99.70.120:1935/live/cctv005.stream model=./yolov8s.engine show save=True classes=[2,5,7] save_txt