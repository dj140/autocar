#!/usr/bin/python3

import numpy as np 
from random import shuffle
from collections import Counter
import pandas as pd 

#path = "training_data/*.npy"
data_path = glob.glob('training_data/*.npy')
for data in data_path:
    train_data = np.load(data)

#df = pd.DataFrame(train_data)
#print(df.head())
#print(Counter(df[1].apply(str)))

lefts = []
rights = []
forwards = []

shuffle(train_data)

for data in train_data:
    img = data[0]
    choice = data[1]

    if choice == [1,0,0]:
        forwards.append([img,choice])
    elif choice == [0,1,0]:
        lefts.append([img,choice])
    elif choice == [0,0,1]:
        rights.append([img,choice])
    else:
        print('no matches')


forwards = forwards[:len(lefts)][:len(rights)]
lefts = lefts[:len(forwards)]
rights = rights[:len(forwards)]
print(len(forwards))
print(len(lefts))
print(len(rights))
final_data = forwards + lefts + rights
shuffle(final_data)

np.save('training_data_v2.npy', final_data)
