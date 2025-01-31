#!/usr/bin/python3
import numpy as np
import sys
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')
import time
from alexnet import alexnet
import random

WIDTH = 320
HEIGHT = 240
LR = 1e-3
EPOCHS = 8
MODEL_NAME = 'tf-{}-{}-{}-epochs.model'.format(LR, 'alexnetv2',EPOCHS)

video = cv2.VideoCapture(0)
video.set (cv2.CAP_PROP_FRAME_WIDTH,320)
video.set (cv2.CAP_PROP_FRAME_HEIGHT,240)

def straight():
    print('straight')

def left():
    print('left')

def right():
    print('right')
    
model = alexnet(WIDTH, HEIGHT, LR)
model.load(MODEL_NAME)

def main():
    last_time = time.time()
    while(True):
        
        ret , image = video.read()
        cv2.imshow("image",image)
        print('loop took {} seconds'.format(time.time()-last_time))
        last_time = time.time()
        screen = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        prediction = model.predict([screen.reshape(320,240,1)])[0]
        print(prediction)

        turn_thresh = .75
        fwd_thresh = 0.70

        if prediction[1] > fwd_thresh:
            straight()
        elif prediction[0] > turn_thresh:
            left()
        elif prediction[2] > turn_thresh:
            right()
        else:
            straight()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break 

main()       










