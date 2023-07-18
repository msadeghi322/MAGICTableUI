#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 19:34:31 2019

@author: mohsensadeghi
"""


import numpy as np     
import cv2      # openCV pagage for computer vision and graphics (ms)



############## User-defined function: circle_tracking  =======================================================================================================

    # track minumum enclosing circle of this mask #######
    
def circle_tracking(hsvmask,TableSize,ColourRange):
    
    width = TableSize.width
    height = TableSize.height
    hsv = hsvmask
    hsvmask = cv2.inRange(hsv, ColourRange.greenLower, ColourRange.greenUpper) # determines the range of colour to be detected (ms)
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
        
        
        ### Projection down to xy plane. Adjustment based on cup height. ######
        x_center = width/2
        y_center = height/2
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

    return (xObject, yObject, radius, len(cnts))





############## User-defined function: ellipse_tracking  =======================================================================================================

    # track minimum enclosing elipse of this mask


def ellipse_tracking(hsvmask,TableSize,ColourRange):
    
    width = TableSize.width
    height = TableSize.height
    
    hsv = hsvmask
    hsvmask = cv2.inRange(hsv, ColourRange.orangeLower, ColourRange.orangeUpper) # cheap
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






############## User-defined function: ellipse_dual_tracking  =======================================================================================================
    
    # track two objects (both cup and ball)

def ellipse_dual_tracking(hsvmask,TableSize,ColourRange):

    width = TableSize.width
    height = TableSize.height
    
    hsv = hsvmask
    hsvmask_or = cv2.inRange(hsv, ColourRange.orangeLower, ColourRange.orangeUpper)  # cheap
    hsvmask_gr = cv2.inRange(hsv, ColourRange.greenLower, ColourRange.greenUpper)  # cheap
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
                #(x, y), (MA, ma), angle = cv2.fitEllipse(cnts[0])
                """circle fit"""
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                MA = 2*radius # for consistency with ellipse
                ma = 2*radius
                angle = 0

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
            xObject  = -1
            yObject  = -1
            radius   = -1
            MA       = 0
            ma       = 0
            angle    = 0
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




