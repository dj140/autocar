import socket
import sys
ros_path = '/opt/ros/kinetic/lib/python2.7/dist-packages'
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append('/opt/ros/kinetic/lib/python2.7/dist-packages')

#opencv库中的摄像头捕捉,video(0)
video = cv2.VideoCapture(0)
#设置分辨率为320*240
video.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

HOST = 'localhost'
PORT = 9876
ADDR = (HOST,PORT)
BUFSIZE = 4096
while True:
	chack,image = video.read()
	ret, jpeg = cv2.imencode('.jpg', image)
	bytes = jpeg.tobytes()
	#cv2.imshow("rgb",image)
	#print(len(bytes))

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(ADDR)

	client.send(bytes)
	#if cv2.waitKey(1) & 0xFF == ord('q'):
	#	break
	client.close()
