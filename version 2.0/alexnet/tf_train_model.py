#!/usr/bin/python3 
__author__ = 'dj140'

import numpy as np
from alexnet import alexnet
from sklearn.model_selection import train_test_split 
import glob

WIDTH = 320
HEIGHT = 240
LR = 1e-3
EPOCHS = 8
MODEL_NAME = 'tf-{}-{}-{}-epochs.model'.format(LR, 'alexnetv2',EPOCHS)

model = alexnet(WIDTH, HEIGHT, LR)

#path = "training_data/*.npy"
data = glob.glob('training_data/*.npy')
#for data in data_path:
train_data = np.load(data[0])

train,test = train_test_split(train_data,test_size=0.3)
#train = train_data[:-50]
#test = train_data[-50:]
print(len(train))
print(len(test))
X = np.array([i[0] for i in train]).reshape(-1,WIDTH,HEIGHT,1)
Y = [i[1] for i in train]
#print(Y)

test_x = np.array([i[0] for i in test]).reshape(-1,WIDTH,HEIGHT,1)
test_y = [i[1] for i in test]

model.fit({'input': X}, {'targets': Y}, n_epoch=EPOCHS, validation_set=({'input': test_x}, {'targets': test_y}), 
    snapshot_step=500, show_metric=True, run_id=MODEL_NAME)

# tensorboard --logdir=log

model.save(MODEL_NAME)
