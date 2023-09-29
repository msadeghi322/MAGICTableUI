

# -*- coding: utf-8 -*-

# note: speed of the loop for processing taken video doesn't matter.
#       when taking video, I should get while loop as fast as I can...
#       Video recording can be fast without real time video feedback. Let's do that next. 


############## Local library  ###########################
from snapshots import take_snapshot
from arguments import get_arguments
from shape_detection import detect_circle, detect_obstacles, detectShapesInTable
from save import save_output_at, save_video, save_dataframe
import constants as C
from check_camera_position import check_camera


################### openCV etc.##########################
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
##########################################################


################  definitions ######################
camera_port =1    # if multiple cameras. 0 would use the mac camera, and 1, 2 ... would use other external cameras


# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
# http://www.rapidtables.com/web/color/RGB_Color.htm

# green filter is robust. 
#greenLower = (29, 86, 6) #  BGR  GREEN darker
greenLower = (24, 142, 0) #  BGR  GREEN darker ##temp at night
#greenUpper = (64, 255, 255) # BGR  GREEN lighter  %
greenUpper = (120, 255, 255)
# Yellow is too close to white board background and confused when ambient light is different. 
yellowLower = (16, 54, 40) # BGR  yellow postit.  
yellowUpper = (45, 255, 255)  # BGR  yellow postit

blueLower = (0, 211, 0) # BGR blue postit. 
blueUpper = (120, 255, 255)  # BGR  blue postit

orangeLower = (0, 141, 112) # BGR oramnge postit. 
orangeUpper = (243, 255, 255)  # BGR  orange postit

redLower = (44, 170, 114)
redUpper = (243, 219, 255)


# def is the equivalent of 'function' in matlab, for user-defined functions
# The following function aparently receives a colour digit and finds the object with that colour, and returns its centre position + it's radius (ms)
def circle_tracking(hsvmask):
    #########################################################
    ##### track minumum enclosing circle of this mask #######
    #########################################################
    hsv = hsvmask
    hsvmask = cv2.inRange(hsv, greenLower, greenUpper) # determines the range of colour to be detected (ms)
    kernel = np.ones((5,5), np.uint8)
    img_erosion = cv2.erode(hsvmask, kernel, iterations=1)       # This gradually fades the tracking? (ms)
    img_dilation = cv2.dilate(img_erosion, kernel, iterations=5) # erode/dial: 1.3ms

    # ------ ms -----
    #Erosion:
    #It is useful for removing small white noises.
    #Used to detach two connected objects etc.
    #Dilation:
    #In cases like noise removal, erosion is followed by dilation. Because, erosion removes white noises, but it also shrinks our object. So we dilate it. Since noise is gone, they won’t come back, but our object area increases.
    #It is also useful in joining broken parts of an object.
    # ---------------


    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, # 0.5ms
            cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:2]
    
    center = None
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        x_center = width/2
        y_center = height/2
        ### Projection down to xy plane. Adjustment based on cup height. ######
        x_adjust = ((lens_h-cup_h)/lens_h)*(x-x_center)
        y_adjust = ((lens_h-cup_h)/lens_h)*(y-y_center)

        xObject = x_center+x_adjust
        yObject = y_center+y_adjust
    else:
        xObject = -1
        yObject = -1
        radius = -1

    return (xObject, yObject, radius, len(cnts))


def ellipse_tracking(hsvmask):
    #########################################################
    ##### track minimum enclosing elipse of this mask #######
    #########################################################
    hsv = hsvmask
    hsvmask = cv2.inRange(hsv, orangeLower, orangeUpper) # cheap
    #hsvmask3d = cv2.merge([zeros, zeros, hsvmask])
    kernel = np.ones((5,5), np.uint8)
    img_erosion = cv2.erode(hsvmask, kernel, iterations=1)       #
    img_dilation = cv2.dilate(img_erosion, kernel, iterations=3) # erode/dial: 1.3ms
    #img_dilation3d = cv2.merge([zeros, img_dilation, zeros])
    
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, # 0.5ms
            cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:2]
    
    center = None
    # only proceed if at least one contour was found
    #print "cnts", len(cnts)
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        #### MinAREA RECT RELATED #####
        #rect = cv2.minAreaRect(cnts[0])
        #box = cv2.boxPoints(rect)
        #box = np.int0(box)

        (x,y),(MA,ma),angle = cv2.fitEllipse(cnts[0])

        x_center = width/2
        y_center = height/2
        ### Projection down to xy plane. Adjustment based on cup height. ######
        #x_adjust = ((lens_h-cup_h)/lens_h)*(x-x_center)
        #y_adjust = ((lens_h-cup_h)/lens_h)*(y-y_center)
        x_adjust = x - x_center
        y_adjust = y - y_center

        xObject = x_center+x_adjust
        yObject = y_center+y_adjust
    else:
        xObject = -1
        yObject = -1
        radius = -1
        MA = 0 
        ma = 0
        angle = 0

    return (xObject, yObject,  MA, ma, angle,  len(cnts), img_dilation)


def ellipse_dual_tracking(hsvmask):
    #########################################################
    ##### track minimum enclosing elipse of this mask - two colors #######
    #########################################################
    hsv = hsvmask
    hsvmask_or = cv2.inRange(hsv, orangeLower, orangeUpper)  # cheap
    hsvmask_gr = cv2.inRange(hsv, greenLower, greenUpper)  # cheap
    hsvmark = [hsvmask_or, hsvmask_gr]
    kernel = np.ones((5, 5), np.uint8)

    xObject_list = [0]*2
    yObject_list = [0]*2
    MA_list = [0]*2
    ma_list = [0]*2
    angle_list = [0]*2
    len_cnts_list = [0]*2
    bad_ball = 0

    num_of_color =2 # two colors tracking
    for i in range(num_of_color):
        if i==0:
            hsvmask = hsvmask_or
        else:
            hsvmask = hsvmask_gr

        # if i==0: # do not erode the small green ball
        img_erosion = cv2.erode(hsvmask, kernel, iterations=1)  #
        # else:
        #     img_erosion = hsvmask
        img_dilation = cv2.dilate(img_erosion, kernel, iterations=3)  # erode/dial: 1.3ms
        # img_dilation3d = cv2.merge([zeros, img_dilation, zeros])

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL,  # 0.5m.s
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:2]

        center = None
        # only proceed if at least one contour was found
        # print "cnts", len(cnts)
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid

            if i==1 or i==2: # use min enclosing circle detection for small ball
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                MA = radius
                ma = radius
                angle = 0
            else:
                """ellipse fit"""
                (x, y), (MA, ma), angle = cv2.fitEllipse(cnts[0])
                """circle fit"""
                # c = max(cnts, key=cv2.contourArea)
                # ((x, y), radius) = cv2.minEnclosingCircle(c)
                # MA = radius
                # ma = radius
                # angle = 0

            x_center = width / 2
            y_center = height / 2
            ### Projection down to xy plane. Adjustment based on cup height. ######
            ###  no adjustment for energy margin calc.
            #x_adjust = ((lens_h - cup_h) / lens_h) * (x - x_center)
            #y_adjust = ((lens_h - cup_h) / lens_h) * (y - y_center)
            x_adjust = x - x_center
            y_adjust = y - y_center

            xObject = x_center + x_adjust
            yObject = y_center + y_adjust

        else:
            xObject = -1
            yObject = -1
            radius = -1
            MA = 0
            ma = 0
            angle = 0
            bad_ball = 1
            # frame_circle = frame.copy()

        # listify
        xObject_list[i] =xObject
        yObject_list[i] = yObject
        MA_list[i] = MA
        ma_list[i] = ma
        angle_list[i]=angle
        len_cnts_list[i] = len(cnts)

    return (xObject_list, yObject_list, MA_list, ma_list, angle_list, len_cnts_list, bad_ball)



