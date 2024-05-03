from flask import Flask, render_template, Response, stream_with_context
import cv2
from threading import Thread
OPENCV_AVFOUNDATION_SKIP_AUTH=1


app = Flask(__name__)
camera = 0

cameraOff = False

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames(firstInitialized):
    i = 0
    global camera
    global cameraOff
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        if cameraOff:
            print("not processing")
        else:
            print("processing")
@app.route('/video_feed')
def video_feed():
    return Response(stream_with_context(gen_frames(False)), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/toggle_camera')
def close_camera():
    global cameraOff
    if cameraOff:
        cameraOff = False
    else:
        cameraOff = True
    return "success"

if __name__ == '__main__':
    app.run(debug=True)