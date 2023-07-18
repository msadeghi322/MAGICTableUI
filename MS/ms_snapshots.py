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



####################################################
###   take a snap shot of a board from webcam   ####
####################################################
def take_snapshot(args, TableSize , timeTag, camera_port):
    
    
    width           = TableSize.width
    centerx         = TableSize.centerx
    centery         = TableSize.centery
    table_halfw     = TableSize.table_halfw
    table_halfh     = TableSize.table_halfh
    
    
    
    # Sound effect setting
    pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
    pygame.mixer.init()
    pygame.init() #turn all of pygame on.
    local_path = os.getcwd()
    print(local_path)
    BeepFiles_path  = os.path.join(str(local_path), "resources","sounds","Beeps")
    if not os.path.exists(BeepFiles_path):
        os.makedirs(BeepFiles_path)
    Beep1 = pygame.mixer.Sound(os.path.join(str(BeepFiles_path), "cam.wav"))
    Beep2 = pygame.mixer.Sound(os.path.join(str(BeepFiles_path), "beep-07.wav"))
        
    
    
    
    cam = cv2.VideoCapture(camera_port)
    cv2.namedWindow("test")
    img_counter = 0

    # state machine. Currently, calibration is not used due to roi detection error and speed issue:WJS 20180509
    state = "calibration" # state: calibration -> shape_detection -> done

    while True:
        ret, frame = cam.read()
        
        # Create a black image
        instructions = np.zeros((512, 650, 3), np.uint8)

        # Write some Text

        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 100)
        fontScale = .7
        fontColor = (255, 255, 255)
        lineType = 2

        cv2.putText(instructions, 'Snapshot Instructions',
                    (10, 50),
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        cv2.putText(instructions, '1. Remove cup from camera view',
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        cv2.putText(instructions, '2. Press Space Bar to take a snapshot',
                    (10, 200),
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        cv2.putText(instructions, 'Press Space Bar again if shape detection unsatisfactory',
                    (10, 300),
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        cv2.putText(instructions, '3. Once you are satisfied place cup back on table ',
                    (10, 400),
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        cv2.putText(instructions, '4. Press Esc to start trial ',
                    (10, 500),
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        # Display the image
        cv2.imshow("instructions", instructions)
        
    # c,r,w,h = 200,100,70,70
#     roiBox = (c,r,w,h)
        frame = imutils.resize(frame, width=width)
        frame_copy = frame.copy() # copy for distortion matrix
#        frame = cv2.resize(frame, (width,height))

        nrmlz=1
        lefty = centery - nrmlz*table_halfh
        righty = centery + nrmlz*table_halfh
        leftx = centerx - nrmlz*table_halfw
        rightx = centerx + nrmlz*table_halfw
        
        
        
        cv2.circle(frame, (centerx, centery), 4, (0, 0, 255), 4)
        cv2.rectangle(frame, (leftx, lefty), (rightx, righty), (153, 255, 255), 3)
        #cv2.line(frame, (0, centery), (frame.shape[1], centery), (0, 0, 255), thickness=3, lineType=8)
        #cv2.line(frame, (centerx, 0), (centerx, frame.shape[0]), (0, 0, 255), thickness=3, lineType=8)
        cv2.circle(frame, (leftx, lefty), 8, (0, 0, 255), 4)
        cv2.circle(frame, (leftx, righty), 8, (0, 0, 255), 4)
        cv2.circle(frame, (rightx, lefty), 8, (0, 0, 255), 4)
        cv2.circle(frame, (rightx, righty), 8, (0, 0, 255), 4)
            
        if img_counter == 0:
            cv2.imshow("test", frame)
        else:
            cv2.imshow("test", detecting_frame)
            
        if not ret:
            break
        k = cv2.waitKey(1)
        
        #-------------------------- Escape and move on ----------------------------
        
        if k%256 == 27:
            # ESC pressed
            if img_counter > 0:
                #dataOutput_path= save_output_at("snapshots",str(args["subject"]))
                dataOutput_path= save_output_at(str(args["subject"])+"\\snapshots","")
                cv2.imwrite(os.path.join(dataOutput_path, timeTag+'.jpg'), prev_frame) # save snapshot image # FIX:CROSS PLATFORM
                dataOutput_path= save_output_at(str(args["subject"])+"\\pickles","")
                #dataOutput_path= save_output_at("pickles",str(args["subject"]))
                savefile_circles = os.path.join(dataOutput_path, timeTag+'_circles.dump' )# FIX:CROSS PLATFORM
                savefile_rectangles = os.path.join(dataOutput_path, timeTag+'_rectangles.dump' )# FIX:CROSS PLATFORM
                           
                pickle.dump(circles, open(savefile_circles, 'wb'))   # save circle characteristics
                pickle.dump(rectangles, open(savefile_rectangles, 'wb')) # save rectangles contours
                pickle.dump(timeTag, open("lastTimeTag.dump", 'wb')) # save the latest time tag.

                #plt.imsave("detected_shapes.png", np.hstack([frame, detecting_frame]))
                print("{} written!".format(savefile_circles))
                print("{} written!".format(savefile_rectangles))
                
            print("Escape hit, closing...")
            break
        
        
        
        
        ##------------------------------- Calibration --------------------------------
        
        elif k%256 == 67 or k%256 == 99: # C or c for calibration
            # calibration
 
            # Define the chess board rows and columns
            rows = 9
            cols = 6
            # termination criteria
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

            # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
            objp = np.zeros((cols*rows,3), np.float32)
            objp[:,:2] = np.mgrid[0:rows,0:cols].T.reshape(-1,2)

            # Arrays to store object points and image points from all the images.
            objectPointsArray = [] # 3d point in real world space
            imgPointsArray = [] # 2d points in image plane.
            
            
            
            # ------------------- Taking pictures -----------------------------
            PicPath= save_output_at(str(args["subject"])+"\\calibration_data"+"\\Raw Pictures",str(timeTag))
            NumPics = args["CalibPhotoNum"];
            print("====== Taking %d Pictures======"%NumPics)
            d=0
            time.sleep(2)
            Beep2.play(0,300)
            while d<NumPics:
                time.sleep(.5)
                Beep1.play()
                rt, pics = cam.read()
                filename = os.path.join(str(PicPath),"pic_%d_"%d +str(timeTag)+'.jpg')
                cv2.imwrite(filename, pics)
                d+=1
                
            
            
            print('-------------------Pictures all taken ---------------------')
            
            # ------------------ load the pictures and find the corners -----------------
            
            
            images = glob.glob(os.path.join(str(PicPath),'*.jpg'))
            print('number of images found in the directory: %d'%len(images))
            imgcnt = 0
            Corners_df = pd.DataFrame()
            FoundCorners = [] # This is a flag we use later to exclude pictures in which the corners were not found

            for fname in images:
                imgs = cv2.imread(fname)
                gray = cv2.cvtColor(imgs,cv2.COLOR_BGR2GRAY)
                imgcnt+= 1
                print("Loading image:  ","%d"%imgcnt , "/%d"%len(images))
                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, (rows,cols),None)
                # If found, add object points, image points (after refining them)
                if ret == True:
                    corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                    print('length of corners',len(corners2))
                    
                    # Add the object points and the image points to the arrays
                    objectPointsArray.append(objp)
                    imgPointsArray.append(corners2)
                    FoundCorners.append(True)
            
                    # generating a data frame to save later
                    dd = pd.DataFrame(corners2[:,0,:])
                    Corners_df = Corners_df.append(dd)
            
                    # Draw and display the corners
                    imgs = cv2.drawChessboardCorners(imgs, (rows,cols), corners2,ret)
                    cv2.imshow('images',imgs)
                    #PicPath2= save_output_at("calibration_data\\"+str(args["subject"]),"Processed Pictures_"+str(timeTag))
                    PicPath2= save_output_at(str(args["subject"])+"\\calibration_data"+"\\Processed Pictures",str(timeTag))
                    filename = os.path.join(PicPath2,"pic_%d_"%imgcnt +str(timeTag)+'.jpg' )
                    cv2.imwrite(filename, imgs)
                    cv2.waitKey(500)
            
            
            # find the distance between the corners

            for i in range(len(imgPointsArray)):
                for j in range(len(imgPointsArray[i])-1):
                    DD = cv2.norm(imgPointsArray[i][j+1], imgPointsArray[i][j], cv2.NORM_L2)
                    print("Distance between corners  %d"%i,",%d: "%j , DD)
            
            
            
            
            # ----------------- Now Calibrate --------------------------
            print('Calibration started now...')
            #dataOutput_path= save_output_at("calibration_data\\"+str(args["subject"]),"NPZ files")
            dataOutput_path= save_output_at(str(args["subject"])+"\\calibration_data","NPZ files")
            #dataOutput_path= os.path.join(PicPath,"NPZ files")
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objectPointsArray, imgPointsArray, gray.shape[::-1],None,None)
            np.savez(os.path.join(dataOutput_path,timeTag+'.npz'), mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
            tempdata = np.load(os.path.join(dataOutput_path,timeTag+'.npz'))
            print('test loading npz', tempdata['dist'])
            if not ret:
                print("Calibration NOT successful")
            
            
            
            
            # ------------------ Undistort the corners for measure calibration -----
            
            Corners_df.columns= ['X','Y']
            #CoordPath= save_output_at("calibration_data\\"+str(args["subject"]),"CornerCoords")
            CoordPath= save_output_at(str(args["subject"])+"\\calibration_data","CornerCoords")
            
            Corners_df.to_csv(os.path.join(str(CoordPath),'RawCoordinates_'+str(timeTag)+'.csv'))

            
            
            
            
            
            
            # ------------------ Calibration Error --------------------------------
            error = 0
            for i in range(len(objectPointsArray)):
                imgPoints, _ = cv2.projectPoints(objectPointsArray[i], rvecs[i], tvecs[i], mtx, dist)
                error += cv2.norm(imgPointsArray[i], imgPoints, cv2.NORM_L2)

            print("Total error: ", error / len(objectPointsArray))
            state = "calibration"
            
            
        # -------------------Take snapshot each time space bar pressed --------------------------        
        elif k%256 == 32:
            # SPACE pressed
            dataOutput_path= save_output_at(str(args["subject"])+"\\snapshots","")
            img_name = timeTag+".jpg"
            cv2.imwrite(os.path.join(dataOutput_path, timeTag+'.jpg'), frame)#  # FIX:CROSS PLATFORM

            time.sleep(1)
            # This is where different shapes are detected.
            circles, rectangles, detecting_frame = detectShapesInTable(dataOutput_path,img_name,  centerx, centery, table_halfw, table_halfh)

            prev_frame = frame.copy()
            img_counter += 1
            state = "done"

    cam.release()
    del cam
    cv2.destroyAllWindows()
    k = cv2.waitKey(1)    # Added by mohsen: if this is not here, it wont close the cv2 windows
    print(img_name)
    return img_name, circles, rectangles 









####### Load snapshots -------
    
def load_snapshot(args, TableSize, timeTag, camera_port):
    
    width           = TableSize.width
    centerx         = TableSize.centerx
    centery         = TableSize.centery
    table_halfw     = TableSize.table_halfw
    table_halfh     = TableSize.table_halfh
    
    
    if args.get("video", False):  # postprocessing
        vname = args["video"][1]

        timetag_circles = vname[:15] + "_circles.dump"
        timetag_rectangles =  vname[:15] + "_rectangles.dump"
        circles = pickle.load(open(os.path.join("Output",str(args["subject"]),"pickles", timetag_circles), 'rb')) #FIX: CROSS PLATFORM
        rectangles = pickle.load(open(os.path.join("Output", str(args["subject"]), "pickles",timetag_rectangles), 'rb')) #FIX: CROSS PLATFORM
        img_name =  vname[:15]+".png"
    else:  # just loading snapshot
        lastTimeTag = pickle.load(open("lastTimeTag.dump", 'rb'))
        print("last time tag",lastTimeTag)
    
        timetag_circles = lastTimeTag + "_circles.dump"
        timetag_rectangles =  lastTimeTag+ "_rectangles.dump"
        print(timetag_circles)
        print(timetag_rectangles)
        circles = pickle.load(open(os.path.join("Output", str(args["subject"]), "pickles",timetag_circles), 'rb')) #FIX: CROSS PLATFORM
        rectangles = pickle.load(open(os.path.join("Output", str(args["subject"]), "pickles",timetag_rectangles), 'rb')) #FIX: CROSS PLATFORM
        img_name = lastTimeTag+".png"
        #####  make a copied pickle data with new timeTag  ###########
        dataOutput_path= save_output_at(str(args["subject"]),"pickles")
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
    
    return img_name, circles, rectangles 










####################################################
###   take a first frame of the video           ####
###  update: this may not be needed at all if we use pickle
####################################################
    

def take_snapshot_from_video(args):
    vname = args['video']
    cam = cv2.VideoCapture(vname)
    # get vcap property 
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    centerx_video = int(width/2)
    centery_video = int(height/2)
    table_halfw_video = 250 # table half-width approx 
    table_halfh_video = 155 # table half-height approx 

    
    cv2.namedWindow("test")

    ret, frame = cam.read()
        
    frame = imutils.resize(frame, width=width, height = height)
    #frame = cv2.resize(frame, (width,height))

    #cv2.imwrite('snapshot_'+args['output']+'_'+timeTag+'.png', frame) #
    #cv2.imwrite(dataOutput_path+'/'+'raw_snapshot_'+args['output']+'_'+timeTag+'.png', frame) #

    ### extract timetag from video file name
    path, filename = os.path.split(vname)  # strip timetag from filename
    timetag_loaded =  filename[:15] + "."


    retreived_default_scores = pickle.load(open('tuple.dump', 'rb'))
    #circles, rectangles, detecting_frame = detectShapesInTable(timetag_loaded,  centerx_video, centery_video, table_halfw_video, table_halfh_video)
 
##    dataOutput_path= save_output_at("snapshots")
    #cv2.imwrite(dataOutput_path+'/'+timetag_loaded +'_video_'+args['output']+'.png', np.hstack([frame, detecting_frame])) #

##    dataOutput_path= save_output_at("pickles")
##    savefile = dataOutput_path+'/'+timetag_loaded+'.dump'
##    pickle.dump(circles, open(savefile, 'wb'))   # save circle characteristics
##    pickle.dump(rectangles, open(savefile, 'wb')) # save rectangles contours
##    print("{} written!".format(savefile))

    cam.release()
    cv2.destroyAllWindows()
    return timetag_loaded, circles, rectangles




####################################################
###   take a snap shot of a board from webcam   ####
####################################################
def check_camera(args, TableSize, timeTag, camera_port):
    
    width           = TableSize.width
    lefty           = TableSize.lefty
    righty          = TableSize.righty
    leftx           = TableSize.leftx
    rightx          = TableSize.rightx
    centerx         = TableSize.centerx
    centery         = TableSize.centery

    cam = cv2.VideoCapture(camera_port)
    cv2.namedWindow("Position_check")

    while True:
        ret, frame = cam.read()
        
        if not ret:
            print("Check Camera_port in main.py")
            break
        
        frame_copy = frame.copy()
        frame_copy = imutils.resize(frame_copy, width=width)
        mask = np.zeros(frame_copy.shape, np.uint8)
        
        #mask[lefty:righty , leftx:rightx] = frame[lefty:righty , leftx:rightx]
        #mask = imutils.resize(mask, width=width)
        mask[lefty:righty , leftx:rightx] = frame_copy[lefty:righty , leftx:rightx]
        

        cv2.circle(mask, (centerx, centery), 4, (0, 0, 255), 4)
        cv2.rectangle(mask, (leftx, lefty), (rightx, righty), (153, 255, 255), 3)
        cv2.line(mask, (0, centery), (mask.shape[1], centery), (255, 0, 255), thickness=3, lineType=8)
        cv2.line(mask, (centerx , 0), (centerx, mask.shape[0]), (255, 0, 255), thickness=3, lineType=8)
        cv2.circle(mask, (leftx , lefty), 8, (255, 0, 255), 4)
        cv2.circle(mask, (leftx , righty), 8, (255, 0, 255), 4)
        cv2.circle(mask, (rightx, lefty), 8, (255, 0, 255), 4)
        cv2.circle(mask, (rightx, righty), 8, (255, 0, 255), 4)

        # Create a black image
        img = np.zeros((400, 720, 3), np.uint8)

        # Write some Text

        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 100)
        fontScale = .7
        fontColor = (255, 255, 255)
        lineType = 2

        cv2.putText(img, 'OPTION 1: Press Esc to Start Trial',
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        cv2.putText(img, '      OR',
                    (10, 200),
                    font,
                    1.5,
                    fontColor,
                    lineType)

        cv2.putText(img, 'OPTION 2: Press s to take a Snapshot (on the initial trial only)',
                    (10, 300),
                    font,
                    fontScale,
                    fontColor,
                    lineType)

        # Display the image
        cv2.imshow("img", img)


        cv2.imshow("Position_check", mask)
        

        if not ret:
            break
        k = cv2.waitKey(1)
        
        if k%256 == 27:   # 27 is the number identifier for space bar
            # ESC pressed             
            print("Escape hit, closing...")
            need_to_take_snapshot = False
            break
        elif k%256 == 83 or k%256 == 115:  ## S or s (for snapshot)
            need_to_take_snapshot = True
            break

    cam.release()
    del cam
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    return need_to_take_snapshot