###############################################################################

###############################################################################
            ###                    Main                     ####
###############################################################################

###############################################################################
            
            
def run_main(timeTag, game_name):
    ## KEYBOARD command:  esc / "q" key to escape, "d" / "D" key to delete the trial.
    print("KEYBOARD command:  esc / q key to escape, d / D key to delete the trial.")





############################  Part 1: Initialization ==========================================================================


    global width, height, lens_h, cup_h  
    width = 640
    height = 480 #360
    lens_h = 0.8 #Lens vertical height 
    cup_h = 0.08 #Cuptop height 

    global running 
    running = True
    # color filter range for calcHist
    cfLower =greenLower
    cfUpper =greenUpper
    
    pts = deque(maxlen=args["buffer"])
    pts_orig = deque(maxlen=args["buffer"])







# --------------  Camera alignment -------------------------------------------------------------------------------
    
    centerx = int(width/2)
    centery = int(height/2)
    #  new table inner dimension: 87cm x 57cm.  (34x22)
    magfactor = 3
    table_width_in_cm = 87
    table_height_in_cm = 57
    table_halfw = table_width_in_cm*magfactor# (large), smaller: 230 table half-width approx. unit in px
    table_halfh = table_height_in_cm*magfactor# # table half-height approx.  # unit in px.

    ### Check if you need another snapshot during experiment due to disturbed camera or table.
    need_to_take_snapshot= False
    need_to_take_snapshot= check_camera(args, width, centerx, centery,table_halfw, table_halfh, timeTag, camera_port)

                
    """ take a snapshot of the board in png"""
    if need_to_take_snapshot:  # here, all the graphical stuff in the begining happen: the instructions, the detection of objects on the table etc
        img_name, circles, rectangles =take_snapshot(args, width, centerx, centery,table_halfw, table_halfh, timeTag, camera_port)
    else: #if args.get("video", False):  
        print("load snapshot, load pickle data")
        if args.get("video", False):  # postprocessing
            vname = args["video"][1]
            #path, filename = os.path.split(vname)  # strip timetag from filename

            timetag_circles = vname[:15] + "_circles.dump"
            timetag_rectangles =  vname[:15] + "_rectangles.dump"

            circles = pickle.load(open(os.path.join("Output", "pickles", timetag_circles), 'rb')) #FIX: CROSS PLATFORM
            rectangles = pickle.load(open(os.path.join("Output",   "pickles", timetag_rectangles), 'rb')) #FIX: CROSS PLATFORM
            img_name =  vname[:15]+".png"
        else:  # just loading snapshot
            lastTimeTag = pickle.load(open("lastTimeTag.dump", 'rb'))
            print("last time tag",lastTimeTag)

            timetag_circles = lastTimeTag + "_circles.dump"
            timetag_rectangles =  lastTimeTag+ "_rectangles.dump"
            print(timetag_circles)
            print(timetag_rectangles)

            circles = pickle.load(open(os.path.join("Output", "pickles", timetag_circles), 'rb')) #FIX: CROSS PLATFORM
            rectangles = pickle.load(open(os.path.join("Output", "pickles", timetag_rectangles), 'rb')) #FIX: CROSS PLATFORM
            img_name = lastTimeTag+".png"

            #####  make a copied pickle data with new timeTag  ###########
            dataOutput_path= save_output_at("pickles")
            savefile_circles = os.path.join(dataOutput_path, timeTag+"_circles.dump") #FIX: CROSS PLATFORM
            savefile_rectangles = os.path.join(dataOutput_path, timeTag+"_rectangles.dump") #FIX: CROSS PLATFORM

            pickle.dump(circles, open(savefile_circles, 'wb'))   # save circle characteristics
            pickle.dump(rectangles, open(savefile_rectangles, 'wb')) # save rectangles contours
            pickle.dump(timeTag, open("lastTimeTag.dump", 'wb')) # save the latest time tag.

            """ test pick dump multiple """
            #np.savez(outfile, circles=circles, rectangles=rectangles)
            #plt.imsave("detected_shapes.png", np.hstack([frame, detecting_frame]))
            print("{} written!".format(savefile_circles))
            print("{} written!".format(savefile_rectangles))

#        load_image = 1
#        img_name="opencv_frame_0.png"  # load default image name (when testing without changing background)

    print("Image name: ", img_name)





# --------------  Check for circles and rectangles captured -----------------------------------------------------------------------


   # in case of point-to-point game, obstacles can be there. 
    if args['tasktype'] == "p2p":
        #circles = detect_circle(img_name) # should be only two circles (start / end)
##        if load_image == 1:
##            circles, rectangles, detecting_frame= detectShapesInTable(img_name, centerx, centery, table_halfw, table_halfh)
##        print circles
        if len(circles) != 2:
            raise RuntimeError("Number of circles is not 2.")

    elif args['tasktype'] == "fig8": # fig8 / pygame (currently the same as p2p
        #if len(circles) != 2:
            #raise RuntimeError("Number of circles is not 2.")
        rectangles = None
    else:  # pygame
        rectangles = None





