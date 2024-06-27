import time
import socket
import json
import numpy as np
import cv2
import math
import os

def mkdirfromfilename(file_path):

    directory_name_os = os.path.dirname(file_path)
    if not os.path.exists(directory_name_os):
        os.makedirs(directory_name_os)
   
def adjdist(y,d,ratio):
    yl=int(480*0.5)
    yh=int(480*0.8)
    res=d+ratio*(yh-y)/(yh-yl)
    return res

def dist(x1,y1,x2,y2,ratio):
    
    dxy=calculate_distance(x1, y1, x2, y2)
    adxy=adjdist(y1,dxy,ratio)
    return dxy,adxy

def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def getResFileNamewithdir(src):
    # print(src)
    filename=src.split("/")[-1].split(".")[0]
    current_time = time.localtime()
    formatted_time = time.strftime("%m-%d_%H:%M:%S", current_time)
    print(formatted_time)  # 예: 2024-0
    resfile="./res/"+formatted_time+'res_'+filename+".txt"
    return resfile
def getResFileNamewithTime(src):
    print(src)
    filename=src.split("/")[-1].split(".")[0]
    current_time = time.localtime()
    formatted_time = time.strftime("%m-%d_%H:%M:%S", current_time)
    print(formatted_time)  # 예: 2024-0
    resfile=formatted_time+'res_'+filename+".txt"
    return resfile
def getResFileName(src):
    # print(src)
    filename=src.split("/")[-1].split(".")[0]
    resfile=filename+".txt"
    return resfile
def getCsvFileName(src):
    print(src)
    filename=src.split("/")[-1].split(".")[0]
    current_time = time.localtime()
    formatted_time = time.strftime("%m-%d_%H:%M:%S", current_time)
    print(formatted_time)  # 예: 2024-0
    resfile='res_'+filename+".csv"
    return resfile




#print('Starting the UDP sender ~~')
UDPserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPserver.settimeout(5)
# addr="172.30.1.60"
addrl='221.168.134.9'
def sendUDP(addr,port,sample_data):
    UDPserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Text :", sample_data)
     
    sample_data = json.dumps(sample_data).encode()
    print("TXD :", sample_data)
    UDPserver.sendto(sample_data, (addr, int(port)))
# def sendUDP(sample_data):
#     UDPserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     print("Text :", sample_data)
     
#     sample_data = json.dumps(sample_data).encode()
#     print("TXD :", sample_data)
#     UDPserver.sendto(sample_data, ('127.0.0.1', 7072))
#     # time.sleep(1)

def cal_ab(x1,y1,x2,y2):
    a=(y2-y1)/(x2-x1)
    b=(x2*y1-x1*y2)/(x2-x1)
    return a,b
def calppm(y):
    a,b=cal_ab(297,13.76,429,25.43)
    return(y*a+b)
def calmeter(y,d):
    return(int(d/calppm(y)*100))

def dict():
    EnrtyT={}
    id=1
    Now=time.time()
    print(Now)
    EnrtyT[id]=time.time()
    EnrtyT[2]="lkw"
    time.sleep(1)
    runtime=time.time()-EnrtyT[1]
    print(runtime)
    print(EnrtyT[1])
    print(EnrtyT[2])
    print(EnrtyT)
    del EnrtyT[2]
    print(EnrtyT)
    if not 3 in EnrtyT:
        EnrtyT[3]="test3"
    print(EnrtyT)

    # resfromfile
 

def getRoiValue(img):
    try:
        f=open("roi.txt","r")
        txt=f.readline()
        values = txt.replace("(","").replace(")","").replace("[","").replace("]","").split(',')
        roi=[]
        for i in range(4):
            roi.append((int(values[2*i+0]),int(values[2*i+1])))
        return(roi)
          
        #   print(v)
    except:
        return(getROI(img))

