from models import inception_v3 as googlenet
import numpy as np
from random import shuffle

#from alexnet import alexnet
#from sklearn.model_selection import train_test_split
WIDTH = 320
HEIGHT = 240
LR = 1e-3
EPOCHS = 8
MODEL_NAME = 'tf-{}-{}-{}-epochs.model'.format(LR, 'google',EPOCHS)
model = googlenet(WIDTH, HEIGHT, 3, LR, output=3, model_name=MODEL_NAME)

#model = alexnet(WIDTH, HEIGHT, LR)

train_data = np.load('2.npy')
shuffle(train_data)
train = train_data[:-50]
test = train_data[-50:]

X = np.array([i[0] for i in train]).reshape(-1,WIDTH,HEIGHT,3)
Y = [i[1] for i in train]

test_x = np.array([i[0] for i in test]).reshape(-1,WIDTH,HEIGHT,3)
test_y = [i[1] for i in test]
#train,test = train_test_split(train_data,test_size=0.3)
#print(len(train))
#print(len(test))
#X = np.array([i[0] for i in train]).reshape(-1,WIDTH,HEIGHT,1)
#Y = [i[1] for i in train]

#test_x = np.array([i[0] for i in test]).reshape(-1,WIDTH,HEIGHT,1)
#test_y = [i[1] for i in test]

model.fit({'input': X}, {'targets': Y}, n_epoch=EPOCHS, validation_set=({'input': test_x}, {'targets': test_y}), 
    snapshot_step=2500, show_metric=True, run_id=MODEL_NAME)

# tensorboard --logdir=foo:C:/Users/H/Desktop/ai-gaming/log
print("保存模型")
model.save(MODEL_NAME)
