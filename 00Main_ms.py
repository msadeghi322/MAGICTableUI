# coding=utf-8
__author__ = 'wonjoonsohn'

# -*- coding: utf-8 -*-

# note: speed of the loop for processing taken video doesn't matter.
#       when taking video, I should get while loop as fast as I can...
#       Video recording can be fast without real time video feedback. Let's do that next. 



############## Call Local and global libraries  =======================================================================================================


from arguments import get_arguments
from shape_detection import detect_circle, detect_obstacles, detectShapesInTable
from save import save_output_at, save_video, save_dataframe
import constants as C


# -------------- openCV --------------------------------------------------------------------------------------------

import numpy as np     
import pandas as pd
import pickle   # something to do with objects (ms)
import cv2      # openCV pagage for computer vision and graphics (ms)
import imutils  # basic image processing functions such as translation, rotation, resizing, skeletonization, displaying Matplotlib images, sorting contours, detecting edges, and ... (ms)
from imutils.video import FileVideoStream
from imutils.video import WebcamVideoStream
from imutils.video import VideoStream
from imutils.video import FPS
from threading import Thread    # Thread allows for running multiple independent parts of a code almost simultaneously (ms)
from collections import deque   # Collections contains diffrerent data structures, one of them in deque which is like a list (ms)
import sys                      # provides system specific variables and functions that directly work with the interpretor (ms)
from scipy import misc          # Like numpy is for scientific computations that builds on numpy some more specific computations (ms)
import glob                     # The glob module finds all the pathnames matching a specified pattern (ms)
import os                       # This provides a way of using operating system dependent (windows, mac, etc) functions to talk with the operating system (ms)
import pdb                      # This is a debugger helps to set breakpoints and single stepping on the program (ms)
import time                     # time dependent functions (ms)
import datetime        
#from matplotlib import pyplot as pslt  ## collide with gooey parser...
import csv
from multiprocessing import Process  # parallel process
import gc  # to disable garbage collection during appending data
#from gooey import Gooey, GooeyParser


# -------------- MS libraries.----------------------------------------------------------------------------------------------
sys.path.append("/MS/")

from MS.ms_Timer import ms_Timer
from MS.ms_StateProcesses import ms_StateProcesses
from MS.ms_ShapeTracking import circle_tracking, ellipse_tracking, ellipse_dual_tracking
from MS.ms_Hardware import ms_Hardware
from MS.ms_snapshots import take_snapshot, load_snapshot, check_camera







############## Some initial definitions  =======================================================================================================

camera_port =0  # if multiple cameras. 0 would use the mac camera, and 1, 2 ... would use other external cameras



# defined an arbitrary class that could be used as structure type data
class structype:
    pass
    


# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
# http://www.rapidtables.com/web/color/RGB_Color.htm
    
ColourRange = structype()
ColourRange.greenLower = (24, 142, 0) #  BGR  GREEN darker ##temp at night
ColourRange.greenUpper = (120, 255, 255)

ColourRange.yellowLower = (16, 54, 40) # BGR  yellow postit.  
ColourRange.yellowUpper = (45, 255, 255)  # BGR  yellow postit

ColourRange.blueLower = (0, 211, 0) # BGR blue postit. 
ColourRange.blueUpper = (120, 255, 255)  # BGR  blue postit

#ColourRange.orangeLower = (0, 141, 112) # BGR oramnge postit. 
#ColourRange.orangeUpper = (243, 255, 255)  # BGR  orange postit

ColourRange.orangeLower = (0, 141, 112) # BGR oramnge postit. 
ColourRange.orangeUpper = (252, 255, 255)  # BGR  orange postit

ColourRange.redLower = (169, 162, 31)
ColourRange.redUpper = (189, 182, 111)



## Define table properties ---------------------------------------------
TableSize = structype();
TableSize.width       = 640  # window width
TableSize.height      = 480  # window height
#TableSize.width       = 640  # window width
#TableSize.height      = 480  # window height

TableSize.lens_h      = 1.2  #Lens vertical height 
TableSize.cup_h       = 0.08 #Cuptop height 
TableSize.magfactor             = 4
TableSize.table_width_in_cm     = 64
TableSize.table_height_in_cm    = 48
TableSize.centerx               = int(TableSize.width/2)  # center of window
TableSize.centery               = int(TableSize.height/2)
TableSize.table_halfw           = TableSize.table_width_in_cm * TableSize.magfactor# (large), smaller: 230 table half-width approx. unit in px
TableSize.table_halfh           = TableSize.table_height_in_cm * TableSize.magfactor# # table half-height approx.  # unit in px.
TableSize.lefty                 = TableSize.centery - TableSize.table_halfh
TableSize.righty                = TableSize.centery + TableSize.table_halfh
TableSize.leftx                 = TableSize.centerx - TableSize.table_halfw
TableSize.rightx                = TableSize.centerx + TableSize.table_halfw





