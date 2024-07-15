from kwse import run ,yolo,view

# src='rtsp://210.99.70.120:1935/live/cctv005.stream'
src='rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaming/channels/102/httpPreview'
#src='rtsp://admin:dongbuict0@192.168.1.11:554/ISAPI/Streaming/channels/102/httpPreview'
#src='rtsp://admin:dongbuict0@dongbuict3.mooo.com:10001/ISAPI/Streaming/channels/102/httpPreview'

resdir= "./dbict3/"
# 걸과물 저장 디렉토리 영상과 .csv(yolo detect 결과) .txt (속도 계산 결과)
hsize=15 #bounding box 의 실제거리 근사값 단위 meter

#view(src,True)
run(src,recordRaw=True,recordRes=True,resdir=resdir,skipCnt=1,showvideo=True,hsize=hsize,minh=20,up=True,yoffset=1)