# --------------  Check for camera stream --------------------------------------------------------------------------------------


    ### if the video path was not supplied, grab the reference to the camera
    if not args.get("video", False):
        print("no video ----------")
        if args.get("thread", False):
            print("thread  started #################################")
            cap = WebcamVideoStream(src=camera_port).start()
        else:
            cap = cv2.VideoCapture(camera_port)
            
    # otherwise, load the video
    else:
        print("yes video ----------")
        if args.get("thread", False):
            cap = WebcamVideoStream(args["video"]).start()
        else:
            #videopath = "Output/" +args["video"][0] + "/videoOutput/"+  args["video"][1] #FIX: CROSS PLATFORM
            videopath = os.path.join("Output", "videoOutput",  args["video"][1]) #FIX: CROSS PLATFORM
            cap = cv2.VideoCapture(videopath)

    #cap.set(cv2.cv.CV_CAP_PROP_FPS, 60) #attemp to set fps recording (doesn't work)
    
    fps = FPS().start()
    time.sleep(1.0)
           
    # Read the first frame of the video
    if args.get("thread", False):
        frame = cap.read()
    else:
        ret, frame = cap.read()




# --------------  Some specific setting for region of interest (???)------------------------------------------------------------------------------------


    """ part for camshift roi """
    if args["marker"] == "cs_object":
        global click_list
        click_list = []
        #create list to store tracked positions
        #positions[x] = the location of the tracked object in frame x
        positions = []
        for i in range(100000): positions.append((0,0))    # what is this loop for
        #make mouse callback function
        def callback(event, x, y, flags, param):
            #if the event is a left button click
            if event == 1:
                click_list.append((x,y))
                print("click")
        cv2.namedWindow('img')
        cv2.setMouseCallback('img', callback)

        # stuff for the mouse callback function 
        # take first frame of the video
 #       ret,frame = cap.read()
        frame = imutils.resize(frame, width=width) # increase fps if small, not expensive
        cv2.imshow('img', frame)
        cv2.waitKey(0)
        c,r = click_list[-2]
        a,b = click_list[-2], click_list[-1]
        h = b[1]-a[1]
        w = b[0]-a[0]
        print("crab", c, r, w, h)
        track_window = (c,r,w,h)
        roi_hist = get_roi_hist(frame, c,r,w,h, cfLower, cfUpper)
        
    # Set the ROI (Region of Interest). 
    #c,r,w,h = 500,400,70,70
    # c,r,w,h = 200,100,70,70
#     roiBox = (c,r,w,h)

    # Create mask and normalized histogram
#     roi = frame[r:r+h, c:c+w]
#     hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(hsv_roi, np.array((0., 30.,32.)), np.array((180.,255.,255.)))
#     roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
#     cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
#     term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)









# --------------  Other initializations -------------------------------------------------------------------------------------------


    # load sound effects to be used later
    startCirclefx, endCirclefx, obstablefx, GoSound, ballDropSound = sound_effects()

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*args["codec"])

    writer = None        # aparently writes on the video file for saving
    writer_raw = None    # same, but for raw data as opposed to virtual
    (h, w) = (None, None)
    zeros = None
                            
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






