#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 17:15:09 2019

@author: mohsensadeghi
"""


import sys
import os, inspect

# sys.path.insert(0, "/MS/")
# sys.path.append('/MS/')

# sys.path.append('../')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))






import time                     # time dependent functions (ms)
from MyClass import MyClass
import cv2
from MS.ms_Timer import ms_Timer 
from main_ms import selectROI


A = ms_Timer()
time.sleep(.5)
G = A.GetTime()

A.Reset()
B = A.GetTime()
time.sleep(.5)
C = A.GetTime()

A.Tic()
T = A.tic_time

time.sleep(.5)
D = A.Toc()


time.sleep(.5)
E = A.Toc()

time.sleep(.5)
F = A.Toc()


print("Get time after 0.5sed:" , G )
print("Get time after reset:", B )
print("Get time again after .5sec:", C )
print("first time tic", T )
print("First Toc after .5sec:", D )
print("Second Toc after 0.5sec from first Toc:", E )
print("Second Toc after 0.5sec from socond Toc:", F )




class someclass:
    pass

STATE = someclass()
STATE.A1 = 1
STATE.A2 = 2
STATE.A3 = 3
STATE.A4 = ms_Timer()

STATE.A4.Reset()
time.sleep(.2)
print("A4 time",STATE.A4.GetTime())    



A = ms_Timer()
print("------blah blah------", A.tic_time , A.LastToc)
B = A.GetTime()
print("print time:",B)







# A = MyClass()
# print("A is equal to", A.a1 , A.a2 , A.a3)
# 
# B = A.func_1()
# print("B is equal to",  A.a1 , A.a2 , A.a3)
# 
# 
# C = A.func_2()
# print("C is equal to", A.a1, A.a2, A.a3)
# 
# 
# cam = cv2.VideoCapture(0)
# 
# window = "OpenCV_window"
# cam = cv2.VideoCapture(0)
# print(cam, "is open:", cam.isOpened())
# 
# cv2.namedWindow(window)
# ready, frame = cam.read()
# print("Frame ready:", ready)
# 
# cv2.imshow(window, frame)
# cv2.waitKey(1)
# input("Press ENTER to close window and camera.") 
# 
# cv2.destroyAllWindows()
# cam.release()
# 
# OPENCV_VIDEOIO_PRIORITY_MSMF=0 
# 





# =============================================================================
# 
# class structtype():
#     pass
# 
# 
# global STATE
# 
# STATE = structtype;
# 
# 
# 
# STATE.INITIALIZE    = 1;
# STATE.SETUP         = 2;
# STATE.HOME          = 3;
# STATE.START         = 4;
# STATE.DELAY         = 5;
# STATE.STIMULUS      = 6;
# STATE.GO            = 7;
# STATE.MOVEWAIT      = 8;
# STATE.MOVING        = 9;
# STATE.FINISH        = 10;
# STATE.NEXT          = 11;
# STATE.INTERTRIAL    = 12;
# STATE.EXIT          = 13;
# STATE.TIMEOUT       = 14;
# STATE.ERROR         = 15;
# STATE.REST          = 16;
# STATE.CALIBRATION   = 17;
# STATE.FEEDBACK      = 18;
# 
# 
# STATE.From          = 0;
# STATE.To            = 0;
# STATE.Last          = 1;
# STATE.Current       = 1;
# 
# STATE.Reset         = time.time();
# time.sleep(2)
# STATE.Timer         = time.time()-STATE.Reset;
# 
# 
# print("Start time",STATE.Reset , "time",STATE.Timer)
# 
# 
# =============================================================================

# =============================================================================
# for i in AllStates:
#     STATE.AllStates[i] = i;
#     print("STATE",STATE.AllStates[i])
# 
# =============================================================================
    



