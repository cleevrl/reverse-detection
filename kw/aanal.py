import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from roi import getRoiValue ,boxinRoinew, drawpolylines,RoiStat,getPpm_ab,get_distance,getppmfromfile
import time
# read csv file

# df = df.iloc[::3]  # Start from the first row (index 0), and get every second row
# df2 = df[df['id'] == 2][:50]
# df3 = df[df['id'] == 3][:50]
# df4 = df[df['id'] == 4][:50]
# df5 = df[df['id'] == 5][:50]
# df6 = df[df['id'] == 6][:50]
# df7 = df[df['id'] == 7][:50]
# df8 = df[df['id'] == 8][:50]
# df['area'] = df['h']*df['x']
def euclidean_distance(row):
    return np.sqrt((row['x2'] - row['x1']) ** 2 + (row['y2'] - row['y1']) ** 2)

def speed_with_previous(row, prev_row,a,b):
    d=np.sqrt((row['x'] - prev_row['x']) ** 2 + (row['y'] - prev_row['y']) ** 2) 
    y1= (row['y'] + prev_row['y'])/2
    yppm=(y1*a+b)/3.5
    dreal=d/yppm
    # print(d,yppm,dreal)
    print(f'd{d}, {y1}, {yppm}, {dreal}')

    return dreal

def distance_with_previous(row, prev_row):
    return np.sqrt((row['x'] - prev_row['x']) ** 2 + (row['y'] - prev_row['y']) ** 2) 
def calculate_distance(pts1, pts2):
    distance = math.sqrt((pts2[0] -pts1[0])**2 + (pts2[1] - pts1[1])**2)
    return distance
def get_distance(pts1,pts2,a,b):
    d=calculate_distance(pts1,pts2)
    y1= (pts1[1]+pts2[1])/2
    yppm=(y1*a+b)/3.5
    dreal=d/yppm
    print(f'd{d}, {y1}, {yppm}, {dreal}')
    return dreal

def save_fig(df,num,sr):
    a,b=getppmfromfile()
    print(f' a={a} b={b}')
# Calculate distance with previous row for each row
    distances = [np.nan]  # Distance with the first row is not defined
    speeds=[np.nan]
   
    for i in range(1, len(df)):
        prev_row = df.iloc[i - 1]
        current_row = df.iloc[i]
        distance= distance_with_previous(current_row, prev_row)

        speed= speed_with_previous(current_row, prev_row,a,b)

        # print(distance)
        speeds.append(speed)
        distances.append(distance)
    df['D'] = distances
    df['speed']=speed
    # print(df)
    # df['Dm'] = df['D'].expanding().mean()
    # df['D4'] = df['D'].rolling(window=10).mean()
    # df['A'] =df['h']*df['w']
    # df['Td']=df['time'].diff()
    # df['Yd']=df['y'].diff()
    # df['speed']=df['D']/df['Td']
    plt.figure(figsize=(10, 6))
    # plt.plot(df['frame'], df['D4']*100, marker='o', label='D4')
    # plt.plot(df['frame'], df['y'], marker='o', label='y')
    # plt.plot(df['frame'], df['Yd'], marker='o', label='YD')
    # # # plt.plot(df['frame'], df['w']*10, marker='o', label='w')
    # # # plt.plot(df['frame'], df['h']*10, marker='o', label='h')
    # # # plt.plot(df['frame'], df['A']/5, marker='o', label='A')
    plt.plot(df['frame'], df['D'], marker='o', label='D')
    plt.plot(df['frame'], df['speed'], marker='o', label='speed')
    # plt.plot(df['frame'], df['Td']*100, marker='o', label='Td')
    # # plt.plot(df['frame'], df['speed'], marker='o', label='speed')



    plt.title('Monthly Sales and Expenses')
    plt.xlabel('y')
    plt.ylabel('x')
    plt.legend()
    plt.grid(True)
    plt.show()
    # plt.save?fig("./res/"+num+"restime.png")