# --------------  Generating the screen for virtual display --------------------------------------------------------------------------------

    if args["mode"] =="pygame":
        pygame.mixer.music.play(-1)
    

    if args["virtual"] >0:
        whiteimage = np.zeros((height, width, 3), np.uint8)
        whiteimage[:] = (255, 255, 255)
        if args["tasktype"] == "p2p":
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(whiteimage, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(whiteimage, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                
            for approx in rectangles:                   
                cv2.drawContours(whiteimage, [approx], -1, (0, 128, 255), 3)
        else: # fig8
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(whiteimage, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(whiteimage, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)


        # draw lens registration target window 
        cv2.circle(whiteimage, (centerx, centery), 4, (0, 0, 255), 4)
        cv2.rectangle(whiteimage, (centerx- table_halfw, centery - table_halfh), (centerx + table_halfw, centery+ table_halfh), (153, 255, 255), 3)

        whiteimage_blank = whiteimage.copy()

    
    
    
    
# -------------- XXX  Game dependent adjustments --------------------------------------------------------------------------------

    ## Before running into while loop, check if the mode is pygame. If so, load start_screen()
    if args["mode"] =="pygame":
        action = 'start_screen'
        ########  SPECIFIC GAME COMPONENTS #2 #####
        square = PLAYER.Player()
        square.set_pos(*pygame.mouse.get_pos())
        score = SCORE.Score()
        firstRun = True

        traffic_dodger_loop = TRAFFIC_GAME.TrafficDodger()

        while action != 'quit':
            if action == 'start_screen':
                action = traffic_dodger_loop.start_screen()
            elif action == 'play':
                break
##            elif action == 'game_over_screen':
##                action = game_over_screen()
##          





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









############################  Part 2: Main loop ==========================================================================



    x_pr = 0
    y_pr = 0
    vx_pr = 0
    vy_pr = 0
    bulk_trial_num = 0
    maxcupx = 0
    mincupx = 5000
    maxcupy = 0

    lefty = centery - table_halfh
    righty = centery + table_halfh
    leftx = centerx - table_halfw
    rightx = centerx + table_halfw
    
    while running:
        
        
        

        
        
# -------------  Read the frame, trim and resize it ----------------------------------------------------------------------------
        
        
        if args.get("thread", False): # cheap
            frame_orig = cap.read()
            if not cap.grabbed: # fail to read a frame
                print("=====================None Frame ======================")
                continue # never catches anything
            frame_raw = frame_orig.copy()
        else:
            ret, frame_orig = cap.read()
            if not ret:
                break

        """ masking out unwanted region"""
        mask = np.zeros(frame_orig.shape, np.uint8)
        mask[lefty:righty, leftx:rightx] = frame_orig[lefty:righty, leftx:rightx]


        """ Resize the frame to increase speed."""
        frame = imutils.resize(mask, width=width)
        if not args.get("video", False):  # NOT a postprocessing mode
            frame_raw = imutils.resize(mask, width=width)

        """ Region of Interest (ROI) setting. Added 20181113
            to prevent detection out of the table."""
        #frame = frame_resized[centery-table_halfh:centery+table_halfh, centerx-table_halfw:centerx+table_halfw]
        #frame = frame_resized[0:640, 0:360]
            
        
        
        
        
        
# -------------  Reset the whiteimage (generated before loop) just for the heck of it? ----------------------------------------------------------------------------
        
        
        if args["virtual"] >0: # renew blank image (in this way, speeds of 3-4fps)
            whiteimage = whiteimage_blank.copy()

        # get the time
        t = time.time()






# -------------  Trial Type setting for bulk  ----------------------------------------------------------------------------
        
        """ bulk recording (e.g. 15 trials in one run) not fully implemented 2018.12.12."""
        if (args["bulkrecording"] > 0) & (bulk_trial_num >0):
            """ Bulk recording (like 15 trials (iw/ow) at once)
            produces files (dataframe + video) per trial. 
            """
            timeTag = time.strftime("%Y%m%d_%H%M%S")  # get a new timetag
            writer = None    #reset for making another video file






# ------------- Check if the target is reached (why here?) then terminate if not bulk recording  ----------------------------------------------------------------------------

        # if there is a time limit 
        
        if args.get("timed", False) > 0:  # time limit was set in -t argument.
            
            if args["tasktype"]=="p2p":
                if inTargetzone >0 and marker == 0: # end the trial when goal is reached.
                   reach_time = time.time()*1000 - startTime
                   print(reach_time)
                   targetzone_time = time.time()*1000 # the time when the cup entered the target
                   marker = 1

            if time.time()*1000- targetzone_time > 3*1000.0 and marker ==1: # terminate 3 second after target zone reached.
                print("Entered target zone 3 seconds ago. Quit the trial.")
                if args["bulkrecording"] > 0:
                    """Increment bulk trial number"""
                    bulk_trial_num += 1
                    marker = 0
                    inTargetzone = 0
                    """ TODO: reset all the kin lists.... """
                    pass
                    # reset_variables

                else:
                    break
                      
                
                
# ------------- Prepare the cue for start (Go!)  ----------------------------------------------------------------------------


            if  start_cue < 1 and time.time()*1000.0 - startTime > 1*1000.0:  # start go sound at 1 second. 
                GoSound.play(0)
                start_cue = 1
                
            # Go! Text displayed 
            if start_cue == 1 and time.time()*1000.0 - startTime < 2.5*1000.0:   # The problem here is that the starttime is set before the loop, so if we want to design a state machin, we should reset after each trial
                cv2.putText(frame, "Go! ", (400, 40),
                            cv2.FONT_HERSHEY_TRIPLEX, 2.0, (224, 255, 255), 13) #
                if args["virtual"] >0:
                    cv2.putText(whiteimage, "Go! ", (400, 40),
                                cv2.FONT_HERSHEY_TRIPLEX, 2.0, (0, 0, 0), 13) # color black

            # Terminate if time is up (This should go up above this section)
            if  time.time()*1000.0 - startTime > args.get("timed", False) * 1000.0:  # in seconds (termination time)                           
                seconds = (time.time()*1000.0 - startTime)/1000.0
                forceQuit = 1
                # Calculate frames per second
                fps_calc  = num_frames / seconds;
                print("Time taken: ", args.get("timed", False), "s, fps: {0}".format(fps_calc))
                break

   
    
    
    
    
# ------------- Save the video up to here  ----------------------------------------------------------------------------


        # check if the writer is None (apparently writer is a flag that controls saving)
        if writer is None:
            # store the image dimensions, initialzie the video writer,
            # and construct the zeros array
            if args.get("video", False):  # postprocessing mode
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            else:
                width = width    # 640
                height = height   # 360 (480 doesn't write to file)
                
            videoName_path = save_video(args, timeTag, categories, gameTest, isRaw=0)

            print('fourcc:', fourcc)
            print('w, h:', width, height)
            writer = cv2.VideoWriter(videoName_path, fourcc, args["fps"],
                                     (width, height), True)
            zeros = np.zeros((height, width), dtype="uint8")

            """ Raw video recording for back up (slows down fps)"""
            if args["rawvideo"] > 0:
                rawvideoName_path = save_video(args, timeTag, categories, gameTest, isRaw=1)
                writer_raw = cv2.VideoWriter(rawvideoName_path, fourcc, args["fps"],
                                             (width, height), True)





# ------------- Get the hsv colour format of the frame for later shape detection and tracking  ----------------------------------------------------------------------------


    	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # expensive 1.5ms






# ------------- Get the position of the cup and ball  ----------------------------------------------------------------------------

# The output of this part is the position of the cup: cupx and cupy.
# this is then used for determining the target positions, and the 


# -- "cl_object"- minimum enclosing circle
# -- "cl_object+kalman" - minimum enclosing circle + kalman filter
# -- "el_object" - minimum enclosing elipse. (better when cup is warped toward the edge)
# -- "el_object_dual" - minimum enclosing elipse & dual color tracking (e.g. the ball and the cup)
# -- "cs_object" - camshift algorithm.


        global xObject, yObject    # have to check if making these global slows down.  WJS.


        if gameTest:
            xObject, yObject = (10, 10)  # camera is not used. trackpad / mouse cursor is used.
            cupx = 100
            cupy = 100
        else:
            if args["marker"] == "cl_object": # track ball
                (xObject, yObject, radius, len_cnts) = circle_tracking(hsv)

                if len_cnts > 0:
                    # only proceed if the radius meets a minimum size
                    if args["trace"] > 0:  
                        if radius > 5:
                            # draw the circle and centroid on the frame,
                            # then update the list of tracked points
                            cv2.circle(frame, (int(xObject), int(yObject)), int(radius),#circle is cheap operation.
                                    (0, 255, 255), 2)
                            cv2.circle(frame,  (int(xObject), int(yObject)), 5, (0, 0, 255), -1)
                cupx = xObject
                cupy = yObject

            elif args["marker"] == "cl_object+kalman": # track ball
                # WJS note: Kalman filter noise parameter may be tuned.
                # Delayed added by the Kalman filter need to be checked.
                # Kalman filter doesn't fix the jumping problem when there are two objects with a same color.
                # Need further process to precent jumping.

                (xObject, yObject, radius, len_cnts) = circle_tracking(hsv)

                ### Jumping prevention (temporary)
                threshold = 60
                #xObject, yObject = prevent_jumping(num_frames, xObject, prevxObject, yObject, prevyObject, threshold)

                # pts=np.array([np.float32(xObject), np.float32(yObject)], np.float32)
                # pts = np.int0(pts)
                measured = np.array((xObject, yObject), np.float32)

                # use to correct kalman filter
                kalman.correct(measured);  # input: measurement

                # get new kalman filter prediction
                prediction = kalman.predict();  # Computes a predicted state.

                if len_cnts > 0:
                    # only proceed if the radius meets a minimum size
                    if args["trace"] > 0:
                        if radius > 5:
                            # draw the circle and centroid on the frame,
                            # then update the list of tracked points
                            cv2.circle(frame, (int(prediction[0]), int(prediction[1])), int(radius),#circle is cheap operation.
                                    (0, 255, 255), 2)
                            cv2.circle(frame,  (int(prediction[0]), int(prediction[1])), 5, (0, 0, 255), -1)
                cupx=xObject
                cupy=yObject


            elif args["marker"] == "el_object": # track ellipse ball
                (xObject, yObject, MA, ma, angle, len_cnts, img_dilation) = ellipse_tracking(hsv)

                if len_cnts > 0:
                    # only proceed if the radius meets a minimum size
                    if args["trace"] > 0:
                        if int(MA/2+ma/2) > 10 & int(MA/2+ma/2) < 100:
                            # draw the circle and centroid on the frame,
                            # then update the list of tracked points
                            cv2.ellipse(frame,(int(xObject),int(yObject)),(int(MA/2), int(ma/2)),int(angle),0,360,(0,255,0), 3)
                            cv2.circle(frame, (int(xObject),int(yObject)), 5, (0, 0, 255), -1)
                cupx = xObject
                cupy = yObject

            elif args["marker"] == "el_object_dual":  # track ellipse cup + ball
                # WJS note: Kalman filter noise parameter may be tuned.
                # Delayed added by the Kalman filter need to be checked.
                # Kalman filter doesn't fix the jumping problem when there are two objects with a same color.
                # Need further process to precent jumping.

                # (xObject, yObject, MA, ma, angle, len_cnts) = ellipse_tracking(hsv)
                (xObject_list, yObject_list, MA_list, ma_list, angle_list, len_cnts_list, bad_ball) = ellipse_dual_tracking(hsv)
                if not args["idlevel"] == "ID1":
                    if bad_ball: # if the ball detection is false, skip this fr=ame. (test this method)
                        print("ball detection failed for this frame - skip this frame.")
                        continue

                num_of_colors = 2
                for i in range(num_of_colors):
                    xObject = xObject_list[i]
                    yObject = yObject_list[i]
                    MA = MA_list[i]
                    ma = ma_list[i]
                    angle = angle_list[i]
                    len_cnts = len_cnts_list[i]

                    ### Jumping prevention (temporary)
                    # threshold = 60
                    # xObject, yObject =  prevent_jumping(num_frames, xObject, prevxObject, yObject, prevyObject, threshold)

                    # pts=np.array([np.float32(xObject), np.float32(yObject)], np.float32)
                    # pts = np.int0(pts)

                    # print 'x, y=',xObject, yObject, " kalmanxy = ", prediction[0], prediction[1]

                    # draw predicton on image
                    # frame = cv2.rectangle(frame, (prediction[0]-(0.5*w),prediction[1]-(0.5*h)), (prediction[0]+(0.5*w),prediction[1]+(0.5*h)), (0,255,0),2);

                    if len_cnts > 0:
                        # only proceed if the radius meets a minimum size
                        if args["trace"] > 0:
                            if int(MA / 2 + ma / 2) > 10 & int(MA / 2 + ma / 2) < 100:
                                # draw the circle and centroid on the frame,
                                # then update the list of tracked points
                                if i == 0:  # orange cup
                                    cv2.ellipse(frame, (int(xObject), int(yObject)),
                                                (int(MA / 2), int(ma / 2)), int(angle), 0, 360, (0, 255, 0), 2)
                                # else:  # green ball
                                #     cv2.ellipse(frame, (int(xObject), int(yObject)),
                                #                 (int(MA / 2), int(ma / 2)), int(angle), 0, 360, (0, 255, 255), 2)

                                cv2.circle(frame, (int(xObject), int(yObject)), 5, (0, 255, 255), -1)
                if args["tasktype"] == "p2p":
                    if num_frames > 100:
                        if start_x > end_x:
                            if cupx > xObject_list[0]:
                                print("x coordinate decreasing")
                                mincupx = xObject_list[0]
                        elif start_x < end_x:
                            if cupx < xObject_list[0]:
                                print("x coordinate increasing")
                                maxcupx = xObject_list[0]


                cupx = xObject_list[0]
                cupy = yObject_list[0]

            elif args["marker"] == "el_object+kalman": # track ellipse ball
                # WJS note: Kalman filter noise parameter may be tuned.
                # Delayed added by the Kalman filter need to be checked.
                # Kalman filter doesn't fix the jumping problem when there are two objects with a same color.
                # Need further process to precent jumping.

                (xObject, yObject, MA, ma, angle, len_cnts) = ellipse_tracking(hsv)

                #pts=np.array([np.float32(xObject), np.float32(yObject)], np.float32)
                #pts = np.int0(pts)

                ###3# add random noise
                #yObject = yObject + np.random.normal(0, 20)

                measured = np.array((xObject,yObject), np.float32)

               # use to correct kalman filter
                kalman.correct(measured); # input: measurement

                # get new kalman filter prediction
                prediction = kalman.predict();  # Computes a predicted state.

                # draw predicton on image
                #frame = cv2.rectangle(frame, (prediction[0]-(0.5*w),prediction[1]-(0.5*h)), (prediction[0]+(0.5*w),prediction[1]+(0.5*h)), (0,255,0),2);

                if len_cnts > 0:
                    # only proceed if the radius meets a minimum size
                    if args["trace"] > 0:
                        if int(MA/2+ma/2) > 10 & int(MA/2+ma/2) < 100:
                            # draw the circle and centroid on the frame,
                            # then update the list of tracked points
                            # cv2.ellipse(frame,(int(prediction[0]),int(prediction[1])),(int(MA/2), int(ma/2)),int(angle),0,360,(0,255,0), 3)
                            # cv2.circle(frame, (int(prediction[0]),int(prediction[1])), 5, (0, 0, 255), -1)  # kalman
                            cv2.circle(frame, (int(cupx), int(cupy)), 5, (255, 0, 255), -1) # original


            elif args["marker"] == "cs_object": # track ball in camshift
                # construct a mask for the color "x", then perform
                # a series of dilations and erosions to remove any small
                # blobs left in the mask
                print("num_frames:", num_frames)

                # initial c,r,w,h supplied by above-if_clause
                # Subsequent c,r,w,h supplied by 
                
                dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1) #(image,  backProject, hist)
                # apply meanshift to get the new location
                ret, track_window= cv2.CamShift(dst, track_window, term_crit)
                # Draw it on image
                points = cv2.boxPoints(ret)
                points = np.int0(points)
                x=track_window[0]+track_window[2]/2
                y=track_window[1]+track_window[3]/2
                radius=(track_window[2]+track_window[3])/2
                # frame = cv2.circle(frame,(int(x), int(y)), int(radius), (0, 255, 0) ,-1)
                img2 = cv2.polylines(frame,[points],True, 255,2)

                #cv2.imshow("img2", img2) 
                k = cv2.waitKey(1) & 0xff  
                if k == 27: # esc key

                    break
                print("box size:", track_window[2]*track_window[3])

                if k == 32 or track_window[2]*track_window[3]>12000: # 32:space
                    cv2.waitKey(0)
                    c,r = click_list[-2]
                    a,b = click_list[-2], click_list[-1]
                    h = b[1]-a[1]
                    w = b[0]-a[0]
                    track_window = (c,r,w,h)
                    roi_hist = get_roi_hist(frame, c,r,w,h, cfLower, cfUpper)
                    print("new track window")
                    #print a,b
           
                center = None

                xObject = x
                yObject = y

        
        
        # previous frame's coordinates to be used later for jumping control
        prevxObject = xObject
        prevyObject = yObject

        
        
# ------------- Check for ball escape  ---------------------------------------------------------------------------------------------        
        
        """ check if ball escaped the cup"""
        if not args["idlevel"]=="ID1": # when there is a ball...

            if not ballEscaped:
                if abs(cupx-xObject_list[1]) > (circles[0][2] + 30)  or abs(cupy-yObject_list[1]) > (circles[0][2]+30) :# I used the start circle radius here but you should use cup radius in principle
                    print('Ball has just dropped')
                    ballEscaped =1
                    ballEscapeTime = time.time() * 1000.0


            """ Ball Escaped! Text displayed"""
            if ballEscaped:
                if time.time()*1000.0 - ballEscapeTime < 2*1000.0:   # play for three second after drop

                    ballDropSound.play(0)
                    ballDropSound.set_volume(0.2)
                # else:
                #     pygame.mixer.Sound.pause()

                # if num_frames % 100 == 0:  # blinks
                cv2.putText(frame, "Ball Escaped! ", (320, 40),
                            cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 255), 8)

                if args["virtual"] > 0:
                    cv2.putText(whiteimage, "Ball Escaped! ", (320, 40),
                                cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 255), 8)