###############################################################################

###############################################################################
            ###                    Main                     ####
###############################################################################

###############################################################################
            
            
def run_main(timeTag, game_name):
    ## KEYBOARD command:  esc / "q" key to escape, "d" / "D" key to delete the trial.
    print("KEYBOARD command:  esc / q key to escape, d / D key to delete the trial.")




    
    
    

############################  Part 1: Initialization ==========================================================================



    running = True
    # color filter range for calcHist
    cfLower =ColourRange.greenLower
    cfUpper =ColourRange.greenUpper
    pts = deque(maxlen=args["buffer"])
    pts_orig = deque(maxlen=args["buffer"])


    # Cup data to write to file
    dataOut = []
    elapsedTimeList= []
    markerList =[]
    xObjectList=[]
    yObjectList=[]
    xObjectList_ball=[]
    yObjectList_ball=[]
    displayList= []
    threadList= []
    tasktypeList= []
    start_cueList= []
    videoList=[]
    startTimeList = []
    startTimeFormattedList = []
    reachTimeList = []
    goalReachedList = []
    # pandas dataframe output
    data = pd.DataFrame([])
    
    # Start time
    startTime = time.time()*1000.0
    startTimeRaw = time.time()
    startTimeFormatted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
    """ converts to human readable: datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')"""
    num_frames = 0
    start_cue = 0
    soundplayed = 0
    delete_trial = 0 # whether to delete this trial because it is bad trial
    inTargetzone = 0  #  in P2P, you are in target zone.
    forceQuit = 0  # when you press 'c' to force quit at the end OR time is up.
    reach_time = 0
    targetzone_time = 0
    reach_time_start = 0
    marker = 0
    prevxObject = 0
    prevyObject = 0
    in_circle = 0
    ballEscaped = 0
    obstacleHit = 0
    #maxcupx = 0
    maxcupy = 0






# --------------  Call and initialize the Camera hardware -------------------------------------------------------------------------------

    

# --------------  Check for snapshot -------------------------------------------------------------------------------
  
    
    ### Check if you need another snapshot during experiment due to disturbed camera or table.
    need_to_take_snapshot= False
    #need_to_take_snapshot= check_camera(args, width, centerx, centery,table_halfw, table_halfh, timeTag, camera_port)
    need_to_take_snapshot= check_camera(args, TableSize, timeTag, camera_port)

                
    """ take a snapshot of the board in png"""
    if need_to_take_snapshot:  # here, all the graphical stuff in the begining happen: the instructions, the detection of objects on the table etc
        img_name, circles, rectangles =take_snapshot(args, TableSize, timeTag, camera_port)
    
    else: #if args.get("video", False):  
        print("load snapshot, load pickle data")
        img_name, circles, rectangles =load_snapshot(args,TableSize, timeTag, camera_port)

    print("Image name: ", img_name)
    
    TableSize.circles     =  circles
    TableSize.rectangles  =  rectangles
    
    



# --------------  Start hardware -------------------------------------------------------------------------------

    HW = ms_Hardware(args, camera_port , TableSize , ColourRange)
    
    HW.Start()         # create cap object to capture video
    HW.Read()          # create frame 
    HW.GetLatest()     # Get the position of cup and ball
    HW.TargetInit()    # initialize the home and target positions
        
       
    
    fps = FPS().start()
    

    # Define the state processing class
    global STATE
    STATE = ms_StateProcesses(HW)
        
    
    
    
    
    
# --------------  Generating the screen for virtual display --------------------------------------------------------------------------------
# This could go to a display function


    if args["mode"] =="pygame":
        pygame.mixer.music.play(-1)
    


    if args["virtual"] >0:
        HW.InitializeVirtualScreen()





