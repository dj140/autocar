import socket
import sys
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
import numpy as np
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')
HOST = ''
PORT = 9876
ADDR = (HOST,PORT)
BUFSIZE = 4096

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind(ADDR)
serv.listen(5)

print ('listening ...')

while True:
  conn, addr = serv.accept()
  print ('client connected ... ', addr)
  while True: 
    stream_bytes = b' '
    stream_bytes += conn.recv(4096)
   # data = conn.recv(BUFSIZE)
    image = cv2.imdecode(np.frombuffer(stream_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
   
    print(image)
