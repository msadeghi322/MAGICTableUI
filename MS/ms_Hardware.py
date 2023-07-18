#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:02:06 2019

@author: mohsensadeghi
"""

import math
from MS.ms_Timer import ms_Timer
from MS.ms_ShapeTracking import ellipse_dual_tracking, ellipse_tracking, circle_tracking
import os
import sys
import cv2
import imutils
from save import save_output_at, save_video, save_dataframe
import time
from shape_detection import detect_circle, detect_obstacles, detectShapesInTable
import pickle
import numpy as np
import glob
import csv
from imutils.video import FileVideoStream
from imutils.video import WebcamVideoStream
from imutils.video import VideoStream
from imutils.video import FPS
from threading import Thread    # Thread allows for running multiple independent parts of a code almost simultaneously (ms)




sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from main_ms import main_ms








class ms_Hardware:
    
    # build a class to resemble the structure data type in matlab
    
    def __init__(HW,Args, camera_port, TableSize , ColourRange, *args):
        
        
        # read arguments and camera port
        HW.args          = Args
        HW.camera_port   = camera_port
        HW.TableSize     = TableSize
        HW.ColourRange   = ColourRange
        HW.circles       = TableSize.circles  
        HW.rectangles    = TableSize.rectangles  
        HW.kalman        = HW.KalmanFilt()
        
        HW.VirtualScreen_Base = []
        HW.VirtualScreen      = []
        
    
        # initialize frame features
        HW.cap           = None 
        HW.frame         = None
        HW.frame_raw     = None
        HW.ret           = True
        HW.hsv           = None  # for detecting colours in the frame
        HW.writer        = None  #  used for saving video on a file
        HW.writer_raw    = None  # same, but for raw data as opposed to virtual
        HW.fourcc        = cv2.VideoWriter_fourcc(*HW.args["codec"])
        HW.timeTag       = time.strftime("%Y%m%d_%H%M%S")
        HW.NumberOfTrials = HW.args["trials"]
        
        # initialize the position variables
        HW.CupX             = []
        HW.CupY             = []
        HW.CupR             = []
        HW.BallX            = -1000000  # default is that there is no ball
        HW.BallY            = -1000000
        HW.CupX_List        = []
        HW.CupY_List        = []
        HW.CupR_List        = []
        HW.BallX_List       = []  
        HW.BallY_List       = []
        HW.FPSCnt           = []
        HW.FPSList          = []
        
        HW.CupRadius        = [] # if the cup is modeled by circle 
        HW.BallRadius       = []
        HW.CupLongDiag      = [] # long diameter of elipse for cup as an elipse
        HW.CupShortDiag     = [] # short diameter
        HW.CupElipseAng     = [] # angle of elipse
        HW.BallLongDiag     = []
        HW.BallShortDiag    = []
        HW.BallElipseAng    = []
        HW.CurrentHome      = []    # if multiple targets, which one is currently the home position    
        HW.CurrentTarget    = []    # and which one the current target position. this could change during experiment
        HW.BallEscapedFlag  = 0
        HW.HitObstacleFlag  = 0
        HW.CupNcnt          = 0     # number of contours found on the screen for cup
        HW.BallNcnt         = 0     # same but for ball
        HW.BadBall          = 0
        HW.Recording        = False
        HW.SavingFlag       = False   # determines when data should be saved for the current trial
        
        
        
        
          
# Start the camera capture    ------------------------------------------
    
    def Start(HW):
       
        if not HW.args.get("video", False):
            print("no video ----------")
            if HW.args.get("thread", False):
                HW.cap = WebcamVideoStream(src=HW.camera_port).start()
                
                print('---- webcamvideostream----')
            else:
                HW.cap = cv2.VideoCapture(HW.camera_port)
                print('---- videoCapture----')
        # otherwise, load the video
        else:
            if HW.args.get("thread", False):
                HW.cap = WebcamVideoStream(HW.args["video"]).start()
            else:
                videopath = os.path.join("Output", "videoOutput",  HW.args["video"][1]) #FIX: CROSS PLATFORM
                HW.cap = cv2.VideoCapture(videopath)
        # read the first frame
        if HW.args.get("thread", False):
            HW.frame = HW.cap.read()
        else:
             HW.ret,  HW.frame =  HW.cap.read()
             
             
                    

        
        
# Stop the camera capture  and release   ------------------------------------------
    
    def Stop(HW):
        
        if HW.args.get("thread", False):
            HW.cap.stop()
        else:
            HW.cap.release()
        
        HW.writer.release()
        if HW.args["rawvideo"] > 0:
            HW.writer_raw.release()

        # We could also shut the windows here, but the question is whether we want to use
        # this at the end of each trial, or at the end of the experiment
    





# update reading each time called    ------------------------------------------
    
    def Read(HW):
        #HW.cap.stream.set(cv2.CAP_PROP_FPS,20)
        if HW.args.get("thread", False): 
            tmp = HW.cap.read()
            if not HW.cap.grabbed: # fail to read a frame
                print(" --------------- \n No frame \n ---------------")
            HW.frame_raw = tmp.copy()
        else:
            HW.ret, tmp = HW.cap.read()
        
        tmp = imutils.resize(tmp, width=HW.TableSize.width);
        mask   = np.zeros(tmp.shape, np.uint8)
        lefty  = HW.TableSize.lefty
        righty = HW.TableSize.righty 
        leftx  = HW.TableSize.leftx
        rightx = HW.TableSize.rightx
        mask[lefty:righty, leftx:rightx] = tmp[lefty:righty, leftx:rightx]
        # resize frame        
        #HW.frame = imutils.resize(mask, width=HW.TableSize.width)
        HW.frame = mask.copy() 
        if not HW.args.get("video", False):  # NOT a postprocessing mode
            #HW.frame_raw = imutils.resize(mask, width=HW.TableSize.width)
            HW.frame_raw = mask.copy() 
        
        HW.FPSCnt = HW.cap.stream.get(cv2.CAP_PROP_FPS)
        #print("Frame Rate: ", HW.FPSCnt )
        
        
        
        
# only call if you need virtual screen ----------------------------------------
    
    def InitializeVirtualScreen(HW):
        
        HW.VirtualScreen = np.zeros((HW.TableSize.height, HW.TableSize.width, 3), np.uint8)
        HW.VirtualScreen[:] = (255, 255, 255)
        for (x, y, r) in HW.circles:
            cv2.circle(HW.VirtualScreen, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(HW.VirtualScreen, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        for approx in HW.rectangles:                   
            cv2.drawContours(HW.VirtualScreen, [approx], -1, (0, 128, 255), 3)
        # draw lens registration target window 
        cv2.circle(HW.VirtualScreen, (HW.TableSize.centerx, HW.TableSize.centery), 4, (0, 0, 255), 4)
        Lx = HW.TableSize.centerx - HW.TableSize.table_halfw
        Ly = HW.TableSize.centery - HW.TableSize.table_halfh
        Rx = HW.TableSize.centerx + HW.TableSize.table_halfw
        Ry = HW.TableSize.centery + HW.TableSize.table_halfh
        cv2.rectangle(HW.VirtualScreen, (Lx , Ly), (Rx, Ry), (153, 255, 255), 3)
        HW.VirtualScreen_Base = HW.VirtualScreen.copy() # Save a base screen to use later
    
        
    
    
# Get the latest position   ---------------------------------------------------
    
    def GetLatest(HW):
        
        HW.hsv = cv2.cvtColor(HW.frame, cv2.COLOR_BGR2HSV)  
        
        if HW.args["marker"] == "cl_object": 

            (x, y, MA, ma, angle, N, img_dilation) = ellipse_tracking(HW.hsv,HW.TableSize,HW.ColourRange)
            HW.CupX              = x
            HW.CupY              = y
            HW.CupR              = (MA+ma)/4
            HW.CupLongDiag       = MA
            HW.CupShortDiag      = ma
            HW.CupElipseAng      = angle
            HW.CupNcnt           = N
            

        elif HW.args["marker"] == "cl_object+kalman": # track ball
            
            (x, y, MA, ma, angle, N) = ellipse_tracking(HW.hsv,HW.TableSize,HW.ColourRange)
            measured = np.array((x,y), np.float32)
            HW.kalman.correct(measured); # input: measurement
            prediction = kalman.predict();  # Computes a predicted state.
            HW.CupX       = prediction[0]
            HW.CupY       = prediction[1]
            HW.CupR              = (MA+ma)/4
            HW.CupLongDiag       = MA
            HW.CupShortDiag      = ma
            HW.CupElipseAng      = angle
            HW.CupNcnt           = N
            
            

        elif HW.args["marker"] == "el_object": # track ellipse ball
            
            (x, y, MA, ma, angle, N, img_dilation) = ellipse_tracking(HW.hsv,HW.TableSize,HW.ColourRange)
            HW.CupX              = x
            HW.CupY              = y
            HW.CupR              = (MA+ma)/4
            HW.CupLongDiag       = MA
            HW.CupShortDiag      = ma
            HW.CupElipseAng      = angle
            HW.CupNcnt           = N
            
            
            
        elif HW.args["marker"] == "el_object+kalman": # track ellipse ball
            
            (x, y, MA, ma, angle, N) = ellipse_tracking(HW.hsv,HW.HW.TableSize,HW.ColourRange)
            measured = np.array((x,y), np.float32)
            HW.kalman.correct(measured); # input: measurement
            prediction = HW.kalman.predict();  # Computes a predicted state.
            HW.CupX       = prediction[0]
            HW.CupY       = prediction[1]
            HW.CupR              = (MA+ma)/4
            HW.CupLongDiag       = MA
            HW.CupShortDiag      = ma
            HW.CupElipseAng      = angle
            HW.CupNcnt           = N              
            
            
            
        elif HW.args["marker"] == "el_object_dual":  # track ellipse cup + ball
            (x, y, MA, ma, angle, N, bad_ball) = ellipse_dual_tracking(HW.hsv,HW.TableSize,HW.ColourRange)
            if not HW.args["idlevel"] == "ID1":
                if bad_ball: # if the ball detection is false, skip this fr=ame. (test this method)
                    print("ball detection failed for this frame - skip this frame.")
            HW.CupX               = x[0]
            HW.CupY               = y[0]
            HW.CupR               = (MA[0]+ma[0])/4
            HW.CupLongDiag        = MA[0]
            HW.CupShortDiag       = ma[0]
            HW.CupElipseAng       = angle[0]
            HW.CupNcnt            = N[0]
            HW.BallX              = x[1]
            HW.BallY              = y[1]
            HW.BallLongDiag       = MA[1]
            HW.BallShortDiag      = ma[1]
            HW.BallElipseAng      = angle[1]
            HW.BallNcnt           = N[1]
        
        # Save positions in an array
        if HW.Recording:
            HW.CupX_List.append(HW.CupX)
            HW.CupY_List.append(HW.CupY)
            HW.CupR_List.append(HW.CupR)
            HW.BallX_List.append(HW.BallX)
            HW.BallY_List.append(HW.BallY)
            HW.FPSList.append(HW.FPSCnt)
            
           

                
            
    
# Start recording the positions   ---------------------------------------------------

    def StartRecording(HW,TrialCnt,categories,TimeInExp):
        # Reset previous trial to start a new one
        HW.CupX_List        = []
        HW.CupY_List        = []
        HW.CupR_List        = []
        HW.BallX_List       = []  
        HW.BallY_List       = []
        # prepare the file for video recording
        videoName_path      = save_video(TimeInExp,TrialCnt,HW.args, HW.timeTag, categories, HW.args["gametest"], isRaw=0)
        rawvideoName_path   = save_video(TimeInExp,TrialCnt,HW.args, HW.timeTag, categories, HW.args["gametest"], isRaw=1)
        HW.WriterInit(videoName_path,rawvideoName_path)        
        HW.Recording        = True
        
        
        
        
# Stop recording the positions   ---------------------------------------------------

    def StopRecording(HW):
        # Dont reset anything as you might need to save it 
        HW.writer.release()
        if HW.args["rawvideo"] > 0:
            HW.writer_raw.release()
        HW.Recording = False    
           
             
        
# write video   ---------------------------------------------------

    def WriteVideo(HW):
        # Record the video
        if HW.Recording:
            HW.writer.write(HW.frame)   
            if HW.args["rawvideo"] > 0:
                HW.writer_raw.write(HW.frame_raw) 
        
           
                     
        
        
# Initialize target and home positions   ---------------------------------------------------
        
    def TargetInit(HW):  
        
        TD = []
        if HW.args['tasktype'] == "p2p":
            if len(HW.circles) != 2:  # for now, just go with two
                HW.Stop()
                cv2.destroyAllWindows()
                k = cv2.waitKey(1)
                raise RuntimeError("----------------------------------- \n Number of targets is less than 2. Add more targets and try again.\n -----------------------------------")
            
            for (x,y,r) in HW.circles:
                dist = math.hypot( (HW.CupX-x) , (HW.CupY-y) )
                TD.append( dist )
            
            min_idx = np.argmin(TD)
            HW.CurrentHome   = HW.circles[min_idx][:]
            HW.CurrentTarget = HW.circles[1-min_idx][:]  # python accepts negative index and goes backwards
        elif HW.args['tasktype'] == "fig8": # fig8 / pygame (currently the same as p2p
            HW.rectangles = None
        else:  # pygame
            HW.rectangles = None
                    
        
        
        
# Check if cup is in home positions ---------------------------------------------


    def InHome(HW):
        ok = False
        Dist = math.hypot( (HW.CupX - HW.CurrentHome[0]) , (HW.CupY - HW.CurrentHome[1])  )
        if Dist<HW.CurrentHome[2]:  # arbitrarily choose half the radius for tolerance
            ok = True
        
        return ok
        
        
    
# Check if cup is in target positions ---------------------------------------------

    def InTarget(HW):
        ok = False
        Dist = math.hypot( (HW.CupX - HW.CurrentTarget[0]) , (HW.CupY - HW.CurrentTarget[1])  )
        if Dist<HW.CurrentTarget[2]/2:  # arbitrarily choose half the radius for tolerance
            ok = True
        
        return ok
        
    
    
    
# Check if cup hit the obstacle ---------------------------------------------

    def InObstacle(HW):
        ok = False
        HW.HitObstacleFlag = 0
        for rect in HW.rectangles:
            if cv2.pointPolygonTest(rect, (HW.CupX, HW.CupY), 0) == 1.0:
                ok = True
                HW.HitObstacleFlag = 1
                break
        return ok        
        
        
    
    
    
# in out and return movements, switch the home and target positions ---------------------------------------------

    def SwapTargets(HW):
        tmp = HW.CurrentHome
        HW.CurrentHome = HW.CurrentTarget
        HW.CurrentTarget = tmp
        
        
    


# Check if ball droped ---------------------------------------------
                
    def BallEscaped(HW):                
        ok   = False
        HW.BallEscapedFlag = 0
        R    = (HW.CupLongDiag + HW.CupShortDiag) /4
        Dist = math.hypot(  (HW.CupX - HW.BallX) , (HW.CupY - HW.BallY)   )
        if Dist> 60*R/84:  
            ok = True
            HW.BallEscapedFlag = 1
            
            
        return ok    
            
    
    
    
    
# Check if ball is rotating inside the cup ---------------------------------------------


    def BallRotating(HW): # we don't have velocity at the moment, so ball rotation means ball is a certain distnce away from the cup centre            
            
        ok = False
        R    = (HW.CupLongDiag + HW.CupShortDiag) /4
        Dist = math.hypot(  (HW.CupX - HW.BallX) , (HW.CupY - HW.BallY)   )
        if Dist>= .75*R/3 and Dist<R:   # .75 because the real cup diameter is .75 of the detected ring diameter
            ok = True
        
        return ok   
        
        
        




# Kalman filter calculation for estimating positions (not used) ---------------------------------------------

    def KalmanFilt(HW):
        
        
        HW.kalman = cv2.KalmanFilter(4,2)
        HW.kalman.measurementMatrix = np.array([[1,0,0,0],
                                             [0,1,0,0]],np.float32)
    
        HW.kalman.transitionMatrix = np.array([[1,0,1,0],
                                            [0,1,0,1],
                                            [0,0,1,0],
                                            [0,0,0,1]],np.float32)
    
        HW.kalman.processNoiseCov = np.array([[1,0,0,0],
                                           [0,1,0,0],
                                           [0,0,1,0],
                                           [0,0,0,1]],np.float32) *0.0000001  # Tune this parameter.
    
        measurement = np.array((2,1), np.float32)
        prediction  = np.zeros((2,1), np.float32)
    
    
    

# Initialize the writer ---------------------------------------------

    def WriterInit(HW,Path,Path_raw):
        
        
        if HW.args.get("video", False):  # postprocessing mode
            HW.TableSize.width  = int(HW.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            HW.TableSize.height = int(HW.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        HW.writer = cv2.VideoWriter(Path, HW.fourcc, HW.args["fps"],
                                 (HW.TableSize.width, HW.TableSize.height), True)
        
        """ Raw video recording for back up (slows down fps)"""
        if HW.args["rawvideo"] > 0:
            HW.writer_raw = cv2.VideoWriter(Path_raw, HW.fourcc, HW.args["fps"],
                                         (HW.TableSize.width, HW.TableSize.height), True)

        







