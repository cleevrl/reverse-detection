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

from lkwutil import getResFileName ,getCsvFileName,sendUDP,dist,mkdirfromfilename,getResFileNamewithdir,resFromFile,find_dist_matrix,sendSpeedtoSharedMemory


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

def view(src1,showvideo):

    frame_count = 0

    cap = cv2.VideoCapture(src1)
   
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    print(w,h,fps)
    # input()
    start=time.time()
    #fps=[]
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        frame_count += 1

        if success:
            if frame_count==1:
                start=time.time()
            if frame_count >2:    
                now=time.time()
                
               # fpscal=elapsed/(frame_count-1)
                fps1=1/(now-start)
                #fps.append(fps1)
                start=now
                # cv2.putText(frame, f'{frame_count} / {fps1}', (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                now =time.strftime('%Y.%m.%d-%H:%M:%S')
                print(f'{now} {frame_count} fps {fps1}  ')
                cv2.putText(frame, f'{frame_count} / {fps1}', (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
           
            # results = model.track(frame, persist=True)
            if showvideo:
                cv2.imshow("YOLOv8 Tracking",frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            # else:
            #     try:
            #         ret, buffer = cv2.imencode('.jpg', annotated_frame,)
            #         annotated_frame = buffer.tobytes()
            #         yield (b'--frame\r\n'
            #             b'Content-Type: image/jpeg\r\n\r\n' + annotated_frame + b'\r\n')
            #     except Exception as e:
            #         pass
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
    model = YOLO("yolov8s.engine")


    frame_count = 0

    cap = cv2.VideoCapture(src1)
   
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    line_pts1 = [(0, int(h*.5)), (w, int(h*.5))]
    line_pts2 = [(0, int(h*.8)), (w, int(h*.8))]
    track_ids=[]

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

def runvid(src1,recordRaw,recordRes,resdir,skipCnt,showvideo,duration,callyolo,hsize,minh,up,yoffset):
    frame_count = 0
    cap = cv2.VideoCapture(src1)


    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format

# Set up the video writer
   
    print(f"Video FPS: {fps}  {width} {height}frames per second") # 24 fps

    txtfileName =resdir+getResFileName(src1)
    csvfileName=txtfileName.replace("txt","csv")
 
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for MP4 format

    res = cv2.VideoWriter(resdir+"res"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
    rawv = cv2.VideoWriter(resdir+"raw"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
    errv = cv2.VideoWriter(resdir+"err"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
    detv = cv2.VideoWriter(resdir+"det"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
    
    f=open(txtfileName,"w")
    fcsv=open(csvfileName,"w")
    fcsv.write("frame,time,id,x,y,w,h,area")
  
    preboxes=[]
    success, preframe = cap.read()
    pretime=0
    errcnt=0
    minh=20
    bighcnt=0
    ReCnt=0
    while cap.isOpened():
        success, frame = cap.read()
        if recordRaw:
            rawv.write(frame)
        
        # print(frame_count)
        if frame_count==1:
            roi=getRoiValue(frame)
        if frame_count%skipCnt!=0:
            continue
       
        frame=drawpolylines(frame,roi)
        annotated_frame=frame
        # continue
     
       
        if success:
           
            boxes,timen = resFromFile(width,height)
            if len(boxes)>0:
            	detv.write(annotated_frame)
            boxes=boxinRoinew(boxes,roi)
            tdiff=float(timen)-float(pretime)
            mats=find_dist_matrix(preboxes,boxes,hsize,tdiff,f,frame_count,minh)
            print(frame_count,tdiff)
          
         
            framespeed=[]
            framespeedrev=[]
            err=False
            mc=0
            pc=0
            pspd=[]
            mspd=[]

            for mat in mats:
                x,y,w,h,px,py,d,ph=mat

                dreal=d/(h/hsize)
                speedms=dreal/tdiff
                spd = speedms * 3.6
               
                cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
                if d<2.1:
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 0, 0), 2)
                    continue
                if h<minh:
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
                    continue
                if ph<minh:
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
                    continue
                r=int(100*h/ph)
                if r<50 or r>140:
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 255), 2)
                    bighcnt+=1
                    text=f'big {bighcnt} r{r} ,mat{mat}\n'
                    f.write(text)
                    continue
                if spd<10 or spd >150:
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 255, 0), 2)
                    continue
               
           
                if spd >0:
                    err=True
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 255), 2)
                    cv2.putText(annotated_frame, str(int(spd)), (int(x), int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                    framespeed.append(spd)
                    # input()
                else:
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 0, 255), 2)
                    cv2.putText(annotated_frame, str(int(spd)), (int(x), int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                    framespeedrev.append(spd)

                if up:
                    if py<y+yoffset:
                        spd=-spd
                        pc+=1
                else:
                    if py>y-yoffset:
                        spd=-spd
                        pc+=1

                
                
                    # t
                if spd>0:
                    mc+=1
                    text=f'\nframe {str(frame_count)} x {x},y {y},w {w},h {h},ppx {px},ppy {py},d {d}, diff {tdiff},dreal {dreal},speedms {speedms},speedkm {spd}'
                    # text=f'\n{str(i)} x {x},y {y} {spd}'
                   
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 0), 2)
                    cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
                    cv2.imwrite(f'{resdir}{frame_count-1}.jpg',preframe)
                    cv2.imwrite(f'{resdir}{frame_count}.jpg',frame)
                        # print(text)
                    f.write(text)
                    pspd.append(spd)
                else:
                   
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 255, 255), 2)
                    cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 3)
                    mspd.append(spd)
                        # minusc+=1

                
        
            if mc>pc:
                errcnt+=1
            else:
                errcnt=0
            if errcnt >2:
                text=f'\nframe {str(frame_count)} {len(boxes)} {mc} {pc} {errcnt} errrrrrrrrrrrrrrrrrrrrrrrr'
                f.write(text)
                print(text)
                # print("\nERRRRRRRRRRRRRRRRRRRRRRRRRR")
                ReCnt+=1
                errcnt=0
            # //    if video:
                cv2.imwrite(f'{resdir}{frame_count-1}err.jpg',preframe)
                cv2.imwrite(f'{resdir}{frame_count}err.jpg',frame)
            # else:

            if(len(mspd)>0):
                mspdd=int(sum(mspd)/len(mspd))
            else:
                mspdd=0
            if(len(pspd)>0):
                pspdd=int(sum(pspd)/len(pspd))
            else:
                pspdd=0
            text=f'\nframe {str(frame_count)} {len(boxes)} {mspdd} {pspdd} {errcnt} {ReCnt}'
            # print(text)
            textv=f'frame {str(frame_count)} {len(boxes)} p {pspdd} m {pspdd} {errcnt} {ReCnt}'
            
            
            # now =time.strftime('%Y.%m.%d - %H:%M:%S') 
            # text= f'{now} frm {i}  forward {mspdd} reverse {pspdd} km/h '


            # if video:
            cv2.putText(frame, str(textv), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            f.write(text)
            # print(text)
            preboxes=boxes
            pretime=float(timen)
            # if video:
            preframe=frame
            now =time.strftime('%Y.%m.%d - %H:%M:%S') 
            text= f'{now} frm {frame_count} car {len(mats)} forward {mspdd} reverse {pspdd} km/h err {ReCnt} '
        #     addrl='221.168.134.9'
            # udpaddrlocal="127.0.0.1"
            # if SharedMemory:
            f.write(text)
            sendSpeedtoSharedMemory(text)
          
            if recordRes:
                    res.write(annotated_frame)

            if showvideo:
                cv2.imshow("YOLOv8 Tracking", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            # else:
            #     try:
            #         ret, buffer = cv2.imencode('.jpg', annotated_frame,)
            #         annotated_frame = buffer.tobytes()
            #         yield (b'--frame\r\n'
            #             b'Content-Type: image/jpeg\r\n\r\n' + annotated_frame + b'\r\n')
            #     except Exception as e:
            #         pass
        else:
            now =time.strftime('%Y.%m.%d - %H:%M:%S') 
            f.write(f'{now} {time.time()} vvvvvvvvvvvvvvvvvvvvvvvideo read error')
            time.sleep(0.01)
            continue
            #pass
      
    f.close()
    cap.release()
    cv2.destroyAllWindows()
def run(src1,recordRaw,recordRes,resdir,skipCnt,showvideo,hsize,minh,up,yoffset):
    frame_count = 0
    cap = cv2.VideoCapture(src1)


    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format

# Set up the video writer
   
    print(f"Video FPS: {fps}  {width} {height}frames per second") # 24 fps

    txtfileName =resdir+getResFileName(src1)
    csvfileName=txtfileName.replace("txt","csv")
 
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    if showvideo:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for MP4 format

        res = cv2.VideoWriter(resdir+"res"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
        rawv = cv2.VideoWriter(resdir+"raw"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
        errv = cv2.VideoWriter(resdir+"err"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
        detv = cv2.VideoWriter(resdir+"det"+getResFileName(src1).replace("txt","avi"), fourcc, fps, (width, height))
    
    f=open(txtfileName,"w")
    fcsv=open(csvfileName,"w")
    fcsv.write("frame,time,id,x,y,w,h,area")
  
    preboxes=[]
    success, preframe = cap.read()
    roi=getRoiValue(preframe)
    pretime=0
    errcnt=0
   
    bighcnt=0
    ReCnt=0
    while cap.isOpened():
        if showvideo:
            success, frame = cap.read()
            if recordRaw:
                rawv.write(frame)
      
        # print(frame_count)
        # if frame_count==1:
        #     roi=getRoiValue(frame)
        if frame_count%skipCnt!=0:
            continue
        if showvideo:
            frame=drawpolylines(frame,roi)
            annotated_frame=frame
        # continue
     
       
        if success:
           
            try:
                boxes,timen = resFromFile(width,height)
            except Exception as e:
                # Handle any exception
                print(f"An error occurred: {e}")
            if showvideo:
                if len(boxes)>0:
                    detv.write(annotated_frame)
            boxes=boxinRoinew(boxes,roi)
            tdiff=float(timen)-float(pretime)
            if tdiff==0:
                continue
            frame_count += 1
            now =time.strftime('%Y.%m.%d-%H:%M:%S')
            nowt=float(time.time())
            # print(now,time.time(),timen)
            # (float(time.time())-float(timen))
            tdiff=float(timen)-float(pretime)
            if tdiff==0:
                time.sleep(.01)
                continue
            # success, frame = cap.read()
            if showvideo:
                annotated_frame=frame
            text=f'now {nowt} frame {frame_count} diffpre {int(tdiff*1000)} ms readiff {int(1000*(nowt-float(timen)))} ms\n'
            print(text)
            f.write(text)
            f.write(str(boxes)+"\n")





            mats=find_dist_matrix(preboxes,boxes,hsize,tdiff,f,frame_count,minh)
            # print(frame_count,tdiff)
          
         
            framespeed=[]
            framespeedrev=[]
            err=False
            mc=0
            pc=0
            pspd=[]
            mspd=[]

            for mat in mats:
                x,y,w,h,px,py,d,ph=mat

                dreal=d/(h/hsize)
                speedms=dreal/tdiff
                spd = speedms * 3.6
                if showvideo:
                    cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
                if d<2.1:
                    if showvideo:
                        cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 0, 0), 2)
                    continue
                if h<minh:
                    if showvideo:
                        cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
                    continue
                if ph<minh:
                    if showvideo:
                        cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
                    continue
                r=int(100*h/ph)
                if r<50 or r>140:
                    if showvideo:
                      cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 255), 2)
                    bighcnt+=1
                    text=f'big {bighcnt} r{r} ,mat{mat}\n'
                    f.write(text)
                    continue
                if spd<10 or spd >150:
                    if showvideo:
                        cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 255, 0), 2)
                    continue
               
           
                if spd >0:
                    err=True
                    if showvideo:
                        cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 255), 2)
                        cv2.putText(annotated_frame, str(int(spd)), (int(x), int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                    framespeed.append(spd)
                    # input()
                else:
                    if showvideo:
                        cv2.rectangle(annotated_frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 0, 255), 2)
                        cv2.putText(annotated_frame, str(int(spd)), (int(x), int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                    framespeedrev.append(spd)

                if up:
                    if py<y+yoffset:
                        spd=-spd
                        pc+=1
                else:
                    if py>y-yoffset:
                        spd=-spd
                        pc+=1

                
                
                    # t
                if spd>0:
                    mc+=1
                    text=f'\nframe {str(frame_count)} x {x},y {y},w {w},h {h},ppx {px},ppy {py},d {d}, diff {tdiff},dreal {dreal},speedms {speedms},speedkm {spd}'
                    # text=f'\n{str(i)} x {x},y {y} {spd}'
                    if showvideo:
                        cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 0), 2)
                        cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
                        cv2.imwrite(f'{resdir}{frame_count-1}.jpg',preframe)
                        cv2.imwrite(f'{resdir}{frame_count}.jpg',frame)
                        # print(text)
                    f.write(text)
                    pspd.append(spd)
                else:
                    if showvideo:
                        cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 255, 255), 2)
                        cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 3)
                    mspd.append(spd)
                        # minusc+=1

                
        
            if mc>pc:
                errcnt+=1
            else:
                errcnt=0
            if errcnt >2:
                text=f'\nframe {str(frame_count)} {len(boxes)} {mc} {pc} {errcnt} errrrrrrrrrrrrrrrrrrrrrrrr'
                f.write(text)
                print(text)
                # print("\nERRRRRRRRRRRRRRRRRRRRRRRRRR")
                ReCnt+=1
                errcnt=0
                if showvideo:
                    cv2.imwrite(f'{resdir}{frame_count-1}err.jpg',preframe)
                    cv2.imwrite(f'{resdir}{frame_count}err.jpg',frame)
            # else:

            if(len(mspd)>0):
                mspdd=int(sum(mspd)/len(mspd))
            else:
                mspdd=0
            if(len(pspd)>0):
                pspdd=int(sum(pspd)/len(pspd))
            else:
                pspdd=0
        
            text=f'\nframe {str(frame_count)} {len(boxes)} {mspdd} {pspdd} {errcnt} {ReCnt}'
            # print(text)
            textv=f'frame {str(frame_count)} {len(boxes)} p {pspdd} m {pspdd} {errcnt} {ReCnt}'
            
            
            # now =time.strftime('%Y.%m.%d - %H:%M:%S') 
            # text= f'{now} frm {i}  forward {mspdd} reverse {pspdd} km/h '


            if showvideo:
                cv2.putText(frame, str(textv), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            f.write(text)
            # print(text)
            preboxes=boxes
            pretime=float(timen)
            if showvideo:
                preframe=frame
            now =time.strftime('%Y.%m.%d - %H:%M:%S') 
            text= f'{now} frm {frame_count} car {len(mats)} forward {mspdd} reverse {pspdd} km/h err {ReCnt} '
        #     addrl='221.168.134.9'
            # udpaddrlocal="127.0.0.1"
            # if SharedMemory:
            f.write(text)
            sendSpeedtoSharedMemory(text)
            if showvideo:
                if recordRes:
                        res.write(annotated_frame)

            if showvideo:
                cv2.imshow("YOLOv8 Tracking", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            # else:
            #     try:
            #         ret, buffer = cv2.imencode('.jpg', annotated_frame,)
            #         annotated_frame = buffer.tobytes()
            #         yield (b'--frame\r\n'
            #             b'Content-Type: image/jpeg\r\n\r\n' + annotated_frame + b'\r\n')
            #     except Exception as e:
            #         pass
        else:
            now =time.strftime('%Y.%m.%d - %H:%M:%S') 
            f.write(f'{now} {time.time()} vvvvvvvvvvvvvvvvvvvvvvvideo read error')
            time.sleep(0.03)
            continue
            #pass
        time.sleep(0.01)
    f.close()
   

if __name__ == "__main__":

    run()
