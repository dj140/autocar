#!/usr/bin/python3
 
# adapted from https://github.com/recantha/EduKit3-RC-Keyboard/blob/master/rc_keyboard.py
 
import sys, termios, tty, os, time
 
def key_check():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    #try:
    tty.setraw(sys.stdin.fileno())
    keys = sys.stdin.read(1)
    #finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return keys

  
