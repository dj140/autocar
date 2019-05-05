#!/usr/bin/python3
import os
import sys
import time
from alexnet import alexnet
from rc_control import  RCControl, ObjectDetection

ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')

class autopilot(object):
    rc_car = RCControl("/dev/ttyUSB0")
    model_name = 'obj_model/ssd_mobilenet_v1_coco_11_06_2017'
    check_point = '/frozen_inference_graph.pb'
    label = 'mscoco_label_map.pbtxt'
    num_class = 90
    obj_detection = ObjectDetection(model_name,check_point,label,num_class)
    def __init__(self, width, height, color, video_port):
        LR = 1e-3
        EPOCHS = 8
        MODEL_NAME = 'tf-{}-{}-{}-epochs.model'.format(LR, 'alexnetv2',EPOCHS)
        self.WIDTH = width
        self.HEIGHT = height
        self.COLOR = color
        self.video = cv2.VideoCapture(video_port)
        self.video.set (cv2.CAP_PROP_FRAME_WIDTH,640)
        self.video.set (cv2.CAP_PROP_FRAME_HEIGHT,480)
        self.webcam = True
        self.model = alexnet(width, height, LR)
        self.model.load(MODEL_NAME)

    def auto(self):
        last_time = time.time()
        while(True):
            ret , image_np = self.video.read()
            self.obj_detection.detect(image_np)
            cv2.imshow("image",image_np)
            print('当前帧数为{} FPS'.format(int(1/(time.time()-last_time))))
            last_time = time.time()

            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            gray_resize = cv2.resize(gray,(self.WIDTH,self.HEIGHT))
            #print(resize.shape)
            prediction = self.model.predict([gray_resize.reshape(self.WIDTH,self.HEIGHT,self.COLOR)])[0]
            print('预测结果:',prediction)


            turn_thresh = .75
            fwd_thresh = 0.70

            if prediction[0] > fwd_thresh:
                self.rc_car.straight()
            elif prediction[1] > turn_thresh:
                self.rc_car.left()
            elif prediction[2] > turn_thresh:
                self.rc_car.right()
            else:
                self.rc_car.straight()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == '__main__':
    #摄像头信息
    w = 320
    h = 240
    c = 1
    #使用摄像头0
    video = 0
    #给init函数赋初值
    dj = autopilot(w,h,c,video)
    #执行auto函数
    dj.auto()
