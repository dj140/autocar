#!/usr/bin/python3 
import numpy as np
import glob
import sys 
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')
#path = 'training_data/*.npy'
data_path = glob.glob('training_data/*.npy')
for data in data_path:
    train_data = np.load(data)
#print(train_data)
for data in train_data:
    img = data[0] 
    print(img.shape)
    choice = data[1]
    print(choice)
    cv2.imshow('test',img)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
