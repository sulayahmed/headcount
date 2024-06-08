from flask import Flask, render_template, Response, stream_with_context
import cv2
from threading import Thread
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import cv2
#import numpy as np
from io import BytesIO  
import time
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import numpy as np
OPENCV_AVFOUNDATION_SKIP_AUTH=1

load_dotenv()
# Azure Cognitive Services credentials
vision_subscription_key = os.environ["AZURE_COMPUTER_VISION_KEY"]
vision_endpoint = os.environ["AZURE_COMPUTER_VISION_ENDPT"]
face_KEY = os.environ["AZURE_FACE_KEY"]
face_ENDPT = os.environ["AZURE_FACE_ENDPT"]

app = Flask(__name__)
camera = 0

cameraOff = False

# Initialize Computer Vision client and Face Client
computervision_client = ComputerVisionClient(vision_endpoint, CognitiveServicesCredentials(vision_subscription_key))
face_client = FaceClient(face_ENDPT, CognitiveServicesCredentials(face_KEY))

def detect_persons(frame):
    # Convert frame to bytes
    _, img_encoded = cv2.imencode('.jpg', frame)
    image_bytes = img_encoded.tobytes()

    # Perform object detection
    detected_objects = computervision_client.detect_objects_in_stream(BytesIO(image_bytes))

    # Check if persons are detected
    for obj in detected_objects.objects:
        if obj.object_property == "person":
            return True
    
    return False


@app.route('/')
def index():
    return render_template('index.html')

pause_capture = False
def gen_frames(firstInitialized):
    global pause_capture
    i = 0
    # Initialize camera
    cap = cv2.VideoCapture(1)
    processing_interval = 3 # in seconds
    start_time = time.time()
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if ret:
            # Display the resulting frame
            frame = np.asarray(frame)
            ret, buffer = cv2.imencode('.jpg', np.asarray(frame))

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            if time.time() - start_time >= processing_interval:
                start_time = time.time()
                
                if not pause_capture:
                    # Check for person
                    if detect_persons(frame):
                        pause_capture = True
                        # Save the frame as an image
                        #CHANGE NAME TO PERSON NAME --> KEEP THE i
                        person_name = "rajan"
                        cv2.imwrite(f'pictures/{person_name}{i}.png', frame)
                        print("Person detected!")
                        i+=1
                        if i == 5:
                            break
                        #IMPLEMENT FUNCTIONALITY
                        #detectFace(f'person_detected{i}.jpg')
                pause_capture = False
        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture
    cap.release()
    cv2.destroyAllWindows()
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