from collections import defaultdict
from haversine import haversine
import cv2
import numpy as np
import math
import socket
from ultralytics import YOLO
from flask import Flask, request, render_template
import json
from roi import getRoiValue ,boxinRoinew, drawpolylines,RoiStat,getPpm_ab,get_distance
import time
import os

from lkwutil import getResFileName ,getCsvFileName,sendUDP,dist,mkdirfromfilename,getResFileNamewithdir,resFromFile,sendSpeedtoSharedMemory

# custom dataset으로 fine-tunning한 YOLOv8 model
# model = YOLO("best.pt")
# model=YOLO("../yolov8n.engine")

# Open the video file: 광교중앙역 cctv영상을 https://www.utic.go.kr/map/map.do?menu=cctv 에서 녹화한 영상

# print('Starting the UDP sender ~~')
UDPserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPserver.settimeout(5)
# src='/home/kw/dbict/Car-Speed-Estimation-using-YOLOv8/video/video.mp4'
# src="/home/kw/JetsonYoloV7-TensorRT/videos/testvideo1.mp4"
# filename=src.split("/")[-1]
# rack history 저장을 위한 dictls

track_history = defaultdict(lambda: [])

IMAGE_H = 1152
IMAGE_W = 720
src = np.float32([[380.4, 613.6], [1058.4, 561.6], [363.2, 301.2], [666.4, 268.4]])
dst = np.float32([[37.289227, 127.050917], [37.289039, 127.050644], [37.288842, 127.051426], [37.288655, 127.051158]])
lat_long_dst = np.float32([[37.289227, 127.050917], [37.289039, 127.050644], [37.288842, 127.051426], [37.288655, 127.051158]])

# python의 haversine 라이브러리로 각 위경도 좌표간의 거리를 계산
dst = np.float32([haversine(dst[0], i, unit="m") for i in dst])
print(dst)  # [0, 31.943, 61.973, 67.023]

dst = np.float32([[0, 0], [31.943, 0], [0, 61.973], [31.943, 61.973]])

lat_long_M = cv2.getPerspectiveTransform(src, lat_long_dst)
M = cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
# print(f"M : {M}")
# print(f"M : {lat_long_M}")

car_dict = defaultdict(list) # tracking되는 차별 id마다 변화되는 미터좌표계 저장ls

speed_dict = defaultdict(list) # 평균 속력 계산
speed_dict1 = defaultdict(list) # 평균 속력 계산

EntryTime= defaultdict(list) # 평균 속력 계산

lat_long_data = defaultdict(list)

#  cv.pointPolygonTest(contours[0], (j,i), True)

def FindPoint(x1, y1, x2, 
              y2, x, y) :
    if (x > x1 and x < x2 and
        y > y1 and y < y2) :
        return True
    else :
        return False
def FindPoint(x1, y1, x2, 
              y2, x, y) :
    if (x > x1 and x < x2 and
        y > y1 and y < y2) :
        return True
    else :
        return False
    
def boxinRoi(boxes,x1, y1, x2,y2):
    nboxes=[]
    for box in boxes:
        x,y,w,h=box
        if(FindPoint(x1,y1,x2,y2,x,y)):
            nboxes.append(box)
    return nboxes

def drawRoi(img,pts):
    print(f'drawroi{pts}')    
    for i in range(3):
        # print(pts[i][0], pts[i][1])
        cv2.line(img, (pts[i][0], pts[i][1]),(pts[i+1][0], pts[i+1][1]),(0, 255, 0),2)
    cv2.line(img, (pts[3][0], pts[3][1]),(pts[0][0], pts[0][1]),(0, 255, 0),2)
    return img

