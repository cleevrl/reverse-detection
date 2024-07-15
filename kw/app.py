# from flask import Flask, render_template, Response, request,send_file
from flask import Flask, render_template, request, redirect, url_for,send_from_directory,send_file,Response,jsonify

import time
import subprocess
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread
from kwse import run, view

global source,savedir,cycle,model,recordRaw,recordRes,savefig,hsize,skipCnt
source="rtsp://admin:admin@172.30.1.43:5540/12"
source="rtsp://210.99.70.120:1935/live/cctv005.stream" 

# source='http://admin:dongbuict0@59.14.95.196:6480/ISAPI/Streaming/channels/101/httpPreview'
source='rtsp://admin:dongbuict0@59.14.95.196:55464/ISAPI/Streaming/channels/102/httpPreview'


savedir="./res_s/"
model='yolov8s.engine'
hsize=15
skipCnt=6


global capture,rec_frame, grey, switch, neg, face, rec, out 
capture=0
grey=0
neg=0
face=0
switch=1
rec=0

#make shots directory to save pics
try:
    os.mkdir('./shots')
except OSError as error:
    pass

#Load pretrained face detection model    
# net = cv2.dnn.readNetFromCaffe('./saved_model/deploy.prototxt.txt', './saved_model/res10_300x300_ssd_iter_140000.caffemodel')

#instatiate flask app  
app = Flask(__name__, template_folder='./templates')

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)


def detect_face(frame):
    global net
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))   
    net.setInput(blob)
    detections = net.forward()
    confidence = detections[0, 0, 0, 2]

    if confidence < 0.5:            
            return frame           

    box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
    (startX, startY, endX, endY) = box.astype("int")
    try:
        frame=frame[startY:endY, startX:endX]
        (h, w) = frame.shape[:2]
        r = 480 / float(h)
        dim = ( int(w * r), 480)
        frame=cv2.resize(frame,dim)
    except Exception as e:
        pass
    return frame

