#!/usr/bin/python3
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util

ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')
cap = cv2.VideoCapture(1)

# model name
MODEL_NAME = 'traffic_light_14389'
# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'object-detection.pbtxt')

NUM_CLASSES = 1

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')

# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

with detection_graph.as_default():
  with tf.Session(graph=detection_graph) as sess:
    while True:
      ret, image_np = cap.read()
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
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
        if classes[0][i] == 1:
          if scores[0][i] >= 0.5:
            mid_x = (boxes[0][i][1]+boxes[0][i][3])
            mid_y = (boxes[0][i][0]+boxes[0][i][2])
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            print(int(mid_x*800),int(mid_y*450))
        #roi = gray[int(mid_x*800),int(mid_y*450)]
        #mask = cv2.GaussianBlur(roi, (25, 25), 0)
        #(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)

        # check if light is on
        #if maxVal - minVal > 150:
        #  cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)

            # Red light
        #  if 1.0 / 8 * (height - 30) < maxLoc[1] < 4.0 / 8 * (height - 30):
        #    cv2.putText(image_np, 'Red', (int(mid_x*800) + 5, int(mid_y*450) - 5),                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

      cv2.imshow('object detection', cv2.resize(image_np, (800,600)))
      if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
