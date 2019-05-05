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

video = cv2.VideoCapture(0)
video.set (cv2.CAP_PROP_FRAME_WIDTH,640)
video.set (cv2.CAP_PROP_FRAME_HEIGHT,480)
serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)


# model name.
OBJ_MODEL_NAME = 'obj_model/ssd_mobilenet_v1_coco_11_06_2017'
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = OBJ_MODEL_NAME + '/frozen_inference_graph.pb'
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('label', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

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

          for i,b in enumerate(boxes[0]):
          # 3代表汽车，6代表巴士，8代表货车，10代表交通灯
            if classes[0][i] == 3 or classes[0][i] == 6 or classes[0][i] == 8:
              if scores[0][i] >= 0.5:
                mid_x = (boxes[0][i][1]+boxes[0][i][3])/2
                mid_y = (boxes[0][i][0]+boxes[0][i][2])/2
                apx_distance = round(((1 - (boxes[0][i][3] - boxes[0][i][1]))**4),1)
                cv2.putText(image_np, '{}'.format(apx_distance), (int(mid_x*800),int(mid_y*450)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

                if apx_distance <=0.5:
                  if mid_x > 0.3 and mid_x < 0.7:
                    cv2.putText(image_np, 'WARNING!!!', (int(mid_x*800)-150,int(mid_y*450)-50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)

            if classes[0][i] == 10:
              if scores[0][i] >= 0.5:
                mid_x = (boxes[0][i][1]+boxes[0][i][3])/2
                mid_y = (boxes[0][i][0]+boxes[0][i][2])/2
                apx_distance = round(((1 - (boxes[0][i][3] - boxes[0][i][1]))**4),1)
                cv2.putText(image_np, '{}'.format(apx_distance), (int(mid_x*800),int(mid_y*450)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

                if apx_distance <=0.5:
                  if mid_x > 0.3 and mid_x < 0.7:
                    cv2.putText(image_np, 'TRAFFIC_LIGHT!!!', (int(mid_x*800)-150,int(mid_y*450)-50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)

          cv2.imshow("image",image_np)
          print('当前帧数为{} FPS'.format(int(1/(time.time()-last_time))))
          last_time = time.time()

          gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
          gray_resize = cv2.resize(gray,(WIDTH,HEIGHT))
          #print(resize.shape)
          prediction = model.predict([gray_resize.reshape(WIDTH,HEIGHT,COLOR)])[0]
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