def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame,source
    i=0

    camera = cv2.VideoCapture(source)
    w, h, fps = (int(camera.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    print(w,h,fps)

    while True:
        success, frame = camera.read() 
        i+=1
        text=f'fn{i},w {w},h {h},fps {fps}'
        # print(text)
        frame= cv2.putText(frame,text, (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)

        if success:
            if(face):                
                frame= detect_face(frame)
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame=cv2.bitwise_not(frame)    
            if(capture):
                capture=0
                now = datetime.datetime.now()
                p = os.path.sep.join(['shots', "shot_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, frame)
            
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                frame=cv2.flip(frame,1)
            
                
            try:
                ret, buffer = cv2.imencode('.jpg', frame,)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass
global text1
text1="Adjust camera Position and press Start !!!"


@app.route('/setroi')
def setRoi():
    
    return render_template('roi.html')

@app.route('/')
def start():
    cmd=f'./clean.sh {source} {model}'
    subprocess.call(cmd, shell=True)
    
    return render_template('start.html', model=model,source=source,hsize=str(hsize),savedir=savedir,skipCnt=str(skipCnt))

@app.route('/save-roi', methods=['POST'])
def save_roi():
    roi_data = request.json
    print('Received ROI data:', roi_data)
    points = roi_data['points']
    
    print('Received ROI data:', points)
    pts=[]
    for point in points:
        print(point)
        pts.append((point['x'],point['y']))
    # cv.destroyAllWindows()
    #  {'points': [{'x': 219, 'y': 206}, {'x': 344, 'y': 202}, {'x': 439, 'y': 310}, {'x': 153, 'y': 346}]}
    # [(215, 199), (326, 186), (455, 325), (165, 376)]
    print(pts)
    f=open("roi.txt","w")
    f.write(str(pts))
    f.close()
    return jsonify({'status': 'success', 'received': roi_data})
    
@app.route('/video_feed')
def video_feed():

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    global source
    return Response(view(source,showvideo=False), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed1')
def video_feed1():
    global source,model,savedir,hsize,skipCnt
    print(f' video feed  {time.time()} {source},{model},{savedir},{hsize}')
    # return Response(barongenframe(source,model,recordRaw,recordRes,resdir=savedir,skipCnt=1,showvideo=False,annotionOn=False,duration=3000,cycle=int(cycle),savefig=True,yolo=False)
    return Response(run(source,recordRaw=True,recordRes=True,resdir=savedir,skipCnt=skipCnt,showvideo=False,duration=0,callyolo=False,hsize=15,minh=20), mimetype='multipart/x-mixed-replace; boundary=frame')


#   <label for="source">source:</label>
#                 <input type="text" id="source" name="source"  size="10" />
#                 <label for="dir">dir:</label>
#                 <input type="text" id="dir" name="dir"  size="10" />
#                 <label for="cycle">cycle:</label>
#                 <input type="text" id="cycke" name="cycle"  size="10" />
#                 <select name="">
#                     <option value="cd">cd</option>
#                     <option value="wafer">wafer</option>
#                 </select>

#                 <label><input type="checkbox" name="recordorg" value="recordorg"> recordorg</label>
#                 <label><input type="checkbox" name="recordres" value="recordres"> recordres</label>
#                 <label><input type="checkbox" name="savefig" value="savefig"> savefig</label>
import psutil
 
def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
@app.route('/requests',methods=['POST','GET'])
def tasksnew():
    global source,savedir,hsize,model,recordRaw,recordRaw,recordRes,camera,skipCnt
    if request.method == 'POST' :#& request.form.get('start') == start :
        if request.form.get('show') == 'show':
            # print('@*@!&*!^*&!^*^!&*^!*&*!') 
            source=request.form.get('source')
            # camera.release()

            # camera = cv2.VideoCapture(source)

            # return render_template('start.html')
            return render_template('start.html', model=model,source=source,hsize=hsize,savedir=savedir)

        if request.form.get('start') == 'start':
            # print('@*@!&*!^*&!^*^!&*^!*&*!') 
            source=request.form.get('source')
            savedir=request.form.get('savedir')
            model=request.form.get('model')
            hsize=int(request.form.get('hsize'))
            skipCnt=int(request.form.get('skipCnt'))
          
            recordRaw = True if 'recordorg' in request.form else False
            recordRes= True if 'recordres' in request.form else False
            callyolo= True if 'callyolo' in request.form else False
            if not checkIfProcessRunning("yolo"):
                cmd=f'./yolo.sh {source} {model}'
                subprocess.call(cmd, shell=True)
                global text1

                text1= 'wait 30 seconds to init yolo'
                # return render_template('start.html')
                time.sleep(50)
                print('wait 30 seconds..')
                text1= 'yolo init finished....'
            else:
               
                text1= '@@@@@@@@@@@@@@@@yolo already started....'
                input()
            print(f'recordRaw ={recordRaw} recordRes ={recordRes}')
     
    elif request.method=='GET':
        print("lkw get********************")
        return render_template('start0.html')
    return render_template('start1.html')


# UPLOAD_FOLDER = os.path.join('temp')
# DOWNLOAD_FOLDER = os.path.join('static', 'downloads')

# # Ensure the upload and download folders exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def list_files(directory):
    files = []
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files
 

# @app.route('/download', methods=['POST'])
# def download_file():
#     file_name = request.form['file_name']
#     file_path = os.path.join(UPLOAD_FOLDER, file_name)

#     # Send the file to the user
#     return send_file(file_path, as_attachment=True)

# @app.route('/download111', methods=['POST'])
# def download_menu():
#    return render_template('index1.html')


def list_files(directory):
    files = []
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files
global root_directory
root_directory="./temp"
# Function to list directories in a directory
def list_directories(directory):
    directories = []
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isdir(path):
            directories.append(filename)
    return directories

@app.route('/downloadMenu', methods=['POST'])
def download_menu():
    # print("download111")
    global root_directory
    filedir=request.form.get('filedir')
    root_directory = filedir  # Replace with your desired root directory
    files = list_files(filedir)
    directories = list_directories(root_directory)
    return render_template('index1.html', files=files, directories=directories, current_directory='')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the form!'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file!'
    
    # You can process/save the file here
    # For example, save the file to a folder
    file.save(os.path.join('uploads', file.filename))
    
    return 'File successfully uploaded!'

@app.route('/download/<path:subpath><filename>')
def download_file(subpath, filename):
    global root_directory
    directory = os.path.join(root_directory, subpath)
    return send_file(directory+filename, as_attachment=True)
    # return send_from_directory(directory, filename)

@app.route('/download1', methods=['POST'])
def download_file1():
    global root_directory
    file_name = request.form['file_name']
    print(f'download_file1 {file_name}')
    file_path = os.path.join(root_directory, file_name)

    # Send the file to the user
    return send_file(file_path, as_attachment=True)


@app.route('/browse/<path:subpath>')
def browse_directory(subpath):
    global root_directory
    directory_path = os.path.join(root_directory, subpath)
    if not os.path.isdir(directory_path):
        return 'Directory does not exist!'
    
    files = list_files(directory_path)
    directories = list_directories(directory_path)
    return render_template('index1.html', files=files, directories=directories, current_directory=subpath)

@app.route('/navigate/<path:subpath>')
def navigate_directory(subpath):
    return redirect(url_for('browse_directory', subpath=subpath))



# @app.route('/startyolo', methods=['POST'])
# def startyolo():
#     global source
#     cmd= f'yolo track source={source} model=./ptfile/bestcd.engine save=false  save_txt'
# # # cmd2='python udpr.py'
#     subprocess.call(cmd, shell=True)


@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
        elif  request.form.get('grey') == 'Grey':
            global grey
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            global neg
            neg=not neg
        elif  request.form.get('face') == 'Face Only':
            global face
            face=not face 
            if(face):
                time.sleep(4)   
        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                          
                 
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=5500)
    
camera.release()
cv2.destroyAllWindows()     