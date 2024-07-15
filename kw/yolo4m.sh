#!/bin/bash

#src='rtsp://210.99.70.120:1935/live/cctv005.stream'
#src='rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaming/channels/102/httpPreview'
#src='rtsp://admin:dongbuict0@192.168.1.11:554/ISAPI/Streaming/channels/102/httpPreview'

yolo predict source=rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaming/channels/102/httpPreview model=./yolov8m.pt save=false classes=[2,5,7] save_txt