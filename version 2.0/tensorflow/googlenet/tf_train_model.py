#!/usr/bin/python3 
__author__ = 'dj140'

from models import inception_v3 as googlenet
import numpy as np
from random import shuffle
from sklearn.model_selection import train_test_split 
import glob

WIDTH = 320
HEIGHT = 240
LR = 1e-3
EPOCHS = 8
MODEL_NAME = 'tf-{}-{}-{}-epochs.model'.format(LR, 'google',EPOCHS)
model = googlenet(WIDTH, HEIGHT, 3, LR, output=3, model_name=MODEL_NAME)

#path = "training_data/*.npy"
data_path = glob.glob('training_data/*.npy')
for data in data_path:
    train_data = np.load(data)

shuffle(train_data)
train,test = train_test_split(train_data,test_size=0.3)
#train = train_data[:-50]
#test = train_data[-50:]

X = np.array([i[0] for i in train]).reshape(-1,WIDTH,HEIGHT,3)
Y = [i[1] for i in train]

test_x = np.array([i[0] for i in test]).reshape(-1,WIDTH,HEIGHT,3)
test_y = [i[1] for i in test]


model.fit({'input': X}, {'targets': Y}, n_epoch=EPOCHS, validation_set=({'input': test_x}, {'targets': test_y}), 
    snapshot_step=2500, show_metric=True, run_id=MODEL_NAME)

# tensorboard --logdir=/log
print("训练完成！！！模型保存在log目录下")
model.save(MODEL_NAME)
