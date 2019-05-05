#!/usr/bin/python3
#用python3运行，编码为UTF-8，避免中文乱码
#coding = UTF-8
#作者，装逼用的，不用管
__author__ = 'dj140'
import sys
#解决ROS和python冲突
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')
import time
#导入numpy，改名为np，方便打字
import numpy as np
#导入串口，和stm32通信用的
import serial
#导入pygame，检测按键输入用的
import pygame
#从pygame.locals中导入所有东西
from pygame.locals import *
import time 
import os 



class collectdata(object):
    #初始化函数
    def __init__(self, serial_port, video_port):

        #opencv库中的摄像头捕捉,video(0)
        self.video = cv2.VideoCapture(video_port)
        #设置分辨率为320*240
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        #设置串口号，波特率
        self.ser = serial.Serial(serial_port, 115200, timeout=1)
        self.stm32=True 
        #初始化标签，前进，左右
        self.w = [1,0,0]
        self.a = [0,1,0]
        self.d = [0,0,1]
        
        #pygame初始化，窗口大小设为250*250
        pygame.init()
        pygame.display.set_mode((250,250))
    #采集图像的函数
    def collect(self):
        print("开始收集图像")
        print("按'q'键退出")
        #开始计时，计算函数用的时间
        start = cv2.getTickCount()
        #初始化四个变量，用来统计帧数
        front_frame = 0
        left_frame = 0
        right_frame = 0
        total_frame = 0
        save_frame = 0
        #初始化两个numpy数组用来储存要保存图像，里面的两个参数一个是矩阵的高，一个是长
        train_data = []

        try:
            #当self.stm32返回值为真时候，执行下面语句
            while self.stm32:
                #读取摄像头传过来的数据，check是bool值验证有没有打开摄像头，frame是帧相当于一个数组
                check, image = self.video.read()
                #把传来的彩色图像转化为灰度图
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #获取图像矩阵的高和长
                #height, width = grey.shape
                #把矩阵高度减半，相当于从图像中间砍了一半
                #half = grey[int(height/2):height, :]
                #把这个砍了一半的图像矩阵重新变成高为1，长为120*320的矩阵，类型为浮点数
                #temp_array = half 
                
                total_frame += 1

                #print(temp_array)
                cv2.imshow("webcam", image)
                #print(grey.shape)
                #cv2.imshow("grey", grey)
                #cv2.imshow("half", half)
                #按键检测部分
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        key_input = pygame.key.get_pressed()

                        if key_input[pygame.K_UP] or key_input[pygame.K_w]:
                            #记录保存里多少帧
                            front_frame += 1
                            print("前进",front_frame)                    
                            #把图像数组保存起来
                            train_data.append([rgb,self.w])
                            #通过串口给stm32写数据
                            self.ser.write('w'.encode())

                        elif key_input[pygame.K_LEFT]:
                            left_frame += 1
                            print("左转",left_frame)
                            train_data.append([rgb,self.a])
                            self.ser.write('d'.encode())

                        elif key_input[pygame.K_RIGHT]:
                            right_frame += 1
                            print("右转",right_frame)
                            train_data.append([rgb,self.d])
                            self.ser.write('a'.encode())
                        
                        elif key_input[pygame.K_q]:
                            print("退出程序")
                            self.stm32 = False 
                            self.ser.write('p'.encode())
                            self.ser.close()
                            break

                    elif event.type == pygame.KEYUP:
                        self.ser.write('p'.encode())
                        
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            #file_name = str(int(time.time()))
            file_name = str((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            directory = "training_data"

            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                np.save(directory + '/' + file_name + '.npy', train_data)
            except IOError as e:
                print(e)
             
            end = cv2.getTickCount()
            save_frame = front_frame + right_frame + left_frame 
            print("程序用时：%.2fs"%((end-start)/cv2.getTickFrequency()))
            print("前进,左转,右转,帧数: ",front_frame,left_frame,right_frame)
            print("总帧数：",total_frame)
            print("保存帧数：",save_frame)
        finally:
            self.video.release()
            cv2.destroyAllWindows()

#类似于判断程序名字是不是main，是的话就执行下面的代码，暂时理解为程序的入口ok
if __name__ == '__main__':
    #串口号，相当于电脑的com口
    sp = "/dev/ttyUSB0"
    video = 0
    #给init函数赋初值
    dj = collectdata(sp,video)
    #执行collect函数
    dj.collect()
