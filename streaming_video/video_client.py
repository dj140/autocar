#!/usr/bin/python3 
import socket
import time
import cv2


client_sock = socket.socket()
client_sock.connect(('192.168.123.120', 50002))
#We are going to 'write' to a file in 'binary' mode
conn = client_sock.makefile('wb')

try:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,320)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,240)

    start = time.time()

    while(cap.isOpened()):
        conn.flush()
        ret, frame = cap.read()
        byteImage = frame.tobytes()
        conn.write(byteImage)


finally:
    finish = time.time()
    cap.release()
    client_sock.close()
    conn.close()

