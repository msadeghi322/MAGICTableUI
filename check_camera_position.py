import cv2
import imutils
import numpy as np
import time

####################################################
###   take a snap shot of a board from webcam   ####
####################################################
def check_camera(args, TableSize, timeTag, camera_port):
    
    width           = TableSize.width
    centerx         = TableSize.centerx
    centery         = TableSize.centery
    table_halfw     = TableSize.table_halfw
    table_halfh     = TableSize.table_halfh
    
    cam = cv2.VideoCapture(camera_port)
    cv2.namedWindow("Position_check")

    while True:
        ret, frame = cam.read()
        
        if not ret:
            print("Check Camera_port in main.py")
            break

        mask = np.zeros(frame.shape, np.uint8)
        lefty = centery - table_halfh
        righty= centery + table_halfh
        leftx = centerx - table_halfw
        rightx = centerx + table_halfw
         
         
        # lefty  = centery - table_halfh
        # righty = mask.shape[0]/2 + 3*table_halfh
        # leftx  = mask.shape[1]/2 - table_halfw
        # rightx = mask.shape[1]/2 + 3*table_halfw
        
        #tmp = True
        #if tmp:
        #    print("dimensions:" ,rightx-leftx , righty-lefty)
        #    tmp=False
        
        
        mask[lefty:righty , leftx:rightx] = frame[lefty:righty , leftx:rightx]

        cv2.circle(mask, (centerx, centery), 4, (0, 0, 255), 4)
        cv2.rectangle(mask, (centerx- table_halfw, centery - table_halfh), (centerx + table_halfw, centery+ table_halfh), (153, 255, 255), 3)
        cv2.line(mask, (0, centery), (mask.shape[1], centery), (255, 0, 255), thickness=3, lineType=8)
        cv2.line(mask, (centerx, 0), (centerx, mask.shape[0]), (255, 0, 255), thickness=3, lineType=8)
        cv2.circle(mask, (centerx- table_halfw, centery - table_halfh), 8, (255, 0, 255), 4)
        cv2.circle(mask, (centerx- table_halfw, centery + table_halfh), 8, (255, 0, 255), 4)
        cv2.circle(mask, (centerx+ table_halfw, centery - table_halfh), 8, (255, 0, 255), 4)
        cv2.circle(mask, (centerx+ table_halfw, centery + table_halfh), 8, (255, 0, 255), 4)

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
            
