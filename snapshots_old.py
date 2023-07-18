import cv2
import imutils
from save import save_output_at, save_video, save_dataframe
import time
from shape_detection import detect_circle, detect_obstacles, detectShapesInTable
import pickle
import numpy as np
import glob
import os


####################################################
###   take a snap shot of a board from webcam   ####
####################################################
def take_snapshot(args, width, centerx, centery, table_halfw, table_halfh, timeTag, camera_port):
    cam = cv2.VideoCapture(camera_port)
    cv2.namedWindow("test")
    img_counter = 0

    # state machine. Currently, calibration is not used due to roi detection error and speed issue:WJS 20180509
    state = "calibration" # state: calibration -> shape_detection -> done

    while True:
        ret, frame = cam.read()
        
    # c,r,w,h = 200,100,70,70
#     roiBox = (c,r,w,h)
        frame = imutils.resize(frame, width=width)
        frame_copy = frame.copy() # copy for distortion matrix
#        frame = cv2.resize(frame, (width,height))


        cv2.circle(frame, (centerx, centery), 4, (0, 0, 255), 4)
        cv2.rectangle(frame, (centerx- table_halfw, centery - table_halfh), (centerx + table_halfw, centery+ table_halfh), (153, 255, 255), 3)
        #cv2.line(frame, (0, centery), (frame.shape[1], centery), (0, 0, 255), thickness=3, lineType=8)
        #cv2.line(frame, (centerx, 0), (centerx, frame.shape[0]), (0, 0, 255), thickness=3, lineType=8)
        cv2.circle(frame, (centerx- table_halfw, centery - table_halfh), 8, (0, 0, 255), 4)
        cv2.circle(frame, (centerx- table_halfw, centery + table_halfh), 8, (0, 0, 255), 4)
        cv2.circle(frame, (centerx+ table_halfw, centery - table_halfh), 8, (0, 0, 255), 4)
        cv2.circle(frame, (centerx+ table_halfw, centery + table_halfh), 8, (0, 0, 255), 4)
            
        if img_counter == 0:
            cv2.imshow("test", frame)
        else:
            cv2.imshow("test", detecting_frame)
            
        if not ret:
            break
        k = cv2.waitKey(1)
        
        if k%256 == 27:
            # ESC pressed
            if img_counter > 0:
                dataOutput_path= save_output_at("snapshots")
                #cv2.imwrite(dataOutput_path+'/'+timeTag+'.png', prev_frame) # save snapshot image # FIX:CROSS PLATFORM
                cv2.imwrite(os.path.join(dataOutput_path, timeTag+'.jpg'), prev_frame) # save snapshot image # FIX:CROSS PLATFORM
                dataOutput_path= save_output_at("pickles")
                #savefile_circles = dataOutput_path+'/'+timeTag+'_circles.dump' # FIX:CROSS PLATFORM
                #savefile_rectangles = dataOutput_path+'/'+timeTag+'_rectangles.dump' # FIX:CROSS PLATFORM
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

            #dataOutput_path= save_output_at("snapshots")  # to load snapshot photo
            #images = glob.glob(os.path.join(dataOutput_path, timeTag+'.jpg')) # dataOutput_path for snapshot
            #print 'image read for calibration: ', images

            ## was: for loop
            #img = cv2.imread(frame)
            
            gray = cv2.cvtColor(frame_copy,cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (rows,cols),None)
            print('corners: ',corners)

            # If found, add object points, image points (after refining them)
            if ret:        
                # REFINE THE CORNER POSITION 
                corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)# tune accuracy

                # Add the object points and the image points to the arrays
                objectPointsArray.append(objp)
                imgPointsArray.append(corners2)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(frame_copy, (rows,cols), corners2,ret)
                cv2.imshow('img',img)
                dataOutput_path= save_output_at("calibration_data")
                cv2.imwrite(os.path.join(dataOutput_path, timeTag+'.jpg'), img)
                cv2.waitKey(1000)

                # camera calibration
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objectPointsArray, imgPointsArray, gray.shape[::-1],None,None)
                np.savez(os.path.join(dataOutput_path,timeTag+'.npz'), mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
                tempdata = np.load(os.path.join(dataOutput_path,timeTag+'.npz'))
                print('loaded npz', tempdata['dist'])

                # Print the camera calibration error
                error = 0

                for i in range(len(objectPointsArray)):
                    imgPoints, _ = cv2.projectPoints(objectPointsArray[i], rvecs[i], tvecs[i], mtx, dist)
                    error += cv2.norm(imgPointsArray[i], imgPoints, cv2.NORM_L2) / len(imgPoints)

                print("Total error: ", error / len(objectPointsArray))
                state = "calibration"

            else:  # chess pattern detection failed
                print("Calibration failed. Reposition the chess board and try again.")
                
                
        elif k%256 == 32:
            # SPACE pressed
            dataOutput_path= save_output_at("snapshots")
            img_name = timeTag+".jpg"
            cv2.imwrite(os.path.join(dataOutput_path, timeTag+'.jpg'), frame)#  # FIX:CROSS PLATFORM

            time.sleep(1)
            circles, rectangles, detecting_frame = detectShapesInTable(img_name,  centerx, centery, table_halfw, table_halfh)

            prev_frame = frame.copy()
            img_counter += 1
            state = "done"

    cam.release()
    cv2.destroyAllWindows()
    print(img_name)
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
