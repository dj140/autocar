#!/usr/bin/python3
#coding = UTF-8
__author__= 'dj140'
import os
import math
import serial
import numpy as np
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util

class RCControl(object):

    def __init__(self, serial_port):
        self.serial_port = serial.Serial(serial_port, 115200, timeout=1)

    def straight(self):
        self.serial_port.write('w'.encode())
        print('前进')
    def left(self):
        self.serial_port.write('a'.encode())
        print('左转')
    def right(self):
        self.serial_port.write('d'.encode())
        print('右转')
    def stop(self):
        self.serial_port.write('p'.encode())
        print('停车')

class DistanceToCamera(object):

    def __init__(self):
        # camera params
        self.alpha = 8.0 * math.pi / 180    # degree measured manually
        self.v0 = 119.865631204             # from camera matrix
        self.ay = 332.262498472             # from camera matrix

    def calculate(self, v, h, x_shift, image):
        # compute and return the distance from the target point to the camera
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
        if d > 0:
            cv2.putText(image, "%.1fcm" % d,
                        (image.shape[1] - x_shift, image.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return d

class ObjectDetection(object):
    def __init__(self,model_name,ckpt,label,num_class):
              # model name.
        self.OBJ_MODEL_NAME = model_name
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        self.PATH_TO_CKPT = self.OBJ_MODEL_NAME + ckpt
        # List of the strings that is used to add correct label for each box.
        self.PATH_TO_LABELS = os.path.join('label', label)
        self.NUM_CLASSES = num_class

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
          od_graph_def = tf.GraphDef()
          with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
         # Loading label map
         # Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

        label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

    def detect(self, image_np):
        with self.detection_graph.as_default():
          with tf.Session(graph=self.detection_graph) as sess:
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
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
                        self.category_index,
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