# ------------- If virtual display on, draw the cup position on corresponding image (why here??)  ---------------------------------------------------------------------------------------------        
       # This should be right after Get position!
        
        if args["virtual"] >0:
            cv2.circle(whiteimage,(int(cupx),int(cupy)), 30, (0, 128, 255), 2)
            cv2.circle(whiteimage, (int(cupx),int(cupy)), 5, (0, 0, 255), -1)





# ------------- In P2P case, determine the home and target positions based on where the cup is placed  ---------------------------------------------------------------------------------------------        
            # This should be up there again, the code order doesn't match the order of performance

        """ P2P: Determine the starting and ending target based on initial coordinate"""
        if args["tasktype"] == "p2p":
            if num_frames == 0: # run only in the first frame, causes no delay.
                if math.hypot(cupx- circles[0][0], cupy-circles[0][1]) < circles[0][2]:
                    start_cicle_ind = 0
                    end_cicle_ind = 1

                elif math.hypot(cupx- circles[1][0], cupy-circles[1][1]) < circles[1][2]:
                    start_cicle_ind = 1
                    end_cicle_ind = 0

                else:
                    start_cicle_ind = 0
                    end_cicle_ind = 1
                    print('cup xObject:', cupx,  ' cup yObject:', cupy)
                    raise RuntimeError("Cup is not positioned in the start circle.")

                start_x = circles[start_cicle_ind][0]
                start_y = circles[start_cicle_ind][1]
                start_r = circles[start_cicle_ind][2]
                end_x = circles[end_cicle_ind][0]
                end_y = circles[end_cicle_ind][1]
                end_r = circles[end_cicle_ind][2]
                mid_y = (start_y + end_y)/2
                
                
               
                
                