# --------------  Defining some categories maybe to use later for saving data etc --------------------------------------------------------------------------------


    """ Output File name with codes for modes
    ## M1X: Play mode (Board tasks)
    ##   M10: p2p  (diagonal)
    ##   M11: p2p  (x-direction)
    ##   M12: p2p  (curved path upper (obstacle avoidance))  
    ##   M20: fig8  (figure-8 task)
    ## M31: Pygame - traffic_dodger
    ## M32: Pygame - banana_catcher
    ## M40: Postprocessing
    """
    if args["mode"] == "pygame":
        category1 = 3
        if game_name == "traffic_dodger":
            category2 = 0
        else:
            category2 = 1  # ADD with more games

    elif args["mode"] == "pp":
        category1 = 4
        category2 = 0
    else:
        category1 = 1
        if args["tasktype"]=="p2p":
            if args["path"]=="diag": # diagonal
                category2 = 0
                pathtype = "diagonal"
            elif args["path"]=="hori":  # horizonal x-axis
                category2 = 1
                pathtype = "horizonal"
            elif args["path"] == "cur": # curve
                category2 = 2
                pathtype = "curve"
            else:
                raise("Category of path error. Check -pth option")
        elif args["tasktype"] =="fig8":
            category2 = 1
            pathtype = "any"

    categories = "M" + str(category1) + str(category2)



    x_pr = 0
    y_pr = 0
    vx_pr = 0
    vy_pr = 0
    bulk_trial_num = 0
    maxcupx = 0
    mincupx = 5000
    maxcupy = 0





############################  Part 2: Main loop ==========================================================================


    
    
    while not STATE.ExitFlag:
        
        # -------------  Read the frame, trim and resize it ----------------------------------------------------------------------------
     
        HW.Read()
        if not HW.ret:
            break

        # ------------- Get the latest position for ball and cup  ----------------------------------------------------------------------------

        HW.GetLatest()
        
        
        Idle_function(HW,categories)
        STATE.To = 0
        STATE.From = 0
        
        

# -------------  Reset the virtual screen to errase previus frame (should be done at each loop) ----------------------------------------------------------------------------
        
        # White image needs to be reset at each loop, to errase previous content and add new content. This is
        # not an issue with displaying the 'frame' as the frame is read anew at the begining of each loop
        if args["virtual"] >0: # renew blank image (in this way, speeds of 3-4fps)
            HW.VirtualScreen = HW.VirtualScreen_Base.copy()

       


# -------------  Trial Type setting for bulk  ----------------------------------------------------------------------------
        
        """ bulk recording (e.g. 15 trials in one run) not fully implemented 2018.12.12."""
        if (args["bulkrecording"] > 0) & (bulk_trial_num >0):
            """ Bulk recording (like 15 trials (iw/ow) at once)
            produces files (dataframe + video) per trial. 
            """
            HW.timeTag = time.strftime("%Y%m%d_%H%M%S")  # get a new timetag
            #HW.writer = None    #reset for making another video file


    
# ------------- Update the tracing position window (pts)  ---------------------------------------------------------------------------------------------        
        
        pts.appendleft((int(HW.CupX), int(HW.CupY)))
        
        
# ------------- Display    ----------------------------------------------------------------------------
        
        # 1. Cup and ball
        
        if args["trace"] > 0:  
            
            # if there is cup, display
            if HW.CupNcnt > 0:
                if int(HW.CupLongDiag/2 + HW.CupShortDiag/2) > 10 & int(HW.CupLongDiag / 2 + HW.CupShortDiag / 2) < 100:
#                    cv2.ellipse(HW.frame, (int(HW.CupX), int(HW.CupY)),
#                                                (int(HW.CupLongDiag / 2), int(HW.CupShortDiag / 2)), int(HW.CupElipseAng), 0, 360, (0, 255, 0), 2)
                    
                    cv2.circle(HW.frame,(int(HW.CupX),int(HW.CupY)), int(HW.CupLongDiag/4 + HW.CupShortDiag/4), (0, 255, 0), 2)
                    cv2.circle(HW.frame,  (int(HW.CupX), int(HW.CupY)), 5, (0, 255, 255), -1)
               
            # if there is ball, display  
            if HW.BallNcnt>0:
                if int(HW.BallLongDiag/2 + HW.BallShortDiag/2) > 10:
                    cv2.circle(HW.frame,  (int(HW.BallX), int(HW.BallY)), 5, (0, 255, 255), -1)
        
        
        # 2. Cup and ball on the virtual white image
        
        if args["virtual"] >0:
            cv2.circle(HW.VirtualScreen,(int(HW.CupX),int(HW.CupY)), int(HW.CupLongDiag/2 + HW.CupShortDiag/2), (0, 128, 255), 2)
            cv2.circle(HW.VirtualScreen, (int(HW.CupX),int(HW.CupY)), 5, (0, 0, 255), -1)
        





