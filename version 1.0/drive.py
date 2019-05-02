#!/usr/bin/python3

import serial
import time
from curtsies import Input
msg = """
检测按键输入，控制小车
---------------------------
Moving around:
         UP

    LEFT    RIGHT
        
        DOWN
---------------------------
加减电机速度：
'z'加速    'x'减速 
---------------------------
'q' or <ESC>退出程序
"""
def main():
    ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
    print(msg)
    with Input() as input_generator:
        for e in input_generator:
            if e == '<UP>':
                ser.write('w'.encode())
                time.sleep(0.5)
                ser.write('p'.encode())
            elif e == '<DOWN>':
                ser.write('s'.encode())
                time.sleep(0.5)
                ser.write('p'.encode())
            elif e == '<LEFT>':
                #print("向前左转")
                ser.write('a'.encode())
                time.sleep(0.5)
                ser.write('p'.encode())
            elif e == '<RIGHT>':
                #print("向前右转")
                ser.write('d'.encode())
                time.sleep(0.5)
                ser.write('p'.encode())

            elif e == 'a':
                ser.write('q'.encode())
            elif e == 'd':
                ser.write('e'.encode())
            elif e == 'z':
                ser.write('z'.encode())
                #print("电机速度增加")
            elif e == 'x':
                ser.write('x'.encode())
                #print("电机速度降低")

            elif e == '<ESC>' or 'q':
                break

if __name__ == '__main__':
    main()