def run_all(file,sr):
    df = pd.read_csv(file, header = 0)
    # Car-Speed-Estimation-using-YOLOv8/res_loc_2024-05-03_10_12.csv
    mid = df['id'].max()
    for i in range(mid):
        print(f'lkw{i}')
        df1 = df[df['id'] == i+1]
        df1 = df1.iloc[::sr]  # Start from the first row (index 0), and get every second row

        save_fig(df1,str(i+1),sr)
def run_one(file,id,sr):
    df = pd.read_csv(file, header = 0)
    # print(df)
   
    df1 = df[df['id'] == id][:34]
    df1 = df1.iloc[::sr]  # Start from the first row (index 0), and get every second row

    save_fig(df1,str(id),sr)
# file="resskip1/05-26_16:11:35res_org.csv"
# file='live005_1/05-26_17:44:47res_cctv005.csv'
# file='live005_1/05-26_17:55:21res_05-26_17:44:47res_cctv005.csv'
# run_one(file,1,1)
# /home/kw/projects/release/runs/detect/predict/labels/cctv005_0.txt
def resFromRunFile(filename,w,h):
    
    # input()
    # filename="/home/kw/res.txt"
    boxes=[]
    ids=[]
    f=open(filename,"r")
    # print(filename)
    Lines = f.readlines()
 
    for line in Lines:
        # print(line)
        val = line.split(' ')
        # for val in vals:
        # print(val)
        if len(val) >1 :
            c= int(val[0])
            x1= int(float(val[1])*w)
            y1= int(float(val[2])*h)
            w1= int(float(val[3])*w)
            h1= int(float(val[4])*h)
            # print(val[1])
            # print(x1,y1,w1,h1)
            boxes.append((c,x1,y1,w1,h1))
        else:
            timestamp=val[0]
        # if len(val)>6:
        #     ids.append(int(val[6]))
        # else:
        #     ids.append(0)
    return boxes, timestamp
# from lkwutil import   resFromRunFile
def find_min_index(lst):
    min_value = min(lst)
    min_index = lst.index(min_value)
    return min_index
def find_min_value(lst):
    min_value = min(lst)
    # min_index = lst.index(min_value)
    return min_value
