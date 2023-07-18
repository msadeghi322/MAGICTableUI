
import numpy as np
import cv2
import imutils
import cv2 as cv
import glob
from save import save_output_at, save_video, plot_and_save_data, save_dataframe
import time
from shape_detection import detect_circle, detect_obstacles, detectShapesInTable
import os




fpath = './Output/calibration_data/'
fname = '20181114_165224' # 20181114_150134
tempdata = np.load(fpath+fname+'.npz')
dist = tempdata['dist'] # distortion coefficients
mtx = tempdata['mtx'] # 3x3 camera matrix (focal length, optical centers etc), note that you dont need to get this again unless you change the focal length etc..

img = cv.imread(fpath+fname+'.jpg')
cv2.imshow('img', img)
cv2.waitKey(0)

h, w = img.shape[:2]
print(dist)
print(mtx)
#dist[2:4] = 0

dist[0][2:5]=0   # no translation. hard coding
print(dist)


print('w:',w, ' h: ', h )
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
#images = glob.glob('./Output/calibration_data/20181113_125926.npz')

dst = cv2.undistort((100,100), mtx, dist, None, newcameramtx)
print('mapped point:', dst)

# line_array =
# undist_line_array = cv2.undistort(line_array, mtx, dist, None, newcameramtx)

""" for test, load a csv and undistort a line. """
import pandas as pd
fpath = './Output/dataframeOutput/'
fname='20181114_165753_condition_iw_M11_computer0_Tracking_success1'
df=pd.read_csv(fpath+fname+'.csv',  skiprows=range(0,13))
#df.to_csv(fpath+fname+'_NoMeta.csv', sep=',', encoding='utf-8', index=False)
#df2=pd.read_csv(fpath+fname+'_NoMeta.csv')
print(list(df))
import matplotlib.pyplot as plt

plt.plot(df['xObject'], df['yObject'])
plt.show()
print('img ', img[1:2])
xy_array=df.as_matrix(columns=df.columns[2:4])
print('xy ', xy_array[1:5])
undist_line_array = cv2.undistort(xy_array, mtx, dist, None, newcameramtx)
plt.plot(undist_line_array)
plt.show()
print(undist_line_array)
# print('dimension:', undist_line_array.shape)
# print('undist[0]:', undist_line_array[0])
# print('undist[1]:', undist_line_array[1])
# plt.plot(undist_line_array[:,0], undist_line_array[:,1])
# plt.show()

k1 =  dist[0][0]
k2 =  dist[0][1]
k3 =  dist[0][4]
import math
cx = mtx[0][2]
cy = mtx[1][2]
fx = mtx[0][0]
fy = mtx[1][1]
print('cx:', cx, ' cy: ', cy)

x_crt_list = []
y_crt_list = []

for i in range(0, len(df['xObject'])):
    x =df['xObject'][i]
    y= df['yObject'][i]
    x_sc = (x-cx) / fx
    y_sc = (y-cy) / fy
    r_sc2 = x_sc*x_sc+y_sc*y_sc
    # distance=math.sqrt((c1-x)**2+(c2-y)**2)
    distortion = 1+r_sc2*(k1+r_sc2*k2)
    #r = distance / correctionRadius
    #x_crt = x+(x-c1)*(k1*r**2 + k2*r**4)
    #y_crt = y+(y-c2)*(k1*r**2 + k2*r**4)
    x_crt=x_sc*(1+k1*r_sc2 + k2*r_sc2*r_sc2)
    y_crt=y_sc*(1+k1*r_sc2 + k2*r_sc2*r_sc2)
    # step2
    # x_crt = x_crt*fx+cx
    # y_crt = y_crt*fy+cy
    x_crt = fx*distortion*x_sc + cx
    y_crt = fy*distortion *y_sc+ cy

    x_crt_list.append(x_crt)
    y_crt_list.append(y_crt)


plt.plot(x_crt_list, y_crt_list)
plt.show()

#x_crt = [x*(1+k1*r**2 + k2*r**4 + k3*r**6) for x in df['xObject'] ]# corrected
#y_crt =[ y*(1+k1*r**2 + k2*r**4 + k3*r**6) for y in df['yObject']]# corrected

# crop
# x, y, w, h = roi
# print(x, y, w, h)
# dst = dst[y:y+h, x:x+w]
# cv.imwrite(fpath+fname+'_calibrated.jpg', dst)
