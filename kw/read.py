from kwse import run,view,se,record,yolo

#src='rtsp://admin:dongbuict0@192.168.1.11:554/ISAPI/Streaming/channels/102/httpPreview'
src="rtsp://210.99.70.120:1935/live/cctv005.stream"

# cordRaw=True  #원본영상 저장 여부 .mp4로 저장됨
# recordRes=True  #처리결과영상 저장 여부 .avi로 저장됨
# skipCnt=1       # camera 프레임 rate가 10 보다 큰경우 예를들어 30fps인경우 3으로 설정 3프레임중 하나마 yolo inference 하게 설정
#sharedMemory # send result to shared memory 1235 else sendUDP

udpaddrlocal="127.0.0.1"
udpport="7072"

addrl='221.168.134.9'
resdir= "./results/" # 걸과물 저장 디렉토리 영상과 .csv(yolo detect 결과) .txt (속도 계산 결과)
hsize=15 #bounding box 의 실제거리 근사값 단위 meter
# duration =0 # 0 forever 

run(src,recordRaw=True,recordRes=True,resdir=resdir,skipCnt=6,showvideo=True,duration=0,yolo=False,hsize=hsize)