# ------------- Display the clock  ---------------------------------------------------------------------------------------------        
        
        currentTime = time.time()*1000
        elapsedTime = 1000*STATE.TrialTimer.GetTime() #currentTime- startTime

        ### Drawing clock, line trace, and traces. (even if display=0, it can be written to file)
        if args["clock"] > 0:
            drawClock(HW.frame, STATE.TrialCnt, elapsedTime,  HW.timeTag, virtual=0)
            # if not args.get("video", False):  # NOT a postprocessing mode
            #     drawClock(frame_raw, num_frames, elapsedTime, timeTag, virtual=0)
            if args["virtual"] >0:
                drawClock(HW.VirtualScreen, STATE.TrialCnt, elapsedTime,  HW.timeTag, virtual=1)
           
            
            

            
# ------------- Display the tracing (we don't need to do this in general)  ---------------------------------------------------------------------------------------------        

            
        if len(pts) > 100:
            if args["marker"] == "el_object+kalman":
                pts_draw = pts[:100]  # keep last 100 points to draw line.
                pts_draw_orig = pts[:100]  # keep last 100 points to draw line.
            else:
                pts_draw = pts[:100] # keep last 100 points to draw line.

        else:
            if args["marker"] == "el_object+kalman":
                pts_draw_orig = pts
                pts_draw = pts
            else:
                pts_draw = pts


        ### line trace
        if args["linetrace"] > 0:
            # loop over the set of tracked points (improve to be < O(n))
            for i in range(1, len(pts_draw)):  # what is xrange in python2 is range in python 3
                    # if either of the tracked points are None, ignore
                    # them
                    if pts_draw[i - 1] is None or pts_draw[i] is None:
                            continue
     
                    # otherwise, compute the thickness of the line and
                    # draw the connecting lines
                    thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)

                    ## line trace drawing is expensive
                    if args["virtual"]>0:
                        if args["tasktype"]=="p2p":
                            if args["obstacles"]:
                                for rect in rectangles:
                                    if cv2.pointPolygonTest(rect, (HW.CupX, HW.CupY), 0) == 1.0:
                                        cv2.line(HW.VirtualScreen, pts_draw[i - 1], pts_draw[i], (0, 0, 255), thickness*3) #red

                            cv2.line(HW.VirtualScreen, pts_draw[i - 1], pts_draw[i], (255, 0, 0), thickness)#blue (cirlce)
                        else: # fig8
                            cv2.line(HW.VirtualScreen, pts_draw[i - 1], pts_draw[i], (255, 0, 0), thickness)#blue
                
                    if args["tasktype"]=="p2p":
                        if args["obstacles"]:
                            for rect in rectangles:
                                if cv2.pointPolygonTest(rect, (HW.CupX, HW.CupY), 0) == 1.0:
                                    cv2.line(HW.frame, pts_draw[i - 1], pts_draw[i], (0, 0, 255), thickness*3) #red
                        if args["marker"] == "el_object+kalman":
                            cv2.line(HW.frame, pts_draw[i - 1], pts_draw[i], (255, 0, 255), thickness)  # red
                            cv2.line(HW.frame, pts_draw_orig[i - 1], pts_draw_orig[i], (255, 0, 0), thickness)  # blue
                        else:
                            cv2.line(HW.frame, pts_draw[i - 1], pts_draw[i], (0, 128, 0), thickness) #green  (circle)
                    else: # fig8
                        if args["marker"] == "el_object+kalman":
                            cv2.line(HW.frame, pts_draw[i - 1], pts_draw[i], (255, 0, 255), thickness)  # red
                        else:
                            cv2.line(HW.frame, pts_draw[i - 1], pts_draw[i], (0, 128, 0), thickness)#green







# ------------- Flip everything you've drawn onto the screen ---------------------------------------------------------------------------------------------        


        """ display"""
            # cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
        if args["display"] > 0:
            cv2.imshow("opencv_demo", HW.frame)  # expensive
            # cv2.imshow("Frame", frame)  # expensive
        if args["virtual"] > 0:
            cv2.imshow("virtualFrame", HW.VirtualScreen)





# ---------------- Write video---------------------------------------------------------------------------------------------

        
        HW.WriteVideo()