# ------------- Append time and measured positions in their arrays  ---------------------------------------------------------------------------------------------        
                
                
        currentTime = time.time()*1000
        elapsedTime = currentTime- startTime

        ## increase performance than appending to dataframe 
        elapsedTimeList.append(elapsedTime)
        start_cueList.append(start_cue)
        videoList.append(args["video"])
        startTimeList.append(startTimeRaw)
        reachTimeList.append(reach_time)


        if args["marker"] == "el_object_dual":
            xObjectList.append(xObject_list[0])
            yObjectList.append(yObject_list[0])
            xObjectList_ball.append(xObject_list[1])
            yObjectList_ball.append(yObject_list[1])
        else:
            xObjectList.append(xObject)
            yObjectList.append(yObject)
            xObjectList_ball.append(-1)
            yObjectList_ball.append(-1)






# ------------- Display the clock  ---------------------------------------------------------------------------------------------        

        ### Drawing clock, line trace, and traces. (even if display=0, it can be written to file)
        if args["clock"] > 0:
            drawClock(frame, num_frames, elapsedTime,  timeTag, virtual=0)
            # if not args.get("video", False):  # NOT a postprocessing mode
            #     drawClock(frame_raw, num_frames, elapsedTime, timeTag, virtual=0)
            if args["virtual"] >0:
                drawClock(whiteimage, num_frames, elapsedTime,  timeTag, virtual=1)
           
            
            


# ------------- Update the tracing position window (pts)  ---------------------------------------------------------------------------------------------        
        
        # update the points queue
        #gc.disable()  # disable garbage collection during appending to speed up?

        if args["marker"] == "el_object+kalman":
            pts_orig.appendleft((int(xObject), int(yObject)))   # append left to have most recent in the beginning 
            pts.appendleft((int(prediction[0]), int(prediction[1])))
        else:
            pts.appendleft((int(cupx), int(cupy)))
        #pts_cupmarkers.appendleft(center_cup)
        #gc.enable()



            
