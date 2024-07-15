
import sysv_ipc
import time
from lkwutil import resFromFile,sendSpeedtoSharedMemory,find_dist_matrix
import math
import socket
from ultralytics import YOLO
from flask import Flask, request, render_template
import json
from roi import readRoiValue ,boxinRoinew
import cv2
import os
memory=sysv_ipc.SharedMemory(1234)
i=0
def run():

    while True:
        # text=f'lkw  texts{i}'
    
        val=memory.read()
        vstr= val.decode("utf-8")
        vstr = vstr.partition("\n")[0]
        print(vstr)

        # boxes,timen = resFromFile(width,height)
        # print(text)
        i+=1
        time.sleep(.1)

# def run1(src1,showvideo):
def run(src1,recordRaw,recordRes,resdir,skipCnt,showvideo,duration,callyolo,hsize,minh,up,yoffset):

    cap = cv2.VideoCapture(src1)
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    preboxes=[]
    pretime=0
    width=704
    height=480
    hsize=15
    f=open(resdir+"res.txt","w")
    frame_count=0
    roi=readRoiValue()
    print(roi)
    #input()
    errcnt=0
    # minh=20
    bighcnt=0
    ReCnt=0

    while True:
        boxes,timen = resFromFile(width,height)
        #print("alloxes")
        #print(boxes)
        boxes=boxinRoinew(boxes,roi)

        # print("boxes")
        # print(boxes)
       
        #input()
        
        now =time.strftime('%Y.%m.%d-%H:%M:%S')
        nowt=float(time.time())
        # print(now,time.time(),timen)
        # (float(time.time())-float(timen))
        tdiff=float(timen)-float(pretime)
        if tdiff==0:
            time.sleep(.01)
            continue
        success, frame = cap.read()
        annotated_frame=frame
        text=f'now{nowt} frame {frame_count} diffpre {int(tdiff*1000)} ms readiff {int(1000*(nowt-float(timen)))} ms\n'
        print(text)
        f.write(text)
        f.write(str(boxes)+"\n")
        # mats=find_dist_matrix(preboxes,boxes,hsize,float(timen)-float(pretime),f,frame_count)
        mats=find_dist_matrix(preboxes,boxes,hsize,tdiff,f,frame_count,20)

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
            print("update preframe\n")
            preframe=frame
        now =time.strftime('%Y.%m.%d - %H:%M:%S') 
        text= f'{now} frm {frame_count} car {len(mats)} forward {mspdd} reverse {pspdd} km/h err {ReCnt} '
    #     addrl='221.168.134.9'
        # udpaddrlocal="127.0.0.1"
        # if SharedMemory:
        f.write(text)
        sendSpeedtoSharedMemory(text)
        # if showvideo:
            # if recordRes:
            #         res.write(annotated_frame)

        if showvideo:
            cv2.imshow("YOLOv8 Tracking", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        preboxes=boxes
        frame_count+=1
        pretime=timen
        time.sleep(.01)
        # if showvideo:
        # cv2.imshow("YOLOv8 Tracking", frame)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break
if __name__ == "__main__":
    src='rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaming/channels/102/httpPreview'
    src='rtsp://admin:dongbuict0@dongbuict3.mooo.com:10001/ISAPI/Streaming/channels/102/httpPreview'
    # run1(src,showvideo=True,up=True)
    run(src,recordRaw=True,recordRes=True,resdir="./resdir7141/",skipCnt=1,showvideo=True,duration=0,callyolo=True,hsize=15,minh=20,up=True,yoffset=1)
