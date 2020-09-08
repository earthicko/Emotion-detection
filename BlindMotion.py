import argparse
import os
import sys
import time
from time import ctime

import cv2
import numpy as np
from tensorflow.keras.layers import (Conv2D, Dense, Dropout, Flatten,
                                     MaxPooling2D)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
import os
import sys
import subprocess
import asyncio
import websockets

if sys.platform == 'linux':
    from gpiozero import CPUTemperature

# input arg parsing
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fullscreen', help='Display window in full screen', action='store_true')
parser.add_argument('-d', '--debug', help='Display debug info', action='store_true')
parser.add_argument('-fl', '--flip', help='Flip incoming video signal', action='store_true')
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
args = parser.parse_args()

# create model
model = Sequential()

model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu', input_shape=(48, 48, 1)))
model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(7, activation='softmax'))

model.load_weights('model.h5')

# prevents openCL usage and unnecessary logging messages
cv2.ocl.setUseOpenCL(False)

# dictionary which assigns each label an emotion (alphabetical order)
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful",
                3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

def get_gpu_temp():
    temp = subprocess.check_output(['vcgencmd measure_temp | egrep -o \'[0-9]*\.[0-9]*\''],
                                    shell=True, universal_newlines=True)
    return str(float(temp))

# start the webcam feed
cap = cv2.VideoCapture(0)

# set serial attributes
portDict = {0: '/dev/ttyUSB0'}

refreshRate = 2 #in seconds


async def processDetection():
    while True:
        # time for fps
        start_time = time.time()

        # Find haar cascade to draw bounding box around face
        ret, frame = cap.read()
        
        if args.flip:
            frame = cv2.flip(frame, -1)
        else:
            frame = cv2.flip(frame, 1)
        if not ret:
            break
        facecasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facecasc.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        faceIndex = 0
        protagonistEmotion = 0
        
        

        for (x, y, w, h) in faces:
            
            roi_gray = gray[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(
                cv2.resize(roi_gray, (48, 48)), -1), 0)
            prediction = model.predict(cropped_img)
            maxindex = int(np.argmax(prediction))
            if faceIndex == 0:
                cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
                protagonistEmotion = maxindex
            else:
                cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 2)
            cv2.putText(frame, emotion_dict[maxindex], (x+20, y-60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            faceIndex += 1
        
        async with websockets.connect("ws://localhost:8765") as websocket:
            await websocket.send(str(protagonistEmotion))
        
        # full screen
        if args.fullscreen:
            cv2.namedWindow("video", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, 1)

        # debug info
        if args.debug:
            fps = str(int(1.0 / (time.time() - start_time)))
            cv2.putText(frame, fps + " fps", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            if sys.platform == 'linux':
                cpu_temp = str(int(CPUTemperature().temperature)) + " C (CPU)"
                cv2.putText(frame, cpu_temp, (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, get_gpu_temp() + " C (GPU)", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                
        cv2.imshow('video', cv2.resize(
            frame, (800, 480), interpolation=cv2.INTER_CUBIC))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

asyncio.get_event_loop().run_until_complete(processDetection())

cap.release()
cv2.destroyAllWindows()
