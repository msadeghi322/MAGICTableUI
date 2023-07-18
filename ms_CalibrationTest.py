#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 17:50:31 2019

@author: mohsensadeghi
"""
import cv2
import imutils
from save import save_output_at, save_video, save_dataframe
import time
from shape_detection import detect_circle, detect_obstacles, detectShapesInTable
import pickle
import numpy as np
import glob
import os
import csv
import pygame
import pandas as pd
import scipy.io as sio
from imutils.video import WebcamVideoStream




# Sound effect setting: just to make a camera click sound --------------------
pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.mixer.init()
pygame.init() #turn all of pygame on.
local_path = os.getcwd()
print(local_path)
BeepFiles_path  = os.path.join(str(local_path), "resources","sounds","Beeps")
if not os.path.exists(BeepFiles_path):
    os.makedirs(BeepFiles_path)
Beep1 = pygame.mixer.Sound(os.path.join(str(BeepFiles_path), "cam.wav"))
#-------------------------------------------------------------------------------   





# ------------------------------  take pictures of chess board ----------------

NumPics = 50
time.sleep(.1)
cam = WebcamVideoStream(src=0).start()
PicPath= save_output_at("TestFolder\\","Raw Pictures") # the \\ sign to separate folders might only be ok for PC, it might give error if used for mac, so something else might work for mac like \ 
print("====== Taking %d Pictures======"%NumPics)
d=0
while d<NumPics:
    pics = cam.read()
    filename = os.path.join(PicPath,"pic_%d.jpg"%d)
    cv2.imwrite(filename, pics)
    d+=1
    Beep1.play()
    cv2.imshow("pic",pics)
    cv2.waitKey(0)

#-------------------------------------------------------------------------------   
    
    
# ------------------------ Setting up calibration ------------------------------
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((9*6,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

#  find and load previously taken images 
images = glob.glob(os.path.join(str(PicPath),'*.jpg'))

Corners_df = pd.DataFrame()
FoundCorners = [] # This is a flag we use later to exclude pictures in which the corners were not found
d=1
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (9,6),None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        
        FoundCorners.append(True)
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)
        
        # generating a data frame to save later
        dd = pd.DataFrame(corners2[:,0,:])
        Corners_df = Corners_df.append(dd)
        
        # Draw and display the corners
#        img = cv2.drawChessboardCorners(img, (9,6), corners2,ret)
#        cv2.imshow('img',img)
#        cv2.waitKey(500)
    else:
        print("The corners were not found for this picture:",fname )
        FoundCorners.append(False)
    print('Loading image %d completed...'%d)
    d+=1    
        
# Done with the cam. so release and close
cam.stop()
cv2.destroyAllWindows()

# Calibrate now
print('Calibration started now...')
StartTime = time.time()
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
print('Calibration time.................: ', time.time()-StartTime)
#-------------------------------------------------------------------------------










#------------------ Some analysis -----------------------------------------
# save the 2D raw coordinates of corners as csv
Corners_df.columns= ['X','Y']
Corners_df.to_csv(os.path.join(str(PicPath),'RawCoordinates.csv'))



# There are two ways of testing how the undistorsion works: 
# 1. load images again, undistort the images, and find the corners for the undistorted images
# 2. load the csv of corner data, use undistortPoints function and directly calculate the undistorted coordinates


 



GG=0
kk=0
for i in range(len(imgpoints)):
    for j in range(len(imgpoints[i])-1):
        DD = cv2.norm(Corners_df.values[j,:], Corners_df.values[j+1,:], cv2.NORM_L2)
        #print("Distance  %d"%i,",%d: "%j , f'{DD:.3f} ')
        if DD<50:
            GG+=DD
            kk+=1

print("The average checkboard unit dist---: " , GG/kk)



# load one picture
CornersNew_df = pd.DataFrame()

d=0
cc=0
for fname in images:
    
    # If found, add object points, image points (after refining them)
    if FoundCorners[d]==True:  # only if the original picture is detectable
        img = cv2.imread(fname)
        dst = cv2.undistort(img, mtx, dist, None, mtx)
        gray = cv2.cvtColor(dst,cv2.COLOR_BGR2GRAY)
        ret, corn_new = cv2.findChessboardCorners(gray, (9,6),None)
        filename = os.path.join(str(fname[:-4])+'_Undist.jpg')
        cv2.imwrite(filename, dst)
        
        if ret == True:
            corners2_new = cv2.cornerSubPix(gray,corn_new,(11,11),(-1,-1),criteria)
            dd = pd.DataFrame(corners2_new[:,0,:])
            CornersNew_df = CornersNew_df.append(dd)
        else:
            corners2_new = imgpoints[cc]
            dd = pd.DataFrame(corners2_new[:,0,:])
            CornersNew_df = CornersNew_df.append(dd)
            print("Corners in undistorted picture were not found for this pic:",fname)
            print("Instead, corners from the original picture were used" )
        cc+=1
    d+=1
    print('Undistortion of image %d completed...'%d)
            
CornersNew_df.columns= ['X','Y']
CornersNew_df.to_csv(os.path.join(str(PicPath),'UndistCoordinates.csv'))


        

GG=0
kk=0
for i in range(len(imgpoints)):
    for j in range(len(imgpoints[i])-1):
        DD = cv2.norm(CornersNew_df.values[j,:], CornersNew_df.values[j+1,:], cv2.NORM_L2)
        #print("Distance  %d"%i,",%d: "%j , f'{DD:.3f} ')
        if DD<50:
            GG+=DD
            kk+=1

print("The average checkboard unit dist---: " , GG/kk)






mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error

#print ("total error: ", mean_error/len(objpoints))



























