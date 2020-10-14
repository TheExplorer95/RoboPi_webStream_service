from flask import Flask, render_template, Response
from threading import Thread, Lock
from time import sleep
from utils.stereo_cam import CamThread
from utils.realsense_cam import RealCam
import cv2 as cv
import imutils
import datetime

# -------- Global vars --------------------
app = Flask(__name__)

cam = CamThread(ID=0, name='frontCam')
realCam = RealCam()

#----------Routes--------------------------
@app.route('/')
def index():
    currentTime = (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M')
    
    templateData = {
            'title': 'RoboPi - Homepage',
            'time': currentTime}

    return render_template('index.html', **templateData)

@app.route('/streams')
def streams():
    return render_template('streams.html')

@app.route('/about')
def about():
    return render_template('about.html')


#----------live feeds---------------------
@app.route('/frontCam_feed')
def frontCam_feed():
    # returns response + media type (mime type)
    return Response(camGen(cam), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/realCam_feed')
def realCam_feed():
    return Response(camGen(realCam), mimetype='multipart/x-mixed-replace; boundary=frame')

#----------Functions---------------------
def camGen(cam):
    while True:
        frame = cam.get_frame()
        if frame is None: 
            continue
        
        (flag, frontFrame) = cv.imencode('.jpg', frame)
        if not flag:
           continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frontFrame) + b'\r\n\r\n')

if __name__ == '__main__':
    app.run(threaded=True, use_reloader=False, debug=True)