# ------------- Display the tracing (we don't need to do this in general)  ---------------------------------------------------------------------------------------------        

            
        if len(pts) > 100:
            if args["marker"] == "el_object+kalman":
                pts_draw = pts[:100]  # keep last 100 points to draw line.
                pts_draw_orig = pts_orig[:100]  # keep last 100 points to draw line.
            else:
                pts_draw = pts[:100] # keep last 100 points to draw line.

        else:
            if args["marker"] == "el_object+kalman":
                pts_draw_orig = pts_orig
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
                                    if cv2.pointPolygonTest(rect, (cupx, cupy), 0) == 1.0:
                                        cv2.line(whiteimage, pts_draw[i - 1], pts_draw[i], (0, 0, 255), thickness*3) #red

                            cv2.line(whiteimage, pts_draw[i - 1], pts_draw[i], (255, 0, 0), thickness)#blue (cirlce)
                        else: # fig8
                            cv2.line(whiteimage, pts_draw[i - 1], pts_draw[i], (255, 0, 0), thickness)#blue
                
                    if args["tasktype"]=="p2p":
                        if args["obstacles"]:
                            for rect in rectangles:
                                if cv2.pointPolygonTest(rect, (cupx, cupy), 0) == 1.0:
                                    cv2.line(frame, pts_draw[i - 1], pts_draw[i], (0, 0, 255), thickness*3) #red
                        if args["marker"] == "el_object+kalman":
                            cv2.line(frame, pts_draw[i - 1], pts_draw[i], (255, 0, 255), thickness)  # red
                            cv2.line(frame, pts_draw_orig[i - 1], pts_draw_orig[i], (255, 0, 0), thickness)  # blue
                        else:
                            cv2.line(frame, pts_draw[i - 1], pts_draw[i], (0, 128, 0), thickness) #green  (circle)
                    else: # fig8
                        if args["marker"] == "el_object+kalman":
                            cv2.line(frame, pts_draw[i - 1], pts_draw[i], (255, 0, 255), thickness)  # red
                        else:
                            cv2.line(frame, pts_draw[i - 1], pts_draw[i], (0, 128, 0), thickness)#green









# ------------- Check if the cup is in target position (second time) and bad implementation ---------------------------------------------------------------------------------------------        


        """"For demo video recording (4 display windows in a frame)"""
        #img_dilation2 = np.dstack([img_dilation] * 3)
        #output =  np.vstack((np.hstack([frame_raw, hsv]), np.hstack([img_dilation2, frame])))


        """  Cursor potision - In or out of target """
        if args["mode"] != "pygame":            # if it is not on game mode
            if args["tasktype"] == "p2p":
                if args["obstacles"]:
                    for rect in rectangles:
                        if math.hypot(cupx - start_x, cupy - start_y) < start_r:
                            print("in the starting circle")
                        elif cv2.pointPolygonTest(rect, (cupx, cupy), 0) == 1.0:
                            print("in the obstacle ")
                            in_obstacle = 1
                            in_circle = 0
                        #elif math.hypot(xObject - start_x, yObject - start_y) < start_r:
                            #print "in the starting circle"
                            obstablefx.play(0)
                            obstablefx.set_volume(0.1)
                            obstacleHit = 1
                        elif math.hypot(cupx - end_x, cupy - end_y) < end_r:
                            print("in the end circle")
                            #if soundplayed==0:
                            in_circle = 1
                            inTargetzone = 1
                            in_obstacle = 0
                            if time.time() * 1000.0 - targetzone_time < 0.5 * 1000.0:  # play for one second target reached
                                endCirclefx.play(0) # play once
                else: # there is no obstacles
                    #if math.hypot(cupx - start_x, cupy - start_y) < start_r:
                        #print("in the starting circle")
    ##                    #startCirclefx.play(0)
                    if start_x > end_x:
                        #if abs(start_x - mincupx)> (1.5*start_r):
                        if mincupx < (start_x -((start_x - end_x)/4)):
                            if math.hypot(cupx - start_x, cupy - start_y) < (start_r):
                        #if math.hypot(cupx - end_x, cupy - end_y) < end_r:
                                inTargetzone = 1
                                print("in the end circle")
                                #if soundplayed==0:
                                #endCirclefx.play(0) # play once
                                in_circle=1
                                if time.time() * 1000.0 - targetzone_time < 0.5 * 1000.0:  # play for one second target reached
                                    endCirclefx.play(0)  # play once
                            else:
                                in_circle=0
                 #                       soundplayed=1
                    elif start_x < end_x:
                        if maxcupx > ( start_x +(( end_x - start_x)/4)):
                            if math.hypot(cupx - start_x, cupy - start_y) < (start_r):
                        #if math.hypot(cupx - end_x, cupy - end_y) < end_r:
                                inTargetzone = 1
                                print("in the end circle")
                                #if soundplayed==0:
                                #endCirclefx.play(0) # play once
                                in_circle=1
                                if time.time() * 1000.0 - targetzone_time < 0.5 * 1000.0:  # play for one second target reached
                                    endCirclefx.play(0)  # play once
                            else:
                                in_circle=0





# ------------- Play Audio feedback  ---------------------------------------------------------------------------------------------        


        """  audiovidual feedback  """
        ## This is very cheap operation
        if args["targetsound"] > 0:  # sound at target
            if not rectangles:  # if no rectangles exist:
                if args["tasktype"] == "p2p":
                    if in_circle:
                        endCirclefx.play(0)  # play once
        if args["targetvisual"] >0:
            if not rectangles:  # if no rectangles exist:
                if args["tasktype"] == "p2p":
                    if in_circle:
                        if num_frames % 8 == 0:  # blinks
                            cv2.circle(frame, (int(end_x), int(end_y)), end_r, (0, 0, 255),  thickness=5)
                        if args["virtual"] > 0:
                            if num_frames % 8 == 0:  # blinks
                                cv2.circle(whiteimage, (int(end_x), int(end_y)), end_r, (0, 0, 255),  thickness=5)
                        ## visual effect





# ------------- Flip everything you've drawn onto the screen ---------------------------------------------------------------------------------------------        


        """ display"""
            # cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
        if args["display"] > 0:
            cv2.imshow("opencv_demo", frame)  # expensive
            # cv2.imshow("Frame", frame)  # expensive
        if args["virtual"] > 0:
            cv2.imshow("virtualFrame", whiteimage)








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






# ------------- Write the frames (Record it) ---------------------------------------------------------------------------------------------        

        # write the frame
        writer.write(frame)   # 1.3ms
        if args["rawvideo"] > 0:
            writer_raw.write(frame_raw)  # record raw for postprocessing see how much it slows down.
        #writer.write(whiteimage)   # 1.3ms   # TODO: make it automatic selection