# ---------------- Make dataframe and Save the data ---------------------------------------------------------------------------------------------
        
        if HW.SavingFlag:
            start_x = HW.CurrentHome[0]   
            start_y = HW.CurrentHome[1]   
            start_r = HW.CurrentHome[2]   
            end_x   = HW.CurrentTarget[0] 
            end_y   = HW.CurrentTarget[1] 
            end_r   = HW.CurrentTarget[2] 
            
            
            if not delete_trial:
                """ with meta data written on top """
                if args["tasktype"] == "p2p":
                    
                    print(" Target radius--------------",end_r)
                    
                    data = pd.DataFrame(
                        {'Frames': STATE.LoopList,
                         'elapsedTime': STATE.TrialTimeList, 
                         'CupX': HW.CupX_List, 
                         'CupY': HW.CupY_List,
                         'CupR': HW.CupR_List,
                         'BallX': HW.BallX_List, 
                         'BallY': HW.BallY_List, 
                         'ReactionTime': STATE.MetronomeReactionTime,
                         'MetronomeOnset':STATE.MetronomeOnset, 
                         'MetronomeDelay':STATE.MetronomeDelay,
                         'ReachDuration':STATE.ReachDuration,
                         'BallEscaped': STATE.BallEscapedFlag, 
                         'BallEscapeTime':STATE.BallEscapeTime , 
                         'TimeInExperiment':STATE.ExperimentTimer.GetTime(),
                         'HomeX': start_x, 
                         'TargetX': end_x, 
                         'HomeY': start_y, 
                         'TargetY': end_y, 
                         'HomeRadius': start_r , 
                         'TargetRadius':end_r,
                         'ExpCondition': HW.args["Condition"],
                         'Trial':STATE.TrialCnt, 
                         })
                    
                    
   
    
    
    
    
                else:
                    data = pd.DataFrame(
                        {'elapsedTime': elapsedTimeList, 'xObject': xObjectList, 'yObject': yObjectList,
                         'xObject_ball': xObjectList_ball, 'yObject_ball': yObjectList_ball,
                         'goalReached': goalReachedList, 'reachTime': reachTimeList,
                         'startCue': start_cueList, 'videoReplay': videoList })
    
                x='x'
                note = ""
                if args['tasktype'] =='p2p':
                    if start_x <= TableSize.centerx:
                        if args['handedness']=="r": # right hander
                            dir_of_move = 'ow'
                        else:
                            dir_of_move = 'iw'
                    else:
                        if args['handedness'] == "r":  # right hander
                            dir_of_move = 'iw'
                        else:
                            dir_of_move = 'ow'
                else:
                    dir_of_move = 'any'
                    
                if not STATE.BallEscapedFlag:    
                    sharedFileName = save_dataframe(STATE.TrialCnt, data,STATE.BallEscapedFlag, x, args, HW.timeTag, categories, gameTest, startTimeFormatted, note, dir_of_move, obstacleHit, pathtype)  # write dataframe to file
                else:
                    sharedFileName = save_dataframe(STATE.TrialCnt, data,STATE.BallEscapedCnt, x, args, HW.timeTag, categories, gameTest, startTimeFormatted, note, dir_of_move, obstacleHit, pathtype) 
                
                
            else:
                HW.writer.release()
                if args["rawvideo"] > 0:
                    HW.writer_raw.release()
                print(videoName_path)
                os.remove(videoName_path) # delete this trial
        
            HW.SavingFlag = False  # flip the flag for the next trial
            
        


# ------------- Keyboard inputs ---------------------------------------------------------------------------------------------        


	# if the 'q' key is pressed, stop the loop
        k= cv2.waitKey(1) & 0xFF   # very expensive. 19ms. # default output = 255 (at least in python 3.6)

        if k == 27: # esc (Break and save)
            goalReachedList.append(0)
            break
        elif k == 67 or k == 99: # "C" and "c" key: completed the fig8 task.
            inTargetzone = 1
            goalReachedList.append(inTargetzone)
            break
        elif k == 68 or k==100: # "D" and "d" key: delete.
            delete_trial = 1
            break

        goalReachedList.append(inTargetzone)

        
        
        
        
############################  Part 3: End of the loop and final regards ==========================================================================
        
        
        
    ### stop the timer and display FPS information
    fps.stop()
    
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    if args["mode"] == "pygame":  # pygame
        #traffic_dodger_loop.game_over_screen(score)
        pass

    print(len(elapsedTimeList), len(xObjectList), len(yObjectList), len(xObjectList_ball), len(yObjectList_ball))  # for debugging
    print(len(start_cueList), len(videoList), len(reachTimeList), len(goalReachedList)) # for debugging



    STATE.ExperimentDuration = STATE.ExperimentTimer.GetTime() / 60
    print(" Experiment total time: %f minutes---------"%STATE.ExperimentDuration)

    if not args['thread'] >0:
        HW.cap.release()
    
    
    
    
