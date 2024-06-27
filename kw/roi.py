
import cv2 as cv
import imutils
import numpy as np
import json
import math

pts = [] #마우스로 클릭한 포인트를 저장
resultforJSON = [] # pts에 저장된 포인트를 json형태로 저장
file_path = './sample.json' #json으로 저장하기 위한 파일경로
def drawpolylines(img2,pts):
    points = np.array(pts, np.int32)
    points = points.reshape((-1,1,2)) #pts 
    img2 = cv.polylines(img2, [points], True, (255,255,255), 2) 
    return img2

def getROI(img):
    def draw_roi(event, x, y, flags, param): #roi검출을 위한 함수 정의
        
        img2 = img.copy()
        
        if event == cv.EVENT_LBUTTONDOWN: #마우스 왼쪽버튼을 클릭하면
            pts.append((x,y)) #pts에 (x,y)좌표를 추가한다
        # print('포인트 #%d 좌표값(%d,%d)' % (len(pts),x,y)) #정상적으로 추가되는지 출력으로 확인
            
        resultforJSON.append({'point':[len(pts)],
                                'coordinate':[[int(x),int(y)]]})
                                # 포인트 순서와 좌표값을 딕셔너리 형태로 추가해준다
                                
        if event == cv.EVENT_RBUTTONDOWN: #마우스 오른쪽버튼을 클릭하면
            pts.pop() #클릭했던 포인트를 삭제한다
            
        if event == cv.EVENT_MBUTTONDOWN: #마우스 중앙(휠)버튼을 클릭하면
            print('총 %d개의 포인트 설정' % len(pts))
            mask = np.zeros(img.shape, np.uint8) #컬러를 다루기 때문에 np로 형변환
            points = np.array(pts, np.int32)
            points = points.reshape((-1,1,2)) #pts 2차원을 이미지와 동일하게 3차원으로 재배열
            
            mask2 = cv.polylines(mask, [points], True, (255,255,255), 2) #포인트와 포인트를 연결하는 라인을 설정
            # mask2 = cv.fillPloy(mask.copy(), [points], (255,255,255)) #폴리곤 내부 색상 설정
            
            ROI = cv.bitwise_and(mask2,img) # mask와 mask2에 중첩된 부분을 추출
            with open(file_path,'w') as outfile: #resultforJSON에 저장된 내용을 json파일로 추출
                json.dump(resultforJSON,outfile,indent=4)
                
            cv.imshow('ROI',ROI)
            cv.waitKey(0)
            
        text= f' select ROI leftTop => rightTop=> rightBottom => leftBottom'
        cv.putText(img, text, (50,50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if len(pts)>0: #포인트를 '원'으로 표시
            cv.circle(img2,pts[-1],3,(0,0,255),-1)
        
        if len(pts)>1:
            for i in range(len(pts) -1):
                cv.circle(img2, pts[i], 5,(0,0,255),-1)
                cv.line(img=img2, pt1=pts[i], pt2=pts[i+1], color=(255,0,0),thickness=2)
        if len(pts)==4: #마우스 중앙(휠)버튼을 클릭하면
            print('총 %d개의 포인트 설정' % len(pts))
            points = np.array(pts, np.int32)
            points = points.reshape((-1,1,2)) #pts 
            img2 = cv.polylines(img2, [points], True, (255,255,255), 2) 
            text= f' press "q" to exit Roi setting'
            cv.putText(img, text, (250,250), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.imshow('image',img2)

 
   
    # img = imutils.resize(img, width=500)
    cv.namedWindow('image')
    cv.setMouseCallback('image',draw_roi)
    # cv.imshow("org",img)
    while True:
        key = cv.waitKey(1) & 0xFF
        if key == 27:
            break
        if key == ord('q'):
            saved_data = {'ROI':pts}
            break
    
    cv.destroyAllWindows()
    f=open("roi.txt","w")
    f.write(str(pts))
    f.close()
    return pts

def getppmref(img):
    def drawppmref(event, x, y, flags, param): #roi검출을 위한 함수 정의
        
        img2 = img.copy()
        
        if event == cv.EVENT_LBUTTONDOWN: #마우스 왼쪽버튼을 클릭하면
            pts.append((x,y)) #pts에 (x,y)좌표를 추가한다
        # print('포인트 #%d 좌표값(%d,%d)' % (len(pts),x,y)) #정상적으로 추가되는지 출력으로 확인
            
        resultforJSON.append({'point':[len(pts)],
                                'coordinate':[[int(x),int(y)]]})
                                # 포인트 순서와 좌표값을 딕셔너리 형태로 추가해준다
                                
        if event == cv.EVENT_RBUTTONDOWN: #마우스 오른쪽버튼을 클릭하면
            pts.pop() #클릭했던 포인트를 삭제한다
            
        if event == cv.EVENT_MBUTTONDOWN: #마우스 중앙(휠)버튼을 클릭하면
            print('총 %d개의 포인트 설정' % len(pts))
            mask = np.zeros(img.shape, np.uint8) #컬러를 다루기 때문에 np로 형변환
            points = np.array(pts, np.int32)
            points = points.reshape((-1,1,2)) #pts 2차원을 이미지와 동일하게 3차원으로 재배열
            
            mask2 = cv.polylines(mask, [points], True, (255,255,255), 2) #포인트와 포인트를 연결하는 라인을 설정
            # mask2 = cv.fillPloy(mask.copy(), [points], (255,255,255)) #폴리곤 내부 색상 설정
            
            ROI = cv.bitwise_and(mask2,img) # mask와 mask2에 중첩된 부분을 추출
            with open(file_path,'w') as outfile: #resultforJSON에 저장된 내용을 json파일로 추출
                json.dump(resultforJSON,outfile,indent=4)
                
            cv.imshow('ROI',ROI)
            cv.waitKey(0)
            
        text= f' select white lines '
        cv.putText(img, text, (50,50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if len(pts)>0: #포인트를 '원'으로 표시
            cv.circle(img2,pts[-1],3,(0,0,255),-1)
        if len(pts)==2:
            cv.line(img=img2, pt1=pts[0], pt2=pts[0+1], color=(255,0,0),thickness=2)
        if len(pts)==4:
            cv.line(img=img2, pt1=pts[2], pt2=pts[2+1], color=(255,0,0),thickness=2)
            text= f' press "q" to exit ppm ref'
            cv.putText(img, text, (250,250), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
     
            
        cv.imshow('image',img2)

 
   
    # img = imutils.resize(img, width=500)
    cv.namedWindow('image')
    cv.setMouseCallback('image',drawppmref)
    # cv.imshow("org",img)
    while True:
        key = cv.waitKey(1) & 0xFF
        if key == 27:
            break
        if key == ord('q'):
            saved_data = {'ROI':pts}
            break
   
    cv.destroyAllWindows()
    f=open("ppm.txt","w")
    f.write(str(pts))
    f.close()
    return pts


def boxinRoinew(boxes,roi):
    nboxes=[]
    # points = np.array(roi, np.int32)
    # points = points.reshape((-1,1,2)).tolist() #pts 

    for box in boxes:
        c,x,y,w,h=box
        if(XyInsideRoi((x,y),roi)):
            nboxes.append(box)
    return nboxes

def XyInsideRoi(point,polygon):
#    def is_point_in_polygon(point, polygon):
    """
    Determines if a point is inside a polygon using the Ray Casting algorithm.

    :param point: A tuple (x, y) representing the point to check.
    :param polygon: A list of tuples [(x1, y1), (x2, y2), ..., (xn, yn)] representing the vertices of the polygon.
    :return: True if the point is inside the polygon, False otherwise.
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside
yl=240
yh=440

def RoiStat(pre,cur,roi):
    py=pre[1]
    y=cur[1]
    val=0
    if py>yh and yl <y and y< yh:
        val=1
    if py > yl and py <yh and y>yl and y <yh:
        val=11
    if py > yl and py <yh and y<yl :
        val=10
    if (py > yh and y >yh) or (py<yl and y <yl):
        val=0
    # print(f"oooooooooo {py} ,{y} oooo {val} oooooooooooooooooooooooooooo")

    return val

def RoiStatup(pre,cur,roi):
    py=pre[1]
    y=cur[1]
    val=0
    if py<yl and yl <y and y< yh:
        val=1
    if py > yl and py <yh and y>yl and y <yh:
        val=11
    if py > yl and py <yh and y >yh:
        val=10
    if (py > yh and y >yh) or (py<yl and y <yl):
        val=0
    # print(f"oooooooooo {py} ,{y} oooo {val} oooooooooooooooooooooooooooo")

    return val




def RoiStatroi(pre,cur,roi):
    # print(f'roi stat{pre} ,{cur} {roi}')
    val=0
    if XyInsideRoi(pre,roi):
        val=+1
    if XyInsideRoi(cur,roi):
        val+=10
    
    print(f'roi stat{pre} ,{cur} ,{val}')
  
    return val
        



# src = cv.imread('img/milkdrop.bmp', cv.IMREAD_GRAYSCALE)
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
def getPpmValue(img):
    try:
        f=open("ppm.txt","r")
        txt=f.readline()
        values = txt.replace("(","").replace(")","").replace("[","").replace("]","").split(',')
        roi=[]
        for i in range(4):
            roi.append((int(values[2*i+0]),int(values[2*i+1])))
        return(roi)
          
        #   print(v)
    except:
        return(getppmref(img))


def cal_ab(x1,y1,x2,y2):
    a=(y2-y1)/(x2-x1)
    b=(x2*y1-x1*y2)/(x2-x1)
    return a,b
def calppm(y):
    a,b=cal_ab(297,13.76,429,25.43)
    return(y*a+b)
def calmeter(y,d):
    return(int(d/calppm(y)*100))
def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance
def calculate_distance(pts1, pts2):
    distance = math.sqrt((pts2[0] -pts1[0])**2 + (pts2[1] - pts1[1])**2)
    return distance

def get_ab(pts):
    d1=calculate_distance(pts[0],pts[1])
    d2=calculate_distance(pts[2],pts[3])
    y1= (pts[0][1]+pts[1][1])/2 # (y1+y2)2
    y2= (pts[2][1]+pts[3][1])/2 # (y1+y2)2
    a,b=cal_ab(y1,d1,y2,d2)
    return a,b
def get_distance_ab(pts1,pts2,a,b):
    d=calculate_distance(pts1,pts2)
    y1= (pts1[1]+pts2[1])/2
    yppm=(y1*a+b)/3.5
    dreal=d/yppm
    # print(f'Y {y1} pixel {d},yppm {yppm},dreal{dreal}')
    return d,dreal
def get_distance(pts1,pts2):
    d=calculate_distance(pts1,pts2)
    return d
def getPpm_ab(img):
    #h,w=img.shape[:2]
    # img = cv.resize(img, dsize=(w*2, h*2), interpolation=cv.INTER_AREA)
    pts=getPpmValue(img)
    print(pts)
    a,b=get_ab(pts)
    return a,b
def getPpm_ab_double(img):
    h,w=img.shape[:2]
    img = cv.resize(img, dsize=(w*2, h*2), interpolation=cv.INTER_AREA)
    pts=getPpmValue(img)
    print(pts)
    a,b=get_ab(pts)
    return a,b
def getPpm_ab_pts(img):
    h,w=img.shape[:2]
    # img = cv.resize(img, dsize=(w*2, h*2), interpolation=cv.INTER_AREA)
    pts=getPpmValue(img)
    print(pts)
    a,b=get_ab(pts)
    return a,b,pts
def getPpm_ab_pts_double(img):
    h,w=img.shape[:2]
    img = cv.resize(img, dsize=(w*2, h*2), interpolation=cv.INTER_AREA)
    pts=getPpmValue(img)
    print(pts)
    a,b=get_ab(pts)
    return a,b,pts
def getppmfromfile():
    src='../img/first_frame.jpg'
    src='/home/kw/dbict/reforg.jpg'
    # text= f' select ROI leftTop=>rightTop> rightBottom=>leftBottom and press "q" '
    img= cv.imread(src)
   
    a,b=getPpm_ab(img)
    return a,b
# pre 469, 437 , now 469, 438, d: 1.48 pixel, a0.13620415510571893 , b-61.86376942417397

def speed(pre,now,a,b,fcount):
    fps=30
    time=fcount*(fps/1000)
    pixel,meter=get_distance(pre,now,a,b)
    print(f' pixel {pixel},fcount{fcount} frame time {time} sec {meter}meter {meter/time} mps {meter/time*3.6} kmh')


if __name__ == "__main__":

    # src='../img/first_frame.jpg'
    # src='/home/kw/dbict/reforg.jpg'
    src='/home/kw/dbict/Car-Speed-Estimation-using-YOLOv8/reforgdb.jpg'
    # # text= f' select ROI leftTop=>rightTop> rightBottom=>leftBottom and press "q" '
    img= cv.imread(src)
   
    a,b,pts=getPpm_ab_pts(img)
    
    # print(get_distance(pts[0],pts[1],a,b))
    # print(get_distance(pts[2],pts[3],a,b))
    # print(get_distance(pts[0],pts[3],a,b))

    # print(get_distance(pts[0],pts[3],a,b))
    # pts=[(819, 687), (827, 720), (863, 850), (877, 906)]
    # a,b=get_ab(pts)
    print(pts,a,b)
    print(get_distance(pts[0],pts[1],a,b))
    print(get_distance(pts[2],pts[3],a,b))
    print(get_distance(pts[0],pts[3],a,b))

    fps=30
    pre=(444,371)
    now=(456,403)
    fcount=29-6
    speed(pre,now,a,b,fcount)
    
    pre=(510,412)
    now=(537,477)
    fcount=75-42
    speed(pre,now,a,b,fcount)

    pre=(467, 320)
    now =(469, 325)
    speed(pre,now,a,b,5)


    #  frm: 45 track 7, pre 467, 320 , now 469, 325, d: 5.73 pixel, a0.2574168279842063 , b-81.93373060879858 ,dreal 18.342294692993164 meter, speed :316.95 kmh fs 15