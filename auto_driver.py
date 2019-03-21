#!/usr/bin/python3
#coding = UTF-8
__author__ = 'dj140'

import sys 
import numpy as np
import cv2

from model import NeuralNetwork
from rc_driver_helper import *

#sensor_data = None
# 超声波传感器的代码，还没搞好
#class SensorDataHandler(socketserver.BaseRequestHandler):

#    data = " "

#    def handle(self):
#        global sensor_data
#        while self.data:
#            self.data = self.request.recv(1024)
#            sensor_data = round(float(self.data), 1)
#            # print "{} sent:".format(self.client_address[0])
#            print(sensor_data)
   
class Autocontol(object):
    
    # h1: 停止标志的高度
    # h2: 红绿灯的高度
    # 单位cm
    h1 = 5.5  
    h2 = 5.5
    # 导入训练好的神经模型
    nn = NeuralNetwork()
    nn.load_model("saved_model/nn_model.xml")

    obj_detection = ObjectDetection()
    #stm32串口号
    rc_car = RCControl("/dev/ttyUSB0") 

    # cascade classifiers opencv中的一个功能，用来识别物体的
    stop_cascade = cv2.CascadeClassifier("cascade_xml/stop_sign.xml")
    light_cascade = cv2.CascadeClassifier("cascade_xml/traffic_light.xml")

    d_to_camera = DistanceToCamera()
    d_stop_sign = 25
    d_light = 25

    stop_start = 0  # 在遇到停止标志的时候计时
    stop_finish = 0
    stop_time = 0
    drive_time_after_stop = 0

    def auto(self):
        
        stop_flag = False
        stop_sign_active = True

        try:
            #打开摄像头
            video =cv2.VideoCapture(0)
            #设置分辨率320*240
            video.set(cv2.CAP_PROP_FRAME_WIDTH,320)
            video.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
            #设置帧率30
            video.set(cv2.CAP_PROP_FPS,30)
            
            while True:
                #check是检测有没有打开摄像头，有则返回1，无0
                #image是图像
                check, image  = video.read()
                #转化为灰度图
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                #图像切半
                height, width = gray.shape
                roi = gray[int(height/2):height, :]
                # 物体识别
                v_param1 = self.obj_detection.detect(self.stop_cascade, gray, image)
                v_param2 = self.obj_detection.detect(self.light_cascade, gray, image)
                # 距离测量
                if v_param1 > 0 or v_param2 > 0:
                    d1 = self.d_to_camera.calculate(v_param1, self.h1, 300, image)
                    d2 = self.d_to_camera.calculate(v_param2, self.h2, 100, image)
                    self.d_stop_sign = d1
                    self.d_light = d2
                #显示图像
                cv2.imshow('image', image)
                # cv2.imshow('mlp_image', roi)
                # 将image矩阵化为向量形式
                image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
                #神经网络预测
                prediction = self.nn.predict(image_array)

                # 当停止标志在0到25cm的距离
                # 并且stop_sign_active标志位为真的时候，车停止
                if 0 < self.d_stop_sign < 25 and stop_sign_active:
                    print("检测到停车标志！！！")
                    self.rc_car.stop()

                    # 遇到停止标志的时候开始计时
                    if stop_flag is False:
                        self.stop_start = cv2.getTickCount()
                        #停车标志位设为真，下一次程序再跑到这里时间就不会从头开始
                        stop_flag = True 
                    self.stop_finish = cv2.getTickCount()
                    #计算时间，时间基本是程序再一次跑到这个地方用的时间
                    self.stop_time = (self.stop_finish - self.stop_start)/ cv2.getTickFrequency()
                    print("Stop time: %.2fs" % self.stop_time)

                    #当在停车标志停了5s，就开车 
                    if self.stop_time > 5:
                        print("停了5s，准备开车")
                        stop_flag = False
                        stop_sign_active = False
                #当检测到红绿灯再前方的时候
                elif 0 < self.d_light < 30:
                    #print("注意前方红绿灯！！！")
                    if self.obj_detection.red_light:
                        print("红灯危险！！")
                        self.rc_car.stop()
                    elif self.obj_detection.green_light:
                        print("绿灯安全")
                        pass
                    elif self.obj_detection.yellow_light:
                        print("黄灯慢行！")
                        pass

                    self.d_light = 30
                    self.obj_detection.red_light = False
                    self.obj_detection.green_light = False
                    self.obj_detection.yellow_light = False
                #如果没遇到红绿灯，没遇到停车标志，则执行自动驾驶程序
                else:
                    self.rc_car.steer(prediction)
                    self.stop_start = cv2.getTickCount()
                    self.d_stop_sign = 25
                    #下面这一部分是，判断距离上一次遇到停止标志有没有超过5s
                    #如果超过了则把标志位重新设为真，以便下一次遇到停止标志的时候可以停车
                    if stop_sign_active is False:
                        self.drive_time_after_stop = (self.stop_start - self.stop_finish) / cv2.getTickFrequency()
                        if self.drive_time_after_stop > 5:
                            stop_sign_active = True
                #按q键退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("car stopped")
                    self.rc_car.stop()
                    break
        finally:
            cv2.destroyAllWindows()
            sys.exit()


if __name__ == '__main__':

    dj = Autocontol()
    dj.auto()
