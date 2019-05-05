#!/usr/bin/python3
import os
import sys
import time
import serial
import random
import numpy as np
import tensorflow as tf
from alexnet import alexnet
from utils import label_map_util
from utils import visualization_utils as vis_util

ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')

video = cv2.VideoCapture(1)
video.set (cv2.CAP_PROP_FRAME_WIDTH,1024)
video.set (cv2.CAP_PROP_FRAME_HEIGHT,720)
serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)


# model name.
OBJ_MODEL_NAME = 'obj_model/traffic_light_14389'
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = OBJ_MODEL_NAME + '/frozen_inference_graph.pb'
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('label', 'object-detection.pbtxt')

NUM_CLASSES = 1

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

# Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def straight():
    serial_port.write('w'.encode())
    print('前进/straight')

def left():
    serial_port.write('a'.encode())
    print('左转/left')

def right():
    serial_port.write('d'.encode())
    print('右转/right')

WIDTH = 320
HEIGHT = 240
COLOR = 1
LR = 1e-3
EPOCHS = 8
MODEL_NAME = 'tf-{}-{}-{}-epochs.model'.format(LR, 'alexnetv2',EPOCHS)

model = alexnet(WIDTH, HEIGHT, LR)
model.load(MODEL_NAME)

def main():
    last_time = time.time()
    with detection_graph.as_default():
      with tf.Session(graph=detection_graph) as sess:
        while(True):
          ret , image_np = video.read()
          image_np_expanded = np.expand_dims(image_np, axis=0)
          image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
          # Each box represents a part of the image where a particular object was detected.
          boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
          # Each score represent how level of confidence for each of the objects.
          # Score is shown on the result image, together with the class label.
          scores = detection_graph.get_tensor_by_name('detection_scores:0')
          classes = detection_graph.get_tensor_by_name('detection_classes:0')
          num_detections = detection_graph.get_tensor_by_name('num_detections:0')
          # Actual detection.
          (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
          # Visualization of the results of a detection.
          vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=8)
          cv2.imshow("image",image_np)
          print('当前帧数为{} FPS'.format(int(1/(time.time()-last_time))))
          last_time = time.time()

          image = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
          image_resize = cv2.resize(image,(WIDTH,HEIGHT))
          prediction = model.predict([image_resize.reshape(WIDTH,HEIGHT,COLOR)])[0]
          print('预测结果:',prediction)

          turn_thresh = .75
          fwd_thresh = 0.70

          if prediction[0] > fwd_thresh:
              straight()
          elif prediction[1] > turn_thresh:
              left()
          elif prediction[2] > turn_thresh:
              right()
          else:
              straight()

          if cv2.waitKey(1) & 0xFF == ord('q'):
              break

if __name__ == '__main__':
    main()