def view(src1):

    frame_count = 0

    cap = cv2.VideoCapture(src1)
   
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    print(w,h,fps)
    input()
    start=time.time()
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        frame_count += 1

        if success:
            if frame_count==5:
                start=time.time()
            if frame_count >10:    
                elapsed=time.time()-start
                fpscal=elapsed/frame_count
                fps1=frame_count/elapsed
                # cv2.putText(frame, f'{frame_count} / {fps1}', (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                now =time.strftime('%Y.%m.%d-%H:%M:%S')
                print(f'{now} {frame_count} fps {fps1}  ')
                cv2.putText(frame, f'{frame_count} / {fps1}', (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
           
            # results = model.track(frame, persist=True)
            cv2.imshow("YOLOv8 Inference", frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

def record(src1,file,duration):
    print(file)
    frame_count = 0
    cap = cv2.VideoCapture(src1)
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format

    rawv = cv2.VideoWriter(file, fourcc, fps, (w, h))
    while frame_count< duration:
        success, frame = cap.read()
        frame_count+=1
        rawv.write(frame)
        cv2.putText(frame, f'{fps} {frame_count} / {duration}', (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if success:
            cv2.imshow("YOLOv8 Inference", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break
    rawv.release()
    cap.release()
    cv2.destroyAllWindows()


def yolo(src1):
    model = YOLO("yolov8n.engine")


    frame_count = 0

    cap = cv2.VideoCapture(src1)
   
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    line_pts1 = [(0, int(h*.5)), (w, int(h*.5))]
    line_pts2 = [(0, int(h*.8)), (w, int(h*.8))]


    start=time.time()
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        frame_count += 1

        if success:
            # Run YOLOv8 inference on the frame
            elapsed=time.time()-start
            fpscal=elapsed/frame_count
            fps1=frame_count/elapsed
            cv2.putText(frame, f'{frame_count} / {fps1}', (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.line(frame, line_pts1[0], line_pts1[1], (255,0,0))
            cv2.line(frame, line_pts2[0], line_pts2[1], (255,0,0))

    
            # Yolov8 tracking 이용
            results = model.track(frame, persist=True)
            boxes = results[0].boxes.xywh.cpu()
            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()
           

            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                x1=int(x)
                y1=int(y)
                text= f'\n {frame_count} ,{time.time()}, {track_id}, {x}, {y}, {w} , {h} '
                print(text)

           
            cv2.imshow("YOLOv8 Inference", frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

def se(src1):
    from ultralytics.solutions import speed_estimation


    frame_count = 0

    cap = cv2.VideoCapture(src1)
    model1 = YOLO("yolov8n.pt")
    names = model1.model.names
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    line_pts = [(0, int(h*.75)), (w, int(h*.75))]

    speed_obj = speed_estimation.SpeedEstimator()
    speed_obj.set_args(reg_pts=line_pts,
                   names=names,
                   view_img=True)

# Loop through the video frames
    start=time.time()
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        frame_count +=1

        if success:
            # Run YOLOv8 inference on the frame
            tracks = model.track(frame, persist=True, show=False)
            frame = speed_obj.estimate_speed(frame, tracks)
            elapsed=time.time()-start
            fpscal=elapsed/frame_count
            fps1=frame_count/elapsed
            cv2.putText(frame, f'{frame_count} / {fps1}', (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            # Display the annotated frame
            cv2.imshow("YOLOv8 Inference", frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()
def cal_ab(x1,y1,x2,y2):
    a=(y2-y1)/(x2-x1)
    b=(x2*y1-x1*y2)/(x2-x1)
    return a,b
def calppm(y):
    a,b=cal_ab(297,13.76,429,25.43)
    return(y*a+b)
def calmeter(y,d):
    return(int(d/calppm(y)*100))

def run(src1,recordRaw,recordRes,resdir,skipCnt,showvideo,annotionOn,addr,port,duration,yolo,hsize):
# def run():
    frame_count = 0
    model = YOLO("yolov8n.engine")


    cap = cv2.VideoCapture(src1)


    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fps=10
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format

# Set up the video writer
   
    print(f"Video FPS: {fps}  {width} {height}frames per second") # 24 fps

    # 속도 계산된 동영상 저장
    # fourcc = cv2.VideoWriter_fourcc(*'avc1')
    txtfileName =resdir+getResFileName(src1)
    resvideofileName=txtfileName.replace("txt","avi")
    # rawvideofileName=resvideofileName.replace("res","raw")
    rawvideofileName=txtfileName.replace("txt","mp4")


    csvfileName=txtfileName.replace("txt","csv")
 
    print("lkw111"+rawvideofileName,resvideofileName)
    # mkdirfromfilename(videofileName)
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for MP4 format

    res = cv2.VideoWriter(resvideofileName, fourcc, fps, (width, height))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format

    rawv = cv2.VideoWriter(rawvideofileName, fourcc, fps, (width, height))
    
    f=open(txtfileName,"w")
    fcsv=open(csvfileName,"w")
    fcsv.write("frame,time,id,x,y,w,h,area")
    # f1=open("raw.csv","w")

    track_ids=[]
    px=0
    py=0
    speed=1
    speed1=1
    d=0
    dreal=0
    carCount=0
    TavgSpeed=[]
    TavgSpeedv=0
    a=0
    b=0
    # if duration==0:
    while cap.isOpened():
    # else:
    # while frame_count<duration:
    
        # 비디오 프레임 읽기
        success, frame = cap.read()
        if recordRaw:
            rawv.write(frame)
        frame_count += 1
        if frame_count==1:
            roi=getRoiValue(frame)
            # ppmref=getppmref(frame)
            a,b=getPpm_ab(frame)
        if frame_count%skipCnt!=0:
            continue
        print(roi)
        frame=drawpolylines(frame,roi)

     
        # f1.write(f': ')

        if success:
            # Yolov8 tracking 이용
            if yolo:
                results = model.track(frame, persist=True)
                boxes = results[0].boxes.xywh.cpu()
                
                if results[0].boxes.id is not None:
                    track_ids = results[0].boxes.id.int().cpu().tolist()
                    rawv.write(frame)
            else:
                boxes,track_ids = resFromFile(src1,width,height,frame_count)

            boxes=boxinRoinew(boxes,roi)
            carCount=len(boxes)
            # if annotionOn:
            #     annotated_frame = results[0].plot()
            # else:
            annotated_frame = frame
            framespeed=[]
            framespeedrev=[]
            frame=drawpolylines(frame,roi)
            # speedN=[]

            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                x1=int(x)
                y1=int(y)
                text= f'\n {frame_count} ,{time.time()}, {track_id}, {x}, {y}, {w} , {h} '
                fcsv.write(text)
                track = track_history[track_id]
                cv2.rectangle(annotated_frame, (int(x), int(y), int(w), int(h)), (0, 255, 0), 2)

                if len(track)>2:
                    px,py=track[-1]
                    # text= f'{frame_count} {track_id}, {px}, {py} , {int(x)}, {int(y)}'
                    d,dreal=get_distance((px,py),(x,y),a,b)             
                    dreal=d/(h/hsize)
                    # print(text)
                    # print(d,dreal,dreal1)
                    # # input("2")

                    # d,da=dist(px,py,x,y,5)
                    
                    speed1 = dreal * ((fps/skipCnt) / 1000) * 3600 
                    if(speed1 <10):
                        speed1=0
                    if(speed1 >100):
                        speed1=100
                    if(py>y):
                        speed1= -speed1
                    # da=d*480/(480-y)*3

                # speed1=calmeter((y+py)/2,d)*(100/fps)/skipCnt
                        
                # cal=calmeter((y+py)/2,d)   
                # speed1= (calmeter((y+py)/2,d)/3.5) * ((fps/skipCnt) / 1000) * 3600 # 1초당 24fps -> 1frame당 1/24초, 거리/(1/24)*3600/1000 -> km/h로 변환
                now =time.strftime('%Y.%m.%d-%H:%M:%S')
                text= f'\n frm: {now} {frame_count} track {track_id}, pre {px}, {py} , now {int(x)}, {int(y)}, d: {d:.2f} pixel, a{a} , b{b} ,dreal {dreal} meter, speed :{speed1:.2f} kmh'
                f.write(text)
                track.append((int(x), int(y))) # x, y center point


                # track.append((float(x), float(y)))  # x, y center point
                # x = x.tolist()
                # y = y.tolist()
                src_coor = np.float32([[x], [y], [1]])
                lat_long_coor = np.dot(M, src_coor)
                lat_long_coor = np.array([lat_long_coor[i][0] / lat_long_coor[2][0] for i in range(3)])
                # print(f'lat_long_coor:{lat_long_coor}, track_id: {track_id}')

                real_coor = np.dot(lat_long_M, src_coor)
                np.set_printoptions(precision=15)
                # print(real_coor)
                real_coor = np.array([real_coor[i][0] / real_coor[2][0] for i in range(3)])
                # print(f'real_coor:{real_coor}, track_id: {track_id}')
                lat_long_data[track_id].append(real_coor[:-1].tolist())

                if not car_dict[track_id]:
                    car_dict[track_id].append(lat_long_coor)
                else:
                    car_dict[track_id].append(lat_long_coor)
                    difference = car_dict[track_id][-2] - lat_long_coor
                    distance = math.sqrt(difference[0] ** 2 + difference[1] ** 2)
                    speed = distance * ((fps/skipCnt) / 1000) * 3600 # 1초당 24fps -> 1frame당 1/24초, 거리/(1/24)*3600/1000 -> km/h로 변환
                    # if speed1 >150:
                    #     continue
                    speed_dict[track_id].append(speed)
                    speed_dict1[track_id].append(speed1)

                    if len(speed_dict1[track_id]) > 4:
                        speed_dict1[track_id].pop(0)
                    elif len(speed_dict1[track_id]) < 4: # 처음 4 프레임은 맨 처음 계산한 속도 출력
                        avg_speed1 = speed_dict1[track_id][0]
                                     
                    if len(speed_dict1[track_id]) == 4:
                        avg_speed1 = sum(speed_dict1[track_id]) / 4.0

                    # 4 프레임의 평균 속도 계산
                    if len(speed_dict[track_id]) > 4:
                        speed_dict[track_id].pop(0)
                    elif len(speed_dict[track_id]) < 4: # 처음 4 프레임은 맨 처음 계산한 속도 출력
                        first_speed = speed_dict[track_id][0]
                        speed_text = f"{int(first_speed)} "
                        text= f'\n frm first : {frame_count} at ({int(x)},{int(y)}) 속도 : {int(first_speed)} km/h, 속도2 : {int(speed1)} km/h, id: {track_id} '
                     # print(text)
                        f.write(f' fs {int(first_speed)}')
                        cv2.putText(annotated_frame, speed_text, (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    
                    # 처음 4 프레임이 지난 이후, 4 프레임의 평균 속도 계산하여 속도 오차 보정
                    if len(speed_dict[track_id]) == 4:
                        avg_speed = sum(speed_dict[track_id]) / 4.0
                        # avg_speed1 = sum(speed_dict1[track_id]) / 4.0
                        speed_text = f"{int(avg_speed)} "
                        speed_text1 = f"{int(avg_speed1)} "
                        if avg_speed1>10 and avg_speed1< 100:
                            framespeed.append(avg_speed1)

                          
                        elif(avg_speed1 <-10 and avg_speed1>-100):
                            # input()
                            framespeedrev.append(avg_speed1)
                          

                        text= f'\n frm avg : {frame_count} at ({int(x)},{int(y)}) 속도 : {int(avg_speed)} km/h, 속도2 : {int(avg_speed1)} km/h, id: {track_id} '
                        print(text)
                        f.write(f' aso {int(avg_speed)}, as1 {int(avg_speed1)} ')
                        # f.write(text)
                        # cv2.putText(annotated_frame, str(track_id), (int(x), int(y) ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                        cv2.putText(annotated_frame, str(carCount), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        cv2.putText(annotated_frame, str(int(track_id)), (int(x), int(y) -10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.putText(annotated_frame, str(int(speed_text1)), (int(x), int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.putText(annotated_frame, str(int(frame_count)), (int(10), int(100)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

           

            if len(framespeed) !=0:
                Fspeed=int(sum(framespeed)/len(framespeed))
            else:
                Fspeed=0
            if len(framespeedrev) !=0:
                Fspeedrev=int(sum(framespeedrev)/len(framespeedrev))
            else:
                Fspeedrev=0


            cv2.putText(annotated_frame, str(Fspeed), (200,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.putText(annotated_frame, str(Fspeedrev), (300,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
           
            now =time.strftime('%Y.%m.%d - %H:%M:%S') 
            text= f'{now} frm {frame_count}  forward {Fspeed} reverse {Fspeedrev} km/h '
        #     addrl='221.168.134.9'
            # udpaddrlocal="127.0.0.1"
            # if SharedMemory:
            sendSpeedtoSharedMemory(text)
          
            if recordRes:
                    res.write(annotated_frame)

            if showvideo:
                cv2.imshow("YOLOv8 Tracking", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        else:
            break


    # video capture object와 close the display window Release
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":

    run()