# ------------- Game specific piece of code ---------------------------------------------------------------------------------------------        


        if args["mode"] == "pygame":
            running = traffic_dodger_loop.game_loop(gameTest, square, score, running, cupx, cupy, firstRun, num_frames, game_name , timeTag , categories, args)
            firstRun = False
        elif args["mode"] =="realtime_plot":
        ############## sending realtime data to monitor window ######
            # win.updateCoordinate(xObject_list[0], yObject_list[0], xObject_list[1], yObject_list[1]) ## works but with some sensible delay. opencv real time movie is seriously affected.
            dt=0.03
            x=xObject_list[0]
            y=yObject_list[0]
            # vx = self.deriv(x, x_pr, dt)
            # vy = self.deriv(y, y_pr, dt)
            vx = (x-x_pr)/dt
            vy = (y-y_pr) / dt

            # vx=vx*0.01/8
            # vy=vy * 0.01 / 8

            # ### use to correct kalman filter
            # vmeasured = np.array((vx, vy), np.float32)
            # kalman.correct(vmeasured);  # input: measurement
            # ### get new kalman filter prediction
            # vpred = kalman.predict();  # Computes a predicted state.

            ax = (vx - vx_pr) / dt
            ay = (vy - vy_pr) / dt

            ### use to correct kalman filter
            ameasured = np.array((ax, ay), np.float32)
            kalman.correct(ameasured);  # input: measurement

            ### get new kalman filter prediction
            apred = kalman.predict();  # Computes a predicted state.

            x_b = xObject_list[1]
            y_b = yObject_list[1]
            win.updateCoordinate(x, y, apred[0], apred[1], x_b, y_b)  ## works but with some sensible delay. opencv real time movie is seriously affected.
            x_pr = x
            y_pr = y
            vx_pr = vx
            vy_pr = vy
        prev_num_frames = num_frames
        num_frames = num_frames + 1
        fps.update()  # update the FPS counter
        
        
        
        
############################  Part 3: End of the loop and final regards ==========================================================================
        
        
        
    ### stop the timer and display FPS information
    fps.stop()
    
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    if args["mode"] == "pygame":  # pygame
        traffic_dodger_loop.game_over_screen(score)

    print(len(elapsedTimeList), len(xObjectList), len(yObjectList), len(xObjectList_ball), len(yObjectList_ball))  # for debugging
    print(len(start_cueList), len(videoList), len(reachTimeList), len(goalReachedList)) # for debugging




# ------------- Creat a Data frame  ---------------------------------------------------------------------------------------------        


    if not delete_trial:
        if args["marker"] == "cl_object" or args["marker"] == "cs_object" or args["marker"] == "el_object" or args["marker"] == "el_object+kalman" or args["marker"] == "el_object_dual" or  args["marker"] == "cl_object+kalman": # track ball
            """ with meta data written on top """
            if args["tasktype"] == "p2p":
                data = pd.DataFrame(
                    {'elapsedTime': elapsedTimeList, 'xObject': xObjectList, 'yObject': yObjectList,
                     'xObject_ball': xObjectList_ball, 'yObject_ball': yObjectList_ball,
                     'goalReached': goalReachedList, 'reachTime': reachTimeList,
                     'startCue': start_cueList, 'videoReplay': videoList, 'start_x': start_x, 'end_x': end_x, 'start_y': start_y, 'end_y': end_y, 'start_r': start_r
                     })
            else:
                data = pd.DataFrame(
                    {'elapsedTime': elapsedTimeList, 'xObject': xObjectList, 'yObject': yObjectList,
                     'xObject_ball': xObjectList_ball, 'yObject_ball': yObjectList_ball,
                     'goalReached': goalReachedList, 'reachTime': reachTimeList,
                     'startCue': start_cueList, 'videoReplay': videoList })

        """########  Custom parameters for saving ########"""

        #if args["mode"]=="pygame":
        x='x'
        #else:
            #x = int(input("Was this trial a success?  Y(1) or N(0) "))

        #if args["note"] >0:
            #note = input("Write any note if any. Enter when done >> ")
        #else:

        note = ""

        if args['tasktype'] =='p2p':
            if start_x <= centerx:
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



# ------------- Save everything  ---------------------------------------------------------------------------------------------        


        sharedFileName = save_dataframe(data, x, args, timeTag, categories, gameTest, startTimeFormatted, note, dir_of_move, ballEscaped, obstacleHit, pathtype)  # write dataframe to file
        writer.release()
        if args["rawvideo"] > 0:
            writer_raw.release()
        ### this is to make the video file name same as data frame (csv) file name (to indicate success trials)
        if not args.get("video", False):  # if not video mode
            local_path = os.getcwd()
            print('local path:', local_path)
            dataOutput_path = os.path.join(str(local_path), "Output", "videoOutput")
            print('dataOutput_path:', dataOutput_path)
            print('sharedFileName:', sharedFileName)
            newVideoName_path = os.path.join(dataOutput_path, sharedFileName+ ".mp4")
            print('newVideoName_path:', newVideoName_path)
    else:
        writer.release()
        if args["rawvideo"] > 0:
            writer_raw.release()
        print(videoName_path)
        os.remove(videoName_path) # delete this trial

    if not args['thread'] >0:
        cap.release()
    
    
    
    
# ------------- Close the windows and shut. it. down.  ---------------------------------------------------------------------------------------------        
    
    cv2.destroyAllWindows()
    k = cv2.waitkey(1)






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
    cv2.putText(frame, "frames: "+str(num_frames), (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (224, 255, 255), 1) # color black
    cv2.putText(frame, "Stopwatch: "+str('%0.3f' %(elapsedTime/1000))+"s", (150, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (224, 255, 255), 1) # color black
    if virtual:
        cv2.putText(frame, "frames: " + str(num_frames), (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)  # color black
        cv2.putText(frame, "Stopwatch: " + str('%0.3f' % (elapsedTime / 1000)) + "s", (150, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)  # color black
    #cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S.%f%p")[:-5],
#                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 153), 1) # color black


def sound_effects():
    #######################################################
    #####  Basic sounds from wav (not a game bg sound)  ###
    #######################################################
    pygame.mixer.init()
    local_path = os.getcwd()
    soundfiles_path = os.path.join(str(local_path), "resources","sounds")
    print('soudfile_path: ', soundfiles_path)
    if not os.path.exists(soundfiles_path):
        os.makedirs(soundfiles_path)
    try:
        startCirclefx = pygame.mixer.Sound(os.path.join(soundfiles_path, "chiptone.wav"))#FIX: CROSS PLATFORM
        endCirclefx = pygame.mixer.Sound(os.path.join(soundfiles_path, "up1-chiptone.wav")) #FIX: CROSS PLATFORM
        obstablefx = pygame.mixer.Sound(os.path.join(soundfiles_path, "noisysqueak1.wav")) #FIX: CROSS PLATFORM
        GoSound = pygame.mixer.Sound(os.path.join(soundfiles_path,"start_coin.wav")) #FIX: CROSS PLATFORM
        ballDropSound = pygame.mixer.Sound(os.path.join(soundfiles_path, "ball_drop2.wav"))  # FIX: CROSS PLATFORM
    except:
        raise(UserWarning, "could not load or play soundfiles in 'data' folder :-(")
    return startCirclefx, endCirclefx, obstablefx, GoSound, ballDropSound



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
    