def resFromSaveFile(src,w,h,frame_count):
    # dir=src.split("/")[:-1]
    dir = os.path.dirname(src)
   
    # input()
    filename=f'{dir}/labels/{src.split("/")[-1].split(".")[0]}_{str(frame_count)}.txt'
    boxes=[]
    ids=[]
    f=open(filename,"r")
    print(filename)
    Lines = f.readlines()
 
    for line in Lines:
        val = line.split(' ')
        # print(len(val))
        if len(val) >1 :
            boxes.append(((float(val[1])*w),(float(val[2])*w),int(float(val[3])*w),int(float(val[4])*w)))
            # boxes.append((int(float(val[1])*w),int(float(val[2])*w),int(float(val[3])*w),int(float(val[4])*w)))

            # print((val[1]*w),(val[2]*h),(val[3]*w),(val[4]*h))
        if len(val)>5:
            ids.append(int(val[5]))
        else:
            ids.append(0)
    
    # print(f'read {ids} {boxes}')
    # input()
    return boxes, ids


import sysv_ipc

# memory2=sysv_ipc.SharedMemory(1235)
memory=sysv_ipc.SharedMemory(1234)
memory2=sysv_ipc.SharedMemory(1235,flags=sysv_ipc.IPC_CREAT|777,size=1000)

def sendSpeedtoSharedMemory(text):

    print(text)
    memory2.write(b'\x00' * memory.size)
    memory2.write(str(text)+"\n")


def resFromFile(w,h):
   
    # input()
    val=memory.read()
    vstr= val.decode("utf-8")
    vstr = vstr.partition("]")[0]
    # print(vstr)
    val1=vstr.replace("[","").replace("]","").replace("'","")
    # print(f'val{val1}')
  
    Lines=val1.split(',')
    boxes=[]
    ids=[]
    for line in Lines:
        # print(line)
        val = line.split(' ')
        # for val in vals:
        print(val)
        if len(val) >1 :
            c= int(val[1])
            x1= int(float(val[2])*w)
            y1= int(float(val[3])*h)
            w1= int(float(val[4])*w)
            h1= int(float(val[5])*h)
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

def find_min_index(lst):
    min_value = min(lst)
    min_index = lst.index(min_value)
    return min_index
def find_min_value(lst):
    min_value = min(lst)
    # min_index = lst.index(min_value)
    return min_value

def find_dist_matrix(pboxes,boxes,hsize,diff,f,frame_count):
    mat=[]
    # print(diff)
    # print(pboxes,boxes)
    ppx=0
    ppy=0
    if diff==0:
        return mat
    if not pboxes or not boxes: 
        return mat
    for box in boxes:
        c,x,y,w,h=box
        d=100
        ppy=0
        for pbox in pboxes:
            c,px,py,pw,ph=pbox
            if(calculate_distance(x,y,px,py)<d):
                d=calculate_distance(x,y,px,py)
                ppy=py
                ppx=px
        if c==5:
            hsize=1.5*hsize
        if c==7:
            hsize=2*hsize     
        dreal=d/(h/hsize)
        speedms=dreal/diff
        
     
        speedkm = speedms * 3.6
        if speedkm>150:
            continue
        if(ppy<y):
            speedkm=-speedkm
        text=f'\nframe {str(frame_count)} x {x},y {y},w {w},h {h},ppx {ppx},ppy {ppy},d {d}, diff {diff},dreal {dreal},speedms {speedms},speedkm {speedkm}'
        f.write(text)
        mat.append((x,y,w,h,speedkm))
    # print(mat)

    return mat
   
def resFromFileFile(src,w,h,frame_count):
    
    # input()
    filename="/home/kw/res.txt"
    boxes=[]
    ids=[]
    f=open(filename,"r")
    print(filename)
    Lines = f.readlines()
 
    for line in Lines:
        val = line.split(' ')
        print(val)
        if len(val) >1 :
            x1= int(float(val[1])*w)
            y1= int(float(val[2])*h)
            w1= int(float(val[3])*w)
            h1= int(float(val[4])*h)
            
            boxes.append((x1-w1/2,y1-h1/2,w1,h1))
            # print((val[1]*w),(val[2]*h),(val[3]*w),(val[4]*h))
        if len(val)>5:
            ids.append(int(val[5]))
        else:
            ids.append(0)
    # print(f' {boxes}')
    # input()
    return boxes, ids
# my_dict[key] = value

if __name__ == "__main__":

    # src='/home/kw/dbict/rescctv005/org.avi'
    # print(getResFileName(src))
    # f=open(getResFileName(src),"w")
   
    dict()

    # for i in range(0,480):
    #     d=i*a+b
    #     print(i,a,b,d)