# ------------- Close the windows and shut. it. down.  ---------------------------------------------------------------------------------------------        

    HW.Stop()
    cv2.destroyAllWindows()
    k = cv2.waitKey(1)






## ========================== important: how to read several csv files and concatinate
    
#    local_path = os.getcwd()
#    DataFramePath = os.path.join(str(local_path), "Output","dataframeOutput")
#    all_files = glob.glob(DataFramePath + "/*.csv")
#    
#    li = []
#    
#    for filename in all_files:
#        df = pd.read_csv(filename, index_col=None, header=0)
#        li.append(df)
#    
#    NewData = pd.concat(li, axis=0, ignore_index=True)
#    NewData.to_csv(r'str(DataFramePath)/NewData')
    
    



















def selectROI(event, x, y, flags, param):
    ###################################################
    ##  Select RoiBox points from mouse click
    ###################################################
    global frame, roiPts, inputMode
    if inputMode and event == cv2.EVENT_LBUTTONDOWN and len(roiPts) < 4:
        roiPts.append((x,y))
        cv2.circle(frame,(x,y),4,(0,255,0),2)
        cv2.imshow("frame2",frame)

def get_roi_hist(frame, c,r,w,h, cfLower, cfUpper):
    ####################################################
    #### get the roi_hist, mask should be circle #######
    ####################################################
    roi = frame[r:r+h, c:c+w]
    hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    print("ROI", c, r, w, h, roi, hsv_roi)
    mask = cv2.inRange(hsv_roi, cfLower,cfUpper ) # should I specify color here?
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180]) #(images, channels mask(NONE=full image), histSize (bin count [256]), ranges [0, 256])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    return roi_hist

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 15, 1 )




def prevent_jumping(num_frames, xObject, prevxObject, yObject, prevyObject, threshold):
    ####################################################
    #### prevent detection jumping when more than ######
    #### one object w/ same color exists          ######
    ####################################################
    if num_frames > 0 and ((abs(xObject - prevxObject) > threshold ) or (abs(yObject - prevyObject) > threshold)):#e.g. threshold# pixel jump compared to previous frame
        xObject = prevxObject
        xObject = prevyObject
    else:
        xObject = xObject
        yObject = yObject
    return xObject, yObject




def kalman_filter_init():
    ####################################################
    ####    Initialize Kalman filter           #########
    ####################################################
    # init kalman filter object
    global kalman, measurement, prediction
    
    kalman = cv2.KalmanFilter(4,2)
    kalman.measurementMatrix = np.array([[1,0,0,0],
                                         [0,1,0,0]],np.float32)

    kalman.transitionMatrix = np.array([[1,0,1,0],
                                        [0,1,0,1],
                                        [0,0,1,0],
                                        [0,0,0,1]],np.float32)

    kalman.processNoiseCov = np.array([[1,0,0,0],
                                       [0,1,0,0],
                                       [0,0,1,0],
                                       [0,0,0,1]],np.float32) *0.0000001  # Tune this parameter.

    measurement = np.array((2,1), np.float32)
    prediction = np.zeros((2,1), np.float32)

    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10,1 ) # not used?


