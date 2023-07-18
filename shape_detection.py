import cv2
import numpy as np
import os

####################################################
###   detect circular start / end region        ####
####################################################    
def detect_circle(img_name):
    # load the image, clone it for output, and then convert it to grayscale
    img = cv2.imread(img_name)
    print(img_name)
    
    output = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
##    cv2.imshow("output", output)

    # detect circles in the image
    circles = cv2.HoughCircles(image=gray, method=cv2.HOUGH_GRADIENT, dp=1.6, minDist=100,
                               param1=50,param2=70,minRadius=10,maxRadius=150)

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(output, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    #cv2.imshow("output", output)

    #plt.imsave("detected_circles.png", np.hstack([img, output]))
    return circles

####################################################
### find rectangular obstacles, return vertices ####
####################################################    
def detect_obstacles(img_name):
    img2 = cv2.imread(img_name)
    print(img_name)
    
    output = img2.copy()
    gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    # find contours in the edged image, keep only the largest
    # ones, and initialize our screen contour
    contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
    rectangles = []
    
    # loop over our contours
    for c in contours:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        print("c:, ", c, " peri:  ", peri)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
 
        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:          
            cv2.drawContours(output, [approx], -1, (0, 128, 255), 3)
            rectangles.append(approx)
##    cv2.imshow("Game Boy Screen", img2)
##    cv2.waitKey(0)
    #plt.imsave("detected_obstacles.png", np.hstack([img2, output]))

    print(len(rectangles))
    return rectangles



#########################################################
###   detect circle / obstacles in the table region  ####
#########################################################

def detectShapesInTable(imagepath, img_name, centerx, centery, table_halfw, table_halfh ):
        path_filename = os.path.join(imagepath, img_name) # FIX:CROSS PLATFORM
        print("path ", path_filename)
        img2 = cv2.imread(path_filename)
        print(img_name)
        #### detect circle . If not satisfied, keep pressing space key for re-detection.######
        ## mask out the table from the zoomed out image
        rec_mask = np.zeros(img2.shape[:2],np.uint8)
        pad = 5
        rec_mask[centery-table_halfh+pad:centery+table_halfh-pad,centerx-table_halfw+pad:centerx+table_halfw-pad] = 255
        masked_frame = cv2.bitwise_and(img2,img2, mask =rec_mask)
        #cv2.imshow("mask", masked_frame)
        
        gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
        # detect circles in the image
        circles = cv2.HoughCircles(image=gray, method=cv2.HOUGH_GRADIENT, dp=1.6, minDist=100,
                                   param1=50,param2=70,minRadius=10,maxRadius=120)

        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # loop over the (x, y) coordinates and radius of the circles
            # remove circles out side of defined table region
            ind = 0
            print("circles:", circles)
            index_to_keep =[]

            for (x, y, r) in circles:
                    # draw the circle in the output image, then draw a rectangle
                    # corresponding to the center of the circle
                    cv2.circle(img2, (x, y), r, (0, 255, 0), 4)
                    cv2.rectangle(img2, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        
        #cv2.imshow("output", output)

        ###### detect obstacles
        gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)

        # find contours in the edged image, keep only the largest
        # ones, and initialize our screen contour
        #_,contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # (obsolete)
        contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # (new 2019)

        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
        rectangles = []
        
        # loop over our contours
        for c in contours:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            if peri > 500: # skip the too large rectangles
                continue
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # if our approximated contour has four points, then
            # we can assume that we have found our screen
            if len(approx) == 4:          
                cv2.drawContours(img2, [approx], -1, (0, 128, 255), 3)
                rectangles.append(approx)

        detecting_frame = img2.copy()

        return circles, rectangles, detecting_frame