def calculate_distance0(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance
def calculate_distance1(x1, y1, x2, y2):
    return abs(y1-y2)
    # return distance
def calculate_distance(x1, y1, x2, y2):
    d= math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    dy = abs(y1-y2)
    return d,dy

dallfail=[]
global uperr,downerr
uperr=0
downerr=0

# def calculate_distance_iou(box,box1):
#     calculate_iou(boxA, boxB)
    



def removedup(mats):
    newmat=[]
    pxyarr=[]
    smats = sorted(mats, key = lambda x:x[0])
    # print(smats)

    for mat in smats:
        d,x,y,w,h,px,py,ph,r=mat
        if (px,py) not in pxyarr:
            pxyarr.append((px,py))
            newmat.append(mat)
            # print("OKKKKKKKKKKKKKKKKKKK")
            # print(mat)

        else:
            # print("dupppppppppppppp")
            # print(mat)
            # print(px,py)
            continue
    # print("newmat")
    # print(newmat)
    return newmat



global hratio
hratio=0



# def pairmat(i,pboxes,boxes):

def pairmatIOU(pboxes,boxes,hsize,diff,f,i):
# def pairmat(pboxes,boxes):
    
    mat=[]
    if not pboxes or not boxes: 
        return mat
    # print(i)
    for box in boxes:
        # c,x,y,w,h=box
        x,y,w,h=box
        d=0
        dy=100
        ppy=0
        ppx=0
        spd=0
        pph=1
        for pbox in pboxes:
            # c,px,py,pw,ph=pbox
            px,py,pw,ph=pbox

            dd=calculate_iou(box,pbox)
          
            if(dd>d):
                d=dd
                ppy=py
                ppx=px
                pph=ph
        dist=calculate_distance0(x,y,ppy,ppx)
        mat.append((dist,x,y,w,h,ppx,ppy,pph,int(100*h/pph)))
        # print(x,y,px,py)
    mat=removedup(mat)
    f.write(f'\nframe{i}pre{str(pboxes)}\n')
    f.write(f'boxes{str(boxes)}\n')
    f.write(f'mat{str(mat)}\n')
    mat=removedup(mat)
    f.write(f'new mat{str(mat)}\n')
    return mat
# def pairmat(pboxes,boxes,hsize,diff,f,i):

def pairmat(pboxes,boxes,hsize,diff,f,i):
# def pairmat(pboxes,boxes):

    mat=[]
    if not pboxes or not boxes: 
        return mat

    for box in boxes:
        c,x,y,w,h=box
        # y=int(y+h/2)
        # if h <20:
        #     continue
        # print(f'box{box}')
        d=100
        dy=100
        ppy=0
        ppx=0
        pph=1
        spd=0
        for pbox in pboxes:
            c,px,py,pw,ph=pbox
            # if ph <20:
            #     continue
            dd=calculate_distance0(x,y,px,py)
            if(dd<d):
                d=dd
                ppy=py
                ppx=px
                pph=ph
        
        mat.append((d,x,y,w,h,ppx,ppy,pph,int(100*h/pph)))
        # print(x,y,px,py)
    # mat=removedup(mat)
    f.write(f'\nframe{i}pre{str(pboxes)}\n')
    f.write(f'boxes{str(boxes)}\n')
    f.write(f'mat{str(mat)}\n')
    mat=removedup(mat)
    f.write(f'new mat{str(mat)}\n')
    return mat
        

def find_dist_matrix(pboxes,boxes,hsize,diff,f,frame_count):
    mat=[]
    print(frame_count,diff)
    print(len(pboxes),len(boxes))
    ppx=0
    ppy=0
    dall=[]
   
    if diff==0:
        return mat
    if not pboxes or not boxes: 
        return mat
    for box in boxes:
        c,x,y,w,h=box
        if h <20:
            continue
        # print(f'box{box}')
        d=100
        dy=100
        ppy=0
        for pbox in pboxes:
            c,px,py,pw,ph=pbox
            # print(f'prebox{pbox}')
            if(calculate_distance0(x,y,px,py)<d):
                d,dy=calculate_distance(x,y,px,py)
                ppy=py
                ppx=px
        if d<2.1:
            continue
        dreal=d/(h/hsize)
        speedms=dreal/diff
       

       
        speedkm = speedms * 3.6
        if ppy<y:
            speedkm=-speedkm
        # speedkmy= (dy/(h/hsize))/diff*3.6
        text=f'{frame_count},{x},{y},{w},{h},{ppx},{ppy},{pw},{ph},{d},{hsize},{diff},{dreal},{int(speedkm)} ,{Isuppperlane(x,y)}\n'
        f.write(text)
        if abs(speedkm)>10 and abs(speedkm) <150:
            dall.append((x,y,w,h,ppx,ppy,d,speedkm))
        else:
        #     dallfail.append((x,y,w,h,ppx,ppy,d,speedkm))
            # print(text)
            # print("speedouttttttttttttttttttttttttttttttttttttt\n")
            continue
        global uperr,downerr
        if(Isuppperlane(x,y)):
            if ppy<y:
                print(x,y,ppx,ppy,d,speedkm)
                uperr+=1
                text="upper reverse \n"
                f.write(text)
                print("reversuuuuuuuuuuuuuuuuuuupppppppppp#####################################")
                # input()
        else:
            if ppy>y:
                print(x,y,ppx,ppy,d,speedkm)
                downerr+=1
                text="down reverse \n"
                f.write(text)
                print("reversdownwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww*********************************")
#         print(x,y,ppx,ppy,d)

#     result = sum(dall)

# # 평균 구하기
#     print(f"average : {result / len(dall)}")

        # if c==5:
        #     hsize=1.5*hsize
        # if c==7:
        #     hsize=2*hsize 

        # # if d<1:
        # #     continue    
        # dreal=d/(h/hsize)
        # speedms=dreal/diff
        
     
        # speedkm = speedms * 3.6
        # if speedkm>150:
        #     continue
        # if(ppy>y+1):
        #    speedkm=-speedkm
        #    print(ppy,y)
        #  #  input()

        
        #     #print("********************************************************************")
        #     #f.write("\n*****************************************\n")

        # text=f'\nframe {str(frame_count)} x {x},y {y},w {w},h {h},ppx {ppx},ppy {ppy},d {d}, diff {diff},dreal {dreal},speedms {speedms},speedkm {speedkm}'
        # print(text)
        # f.write(text)
        # mat.append((x,y,w,h,speedkm))
    # print(mat)

    return  dall
from collections import defaultdict
import cv2
import os
from roi import readRoiValue ,boxinRoinew
# def removedup(mats):
#     print("remove")
#     print(mats)
    # for mat in mats:
    #     print(mat)

def analorg(resdir,skipcnt,kk):
    width=704
    height=480
    preboxes=[]
    pretime=0
    hsize=15
    alldd=[]
    allspd=[]
    track=[]
    car1=[]
    car2=[]
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    f=open(resdir+"/res.txt","w")
    fr=open(resdir+"/ixyspd.txt","w")
    # /dbict/data/709/
    # src=f'/home/kw/dbict/data/709/predict9/ttpPreview.avi'
    # src="/home/kw/dbict/release627/video/rawhttpPreview.avi"
    # src=f'/home/kw/dbict/release627/runs/detect/predict{kk}/rawhttpPreview.avi'
    src=f'/home/kw/dbict/release627/runs/detect/predict{kk}/httpPreview.avi'

    # src=f'/home/kw/dbict/release627/runs/detect/predict{kk}/httpPreview.avi'

    # runs/detect/predict19/cctv005.avi
    # src="/home/kw/dbict/release627/video/predict5/httpPreview.avi"
    cap = cv2.VideoCapture(src)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    # if not os.path.exists(resdir):
    #     os.makedirs(resdir)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for MP4 format

    res = cv2.VideoWriter(resdir+"res.avi", fourcc, fps, (width, height))


    roi=readRoiValue()

    i=0
    errcnt=0
    bighcnt=0
    # while cap.isOpened():
    # skipcnt=10
    minusc=0
    while i<30000:
    # else:
    # while frame_count<duration:
    
        # 비디오 프레임 읽기
        success, frame = cap.read()
        frame=drawpolylines(frame,roi)
        i+=1
        if i%skipcnt!=0:
            continue

        src=f'/home/kw/dbict/release627/runs/detect/predict{kk}/labels/httpPreview_{i}.txt'
        boxes,tstamp=resFromRunFile(src,width,height)
      
        boxes=boxinRoinew(boxes,roi)
        # print(boxes)
        # text=f' frame{i} boxes{boxes} mat{mat}'
        # mats=find_dist_matrix(preboxes,boxes,hsize,float(tstamp)-float(pretime),f,i)
        tdiff=float(tstamp)-float(pretime)
        mats=pairmat(preboxes,boxes,hsize,float(tstamp)-float(pretime),f,i)
        text=f' frame{i} boxes{boxes} mat{mats}'
        # for mat in mats:
        #     d,x,y,w,h,px,py,ph,r=mat
        #     dreal=d/(h/hsize)
        #     speedms=dreal/tdiff
        #     spd = speedms * 3.6
        #     if py<y:
        #         spd=-spd
        #     print(i,x,y,spd)
            # f0.write((i,x,y,spd))

        # continue
        
        print(text)
        # removedup(mats)
        err=False
        
        for mat in mats:
            d,x,y,w,h,px,py,ph,r=mat
            # if d<2.1:
            #     cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 255), 2)
            #     cv2.putText(frame, "d<", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
            #     continue
            # if h<20:
            #     cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 255), 2)
            #     cv2.putText(frame, "<h", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
            #     continue
            # if ph<20:
            #     cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
            #     cv2.putText(frame, "<ph", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)

            #     continue
            # if r<80 or r>120:
            #     bighcnt+=1
            #     text=f'big {bighcnt} r{r} ,mat{mat}\n'
            #     f.write(text)
            #     cv2.putText(frame, "h/ph", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
            #     cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 0, 255), 2)
            #     continue
            dreal=d/(h/hsize)
            speedms=dreal/tdiff
            spd = speedms * 3.6
            if py<y:
                if spd>10:
                    spd=-spd
                # text=f'\nframe {str(i)} x {x},y {y},w {w},h {h},ppx {px},ppy {py},d {d}, diff {tdiff},dreal {dreal},speedms {speedms},speedkm {spd}'
                    text=f'\n{str(i)} x {x},y {y} {spd}'

                    fr.write(text)
                    minusc+=1
            # if abs(spd)<10 or abs(spd) >150:
            #     cv2.putText(frame, f'out{spd}', (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
            #     cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 0, 0), 2)
            #     continue

            
            text=f'\nframe {str(i)} x {x},y {y},w {w},h {h},ppx {px},ppy {py},d {d}, diff {tdiff},dreal {dreal},speedms {speedms},speedkm {spd}'
            # text=f'\nframe {str(i)} x {x},y {y},w {w},h {h},ppx {px},ppy {py},d {d}, speedkm {spd}'


            # print(text)
            f.write(text)
            
            alldd.append(d)
            
            allspd.append(spd)
            #  x,y,w,h,s=m
            if spd>0:
               
                cv2.line(frame, (x,y), (px,py),(255,255,0),2)
                # print(text)
                cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 3)
                f.write("\nerror")
                err=True
                errcnt +=1
            else:
                cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)

           
            # cv2.putText(frame, str(int(y)), (int(x), int(y) +0), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)


            cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 255), 2)
        global uperr,downerr
        cv2.putText(frame, str(i), (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, str(errcnt), (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if(err):
            cv2.imwrite(f'{resdir}_{i-1}.jpg',preframe)
            cv2.imwrite(f'{resdir}_{i}.jpg',frame)
            # errcnt += 1
        # cv2.putText(frame, str(downerr), (300, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


        preboxes=boxes
        pretime=float(tstamp)
        preframe=frame
      
        # if showvideo:
        cv2.imshow("YOLOv8 Tracking", frame)
        res.write(frame)
        # input()
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        time.sleep(0.03)

    result = sum(alldd)
    print(f'uperr {uperr},downerr {err}')

# # 평균 구하기
    print(f"lendd  {len(alldd)} max ={max(alldd)} average : {result / len(alldd)}")
    print(f"lenspd {len(allspd)} max ={max(allspd)} average : {sum(allspd) / len(allspd)}")
    f.write(f'uperr {uperr},downerr {errcnt}')

# # 평균 구하기
    f.write(f"lendd  {len(alldd)} max ={max(alldd)} average : {result / len(alldd)}")
    f.write(f"lenspd {len(allspd)} max ={max(allspd)} average : {sum(allspd) / len(allspd)}")

def anal(src,resdir,skipcnt,kk,framecnt,up,video,yoffset):
    width=704
    height=480
    preboxes=[]
    pretime=0
    hsize=15
    alldd=[]
    allspd=[]
    track=[]
    car1=[]
    car2=[]
    if not os.path.exists(resdir):
        os.makedirs(resdir)
    f=open(resdir+"/res.txt","w")
    fr=open(resdir+"/ixyspd.txt","w")
   
    # src=f'/home/kw/dbict/release627/runs/detect/predict{kk}/rawhttpPreview.avi'

    cap = cv2.VideoCapture(src)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    # if not os.path.exists(resdir):
    #     os.makedirs(resdir)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for MP4 format

    res = cv2.VideoWriter(resdir+"res.avi", fourcc, fps, (width, height))


    roi=readRoiValue()

    i=0
    errcnt=0
    ReCnt=0
    bighcnt=0
    # while cap.isOpened():
    # skipcnt=10
    minusc=0
    while i<framecnt:
    # else:
    # while frame_count<duration:
    
        # 비디오 프레임 읽기
        if video:
            success, frame = cap.read()
            frame=drawpolylines(frame,roi)
        i+=1
        if i%skipcnt!=0:
            continue
        
        # src=f'/home/kw/dbict/release627/runs/detect/predict{kk}/labels/rawhttpPreview_{i}.txt'
        filename=os.path.basename(src).split(".")[0]
        src1=os.path.dirname(src)+"/labels/"+filename+"_"+str(i)+".txt"
        boxes,tstamp=resFromRunFile(src1,width,height)
      
        boxes=boxinRoinew(boxes,roi)
        # print(boxes)
        # text=f' frame{i} boxes{boxes} mat{mat}'
        # mats=find_dist_matrix(preboxes,boxes,hsize,float(tstamp)-float(pretime),f,i)
        tdiff=float(tstamp)-float(pretime)
        mats=pairmat(preboxes,boxes,hsize,float(tstamp)-float(pretime),f,i)
        text=f' frame{i} boxes{boxes} mat{mats}'
       
        err=False
        pc=0
        mc=0
        pspd=[]
        mspd=[]
        for mat in mats:
            d,x,y,w,h,px,py,ph,r=mat
           
            dreal=d/(h/hsize)
            speedms=dreal/tdiff
            spd = speedms * 3.6
            # cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 255), 2)
            # cv2.putText(frame, str(spd), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
            if spd <10 or spd>150:
                if video:
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 255), 2)
                    cv2.putText(frame, "bad spd", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
                continue

            if d<2.1:
                if video:
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 255), 2)
                    cv2.putText(frame, "d<", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
                continue
            if h<20:
                if video:
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 255), 2)
                    cv2.putText(frame, "<h", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
                continue
            if ph<20:
                if video:
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 255, 0), 2)
                    cv2.putText(frame, "<ph", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)

            #     continue
            if r<80 or r>120:
                bighcnt+=1
                text=f'big {bighcnt} r{r} ,mat{mat}\n'
                f.write(text)
                if video:
                    cv2.putText(frame, "h/ph", (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 3)
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 0, 255), 2)
                continue

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
                text=f'\nframe {str(i)} x {x},y {y},w {w},h {h},ppx {px},ppy {py},d {d}, diff {tdiff},dreal {dreal},speedms {speedms},speedkm {spd}'
                # text=f'\n{str(i)} x {x},y {y} {spd}'
                if video:
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (0, 0, 0), 2)
                    cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
                    # cv2.imwrite(f'{resdir}{i-1}.jpg',preframe)
                    cv2.imwrite(f'{resdir}{i}.jpg',frame)
                    # print(text)
                fr.write(text)
                pspd.append(spd)
            else:
                if video:
                    cv2.rectangle(frame, (int(x-w/2), int(y-h/2), int(w), int(h)), (255, 255, 255), 2)
                    cv2.putText(frame, str(int(spd)), (int(x), int(y) -20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 3)
                mspd.append(spd)
                    # minusc+=1

            
       
        if mc>pc:
            errcnt+=1
        else:
            errcnt=0
        if errcnt >2:
            text=f'\nframe {str(i)} {len(boxes)} {mc} {pc} {errcnt} errrrrrrrrrrrrrrrrrrrrrrrr'
            fr.write(text)
            print(text)
            # print("\nERRRRRRRRRRRRRRRRRRRRRRRRRR")
            ReCnt+=1
            errcnt=0
            if video:
                # cv2.imwrite(f'{resdir}{i-1}err.jpg',preframe)
                cv2.imwrite(f'{resdir}{i}err.jpg',frame)
        if(len(mspd)>0):
            mspdd=int(sum(mspd)/len(mspd))
        else:
            mspdd=0
        if(len(pspd)>0):
            pspdd=int(sum(pspd)/len(pspd))
        else:
            pspdd=0
        text=f'\nframe {str(i)} {len(boxes)}p {mspdd} m{pspdd} e{errcnt} err{ReCnt}'
        # print(text)
        textv=f'frame {str(i)} {len(boxes)} p {pspdd} m {pspdd} {errcnt} err{ReCnt}'
        
        
        # now =time.strftime('%Y.%m.%d - %H:%M:%S') 
        # text= f'{now} frm {i}  forward {mspdd} reverse {pspdd} km/h '


        if video:
            cv2.putText(frame, str(textv), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        fr.write(text)
        print(text)
        preboxes=boxes
        pretime=float(tstamp)
        if video:
            preframe=frame
#    /rint(ReCnt)  
        # if video:
        #     cv2.imshow("YOLOv8 Tracking", frame)
        #     res.write(frame)
        # #     # input()
        #     if cv2.waitKey(1) & 0xFF == ord("q"):
        #          break
        # time.sleep(0.03)
    return ReCnt

   


def line_equation(x1, y1, x2, y2):
    # 두 점을 지나는 직선의 기울기 m 계산
    m = (y2 - y1) / (x2 - x1)
    
    # 직선의 절편 c 계산
    c = y1 - m * x1
    
    return m, c
def line(p1,p2):
    x1,y1=p1
    x2,y2=p2
    m,c=line_equation(x1, y1, x2, y2)
    return m,c
# # 예제 좌표
# x1, y1 = 2, 3
# x2, y2 = 4, 7
m,c=line((306, 176), (417, 339))
def Isuppperlane(x,y):
    
    if(x*m+c >y):
       return True
    else:
       return False
# # 직선의 방정식 계산
# m, c = line_equation(x1, y1, x2, y2)

# print(f"직선의 방정식: y = {m}x + {c}")

# line (306, 176), (417, 339)
def plot(x,y):
    
    plt.plot(x, y, marker='o', label='D')
    plt.title('Monthly Sales and Expenses')
    plt.xlabel('y')
    plt.ylabel('x')
    plt.legend()
    plt.grid(True)
    plt.show()
def caldist():
    i=0
    # while cap.isOpened():
    width=704
    height=480
    CarY=[]
    trucks=[]
    buses=[]
    CarH=[]
    TruckR=[]
    BusR=[]
    while i<3997:
      
        src=f'/home/kw/dbict/release627/runs/detect/predict2/labels/httpPreview_{i}.txt'
        boxes,tstamp=resFromRunFile(src,width,height)
        for box in boxes:
            c,x,y,w,h=box
            if c==2:
               CarY.append((x,y,h,y/h))
               CarH.append(y/h)
            elif c==5:
               trucks.append((x,y,w,h,y/h))
               TruckR.append(y/h)
            elif c==7:
               buses.append((x,y,w,h,y/h))
               BusR.append(y/h)
              # print(boxes)
        i+=1
    # printf'car {len(cars)} trucks {len(trucks)} buses {len(buses)}')
 
    print(CarY)
    # plot(CarY,CarH)
def calculate_iou(boxA, boxB):
    # Box format: [x, y, w, h]
    # Convert to (x1, y1, x2, y2)
    c,x1A, y1A, wA, hA = boxA
    c,x1B, y1B, wB, hB = boxB

    x2A = x1A + wA
    y2A = y1A + hA
    x2B = x1B + wB
    y2B = y1B + hB
    
    # Calculate the (x, y) coordinates of the intersection rectangle
    xA = max(x1A, x1B)
    yA = max(y1A, y1B)
    xB = min(x2A, x2B)
    yB = min(y2A, y2B)
    
    # Compute the area of intersection rectangle
    interWidth = max(0, xB - xA)
    interHeight = max(0, yB - yA)
    interArea = interWidth * interHeight
    
    # Compute the area of both bounding boxes
    boxAArea = wA * hA
    boxBArea = wB * hB
    
    # Compute the Intersection over Union (IoU)
    iou = interArea / float(boxAArea + boxBArea - interArea)
    
    return iou

# Example usage:
def pairmat0(pboxes,boxes):

    mat=[]
    if not pboxes or not boxes: 
        return mat

    for box in boxes:
        c,x,y,w,h=box
        print(f'box{box}')
        d=100
        dy=100
        ppy=0
        ppx=0
        pph=1
        spd=0
        for pbox in pboxes:
            c,px,py,pw,ph=pbox
          
          
            dd=calculate_distance0(x,y,px,py)
            print(f'     pbox{pbox} dd {dd}')
            if(dd<d):
                print(f'      small pbox{pbox}')
                d=dd
                ppy=py
                ppx=px
                pph=ph
        
        mat.append((d,x,y,w,h,ppx,ppy,pph,int(100*h/pph)))
    print(mat)
    mat=removedup(mat)
   
    return mat

def rmdup(boxes):
    box=[]

    for i in range(len(boxes)-1):
        for j in range(len(boxes)-1):
            print(calculate_iou(boxes[i], boxes[j]))

   
import subprocess


if __name__ == "__main__":
   
    kk=12

    resdir ="./res714vid"
    # # # for i in range(1,15):
    skipcnt=1

    res=resdir+"_"+str(kk)+"s"+str(skipcnt)+"/"
    # src=f'/home/kw/dbict/release627/runs/detect/predict{kk}/httpPreview.avi'
    # src=f'~/reverse-detection/runs/detect/predict{kk}/httpPreview.avi'
    src=f'/home/det-nano/reverse-detection/runs/detect/predict{kk}//httpPreview.avi'
    src1=os.path.dirname(src)+"/labels/"
    cmd=f'ls {src1}'
   
    commands = [
    cmd ,
    'wc -l',
    ]

    p1 = subprocess.Popen(commands[0], stdout=subprocess.PIPE, shell=True)
    p2 = subprocess.Popen(commands[1], stdin=p1.stdout, stdout=subprocess.PIPE, shell=True)
    p1.stdout.close()  # p1의 출력을 닫아줍니다.
    output = p2.communicate()[0]
    fcnt=output.decode()
    print(fcnt)
    # def anal(src,resdir,skipcnt,kk,framecnt,up,video,yoffset):

    cnt=anal(src,res,skipcnt,kk,int(fcnt)-3,True,True,1)
    print(skipcnt,cnt)



    # for i in range(1,15):
    #     skipcnt=i
    #     res=resdir+str(skipcnt)+"/"

    #     anal(res,skipcnt)

    # caldist()
    # m,c=line((306, 176), (417, 339))
    # print(Isuppperlane(310,176))
    # # leftright(310,176)
    # leftright(410,339)
    # leftright(420,339)
   
    # print(f"직선의 방정식: y = {m}x + {c}")
    # for x in range(0,480):
    #     y= x*m+c
    #     print(x,y)

# resskip1/05-26_16:11:35res_org.csv
    
# run_all("res_cctv005.csv",1)

# Car-Speed-Estimation-using-YOLOv8/res_cctv005.csv
    
# [(2, 383, 186, 29, 26), (2, 334, 171, 25, 17), (2, 502, 254, 51, 44), (2, 473, 236, 47, 35), (2, 474, 237, 31, 35)] 
# [(2, 380, 184, 27, 24), (2, 329, 169, 23, 18), (2, 502, 254, 51, 44), (2, 473, 236, 48, 36)]
# 186 184

# frame 1 x 380,y 184,w 27,h 24,ppx 383,ppy 186,d 3.605551275463989, diff 0.06069827079772949,dreal 2.2534695471649933,speedms 37.1257618635371,speedkm -133.65274270873357

# frame 1 x 502,y 254,w 51,h 44,ppx 502,ppy 254,d 0.0, diff 0.06069827079772949,dreal 0.0,speedms 0.0,speedkm 0.0

# frame 1 x 473,y 236,w 48,h 36,ppx 473,ppy 236,d 0.0, diff 0.06069827079772949,dreal 0.0,speedms 0.0,speedkm 0.0
# [(380, 184, 27, 24, -133.65274270873357), (502, 254, 51, 44, 0.0), (473, 236, 48, 36, 0.0)]
