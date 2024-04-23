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

load_dotenv()
# Azure Cognitive Services credentials
vision_subscription_key = os.environ["AZURE_COMPUTER_VISION_KEY"]
vision_endpoint = os.environ["AZURE_COMPUTER_VISION_ENDPT"]
face_KEY = os.environ["AZURE_FACE_KEY"]
face_ENDPT = os.environ["AZURE_FACE_ENDPT"]

# Initialize Computer Vision client and Face Client
computervision_client = ComputerVisionClient(vision_endpoint, CognitiveServicesCredentials(vision_subscription_key))
face_client = FaceClient(face_ENDPT, CognitiveServicesCredentials(face_KEY))

# Function to detect persons in a frame using Azure Cognitive Services
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

global pause_capture
pause_capture = False
#function that starts camera and processes each frame
def activateCamera():
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
            cv2.imshow('Frame', frame)
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

# #function to detect face in image of person
# def detectFace(img_path):
#     with open(img_path, 'r+b') as image_file:
#         detected_faces_local = face_client.face.detect_with_stream(image=image_file, return_face_id=False)
#     img = Image.open(img_path)
#     draw = ImageDraw.Draw(img)
#     for face in detected_faces_local:
#         draw.rectangle([
#             (face.face_rectangle.left, face.face_rectangle.top),
#             (face.face_rectangle.left + face.face_rectangle.width, face.face_rectangle.top + face.face_rectangle.height)
#         ], outline='red')

#     # Display the image
#     img = img.crop(
#             (face.face_rectangle.left, 
#             face.face_rectangle.top,
#             face.face_rectangle.left + face.face_rectangle.width, 
#             face.face_rectangle.top + face.face_rectangle.height)
#         )
#     img.save(img_path)


activateCamera()