def drawClock(frame, num_frames, elapsedTime, timeTag, virtual):
    ####################################################
    ### display date/fm on screen (run when recording)##
    ####################################################
    import datetime
    # draw the text and timestamp on the frame
    cv2.putText(frame, "Trial: "+str(num_frames), (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (224, 255, 255), 1) # color black
    cv2.putText(frame, "Stopwatch: "+str('%0.3f' %(elapsedTime/1000))+"s", (150, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (224, 255, 255), 1) # color black
    if virtual:
        cv2.putText(frame, "Trial: " + str(num_frames), (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)  # color black
        cv2.putText(frame, "Stopwatch: " + str('%0.3f' % (elapsedTime / 1000)) + "s", (150, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)  # color black
    #cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S.%f%p")[:-5],
#                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 153), 1) # color black


def sound_effects():
    ### play(loops=0, maxtime=0, fade_ms=0) the options for playing the sound
    ### loop: repetitions AFTER the first play (loop=5 means total of 6 repetitions, first play + 5 repetitions)
    ### maxtime: how long the sound will play in ms
    ### fade_ms: starts from volume 0 and ramps up to max volume in xx ms
    
    #######################################################
    #####  Basic sounds from wav (not a game bg sound)  ###
    #######################################################
    pygame.mixer.init()
    local_path = os.getcwd()
    soundfiles_path = os.path.join(str(local_path), "resources","sounds")
    BeepFiles_path  = os.path.join(str(local_path), "resources","sounds","Beeps")
    #print('soudfile_path: ', soundfiles_path)
    if not os.path.exists(soundfiles_path):
        os.makedirs(soundfiles_path)
    try:
        Metronome = pygame.mixer.Sound(os.path.join(soundfiles_path, "neutral.wav"))#FIX: CROSS PLATFORM
        ErrorSound = pygame.mixer.Sound(os.path.join(soundfiles_path, "chord.wav"))#FIX: CROSS PLATFORM
        Neutral = pygame.mixer.Sound(os.path.join(soundfiles_path, "Alarm02.wav"))
        RestSound = pygame.mixer.Sound(os.path.join(soundfiles_path, "Alarm01.wav"))
        endCirclefx = pygame.mixer.Sound(os.path.join(soundfiles_path, "up1-chiptone.wav")) #FIX: CROSS PLATFORM
        obstablefx = pygame.mixer.Sound(os.path.join(soundfiles_path, "noisysqueak1.wav")) #FIX: CROSS PLATFORM
        GoSound = pygame.mixer.Sound(os.path.join(soundfiles_path,"start_coin.wav")) #FIX: CROSS PLATFORM
        ballDropSound = pygame.mixer.Sound(os.path.join(soundfiles_path, "ball_drop2.wav"))  # FIX: CROSS PLATFORM
        Beep1 = pygame.mixer.Sound(os.path.join(BeepFiles_path, "beep-02.wav"))
        Beep2 = pygame.mixer.Sound(os.path.join(BeepFiles_path, "beep-04.wav"))
        Beep3 = pygame.mixer.Sound(os.path.join(BeepFiles_path, "beep-06.wav"))
        Beep = pygame.mixer.Sound(os.path.join(soundfiles_path, "Speech On.wav"))
        # Beep6 = pygame.mixer.Sound(os.path.join(BeepFiles_path, "beep-01a.wav"))
        # Beep7 = pygame.mixer.Sound(os.path.join(BeepFiles_path, "beep-02.wav"))
        # 
    except:
        raise(UserWarning, "could not load or play soundfiles in 'data' folder :-(")
    return ErrorSound , Neutral, Metronome, RestSound, Beep , endCirclefx, obstablefx, ballDropSound




############# Idle function ==========================================================================


def Idle_function(HW,categories):
    
    
    global STATE
    global SOUND
    
    
    # run the state process to update the states
    STATE.ms_StateProcess(HW)        
    
    
    
    
    if STATE.To== STATE.SETUP:
        pass #SOUND.Beep4.play(0,300)
    
    
    if STATE.From == STATE.SETUP:  # Start recording from here
        
        # The exp timer helps record all videos even with ball escape
        HW.StartRecording(STATE.TrialCnt,categories,STATE.ExperimentTimer.GetTime())
        STATE.StartLoopCount()
            
        
    
    if STATE.To == STATE.GO:
        SOUND.Beep.play(0,300) 
        #cv2.putText(HW.frame, "Go! ", (400, 40), 
        #            cv2.FONT_HERSHEY_TRIPLEX, 2.0, (224, 255, 255), 13) #
        if args["virtual"] >0:
            cv2.putText(HW.VirtualScreen, "Go! ", (400, 40), 
                        cv2.FONT_HERSHEY_TRIPLEX, 2.0, (0, 0, 0), 13) # color black


    if STATE.To == STATE.METRONOME:
        if HW.args["MetrnmInt"]=="random":
            tt = np.random.uniform(1.5,3) # uniform random between 0-1
            STATE.MetronomeDelay =  tt      # convert to exponential random variable with mean 1
            
            
    if STATE.To== STATE.TOOSOON:
        SOUND.ErrorSound.play(1,300) 
    
        
    if STATE.To == STATE.REACTTIME:
        SOUND.Metronome.play(0,300)
        
    if STATE.Current==STATE.REACTTIME:
        cv2.putText(HW.frame, "Go! ", (400, 40), 
                    cv2.FONT_HERSHEY_TRIPLEX, 2.0, (224, 255, 255), 13)
    

    if STATE.Current == STATE.MOVING:
        if HW.InObstacle():
            print('xxxxxxxxxxxx Obstacle hit xxxxxxxxxxxxxx')
            SOUND.obstablefx.play(0,300)
            cv2.putText(HW.frame, "Obstacle hit! ", (320, 40),
                           cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 255), 8)
    
    
    
    if STATE.From == STATE.INTARGET:
        #SOUND.Beep1.play(0,300)
        if STATE.TooSlowFlag:
            #SOUND.Neutral.play(0,1000) 
            STATE.TooSlowFlag = False
        else: 
           SOUND.endCirclefx.play(0)  # play once
        
        
        
    if STATE.Current == STATE.RECOVER:
        pass

#        if num_frames % 8 == 0:  # blinks
#            cv2.circle(frame, (int(end_x), int(end_y)), end_r, (0, 0, 255),  thickness=5)
#        if args["virtual"] > 0:
#            if num_frames % 8 == 0:  # blinks
#                cv2.circle(HW.VirtualScreen, (int(end_x), int(end_y)), end_r, (0, 0, 255),  thickness=5)
#                        ## visual effect
    
    
    
        
    
    if STATE.To == STATE.FINISH:
    #if STATE.From == STATE.FINISH:
        HW.StopRecording()
        print('................Loop counts',STATE.LoopCnt)
        STATE.StopLoopCount()
        HW.SavingFlag = True
        SOUND.Neutral.play(0,700)
           
        
    
    if STATE.To == STATE.REST:
        #SOUND.RestSound.play(0,6000)
        SOUND.RestSound.play(0,2000)
        
    if STATE.From == STATE.REST:
        #SOUND.Neutral.play(0,1000)    
        print('****  End of Rest Break****')

    if STATE.To == STATE.BALLESCAPED:
        print('Ball has just dropped')
        #SOUND.ballDropSound.play(0,600)
        cv2.putText(HW.frame, "Ball Escaped! ", (320, 40),
                           cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 255), 8)

        if HW.args["virtual"] > 0:
            cv2.putText(HW.VirtualScreen, "Ball Escaped! ", (320, 40),
                                cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 255), 8)



    if STATE.To == STATE.EXIT:
       SOUND.RestSound.play(0,6000)






############# Part 4: Call the run_main function to start ==========================================================================

if __name__ == "__main__":
    from scipy.io import savemat, loadmat
    timeTag = time.strftime("%Y%m%d_%H%M%S")
    import argparse
    import math, random, sys
    import pygame
    from pygame.locals import *

    ###  get arguments from terminal
    global args  # check speed performance...
    args = get_arguments()

    global gameTest
    gameTest = args["gametest"]
    game_name = 'traffic_dodger';  ##  OPTIONS: 'banana_game', 'traffic_dodger'


    
    # load sound effects to be used later
    global SOUND
    SOUND = structype()
    ErrorSound , Neutral, Metronome, RestSound, Beep ,endCirclefx, obstablefx, ballDropSound= sound_effects()
    SOUND.ErrorSound , SOUND.Neutral, SOUND.Metronome, SOUND.RestSound, SOUND.Beep , SOUND.endCirclefx, SOUND.obstablefx, SOUND.ballDropSound= sound_effects()
    
    
    

    
    ############## SPECIFIC GAME COMPONENT  #1 ##############
    if args["mode"] =="pygame":
        """ setting worked for python 2"""
        import games.traffic_dodger.player as PLAYER
        import games.traffic_dodger.score as SCORE
        import games.traffic_dodger.game_loop as TRAFFIC_GAME
        import games.traffic_dodger.pygame_setup ## setup for traffic dodger.
        # """ setting for python 3"""
        # from games.traffic_dodger.player import *
        # from games.traffic_dodger.score import *
        # from games.traffic_dodger.game_loop import *
        # from games.traffic_dodger.pygame_setup import *  ## setup for traffic dodger.
    #########################################################
    elif args["mode"] =="realtime_plot":
        import sys
        import graphical_panel.realtime_magictable as MONITOR_WINDOW
        global win, p
        win = MONITOR_WINDOW.magictable_monitor_window()
        # p = Process(target=MONITOR_WINDOW.magictable_monitor_window(), args=())
        # sys.exit(win.app.exec_())

    run_main(timeTag, game_name) # Main openCV loop
    










    