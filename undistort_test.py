import cv2
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import csv

## Won Joon Sohn, Aug. 2019. 
# Helpful: https://stackoverflow.com/questions/47402445/need-help-in-understanding-error-for-cv2-undistortpoints

# file reading
calibrationFile = os.path.join("Output", "calibration_data", "20190820_202943.npz")
filename="Trial5"
fileloaded = filename + ".csv"
arrayfile = os.path.join("Output", "dataframeOutput", fileloaded)

# Remove the metadata lines 
meta_data_length = 18  # meta-data-length in csv -1
dfmeta = pd.read_csv(arrayfile, nrows = meta_data_length )
df = pd.read_csv(arrayfile, header = meta_data_length+1 )
nrows = len(df.xObject) - 1

# 2D array data
points = np.column_stack([df['xObject'], df['yObject']])
#print(points.shape)
points = points[:, np.newaxis, :]  # Expand the array to fit in to undistortPoints()


## load calibration data
calib = np.load(calibrationFile)
print(calib.files)
print('mtx:', calib['mtx'])
print('dist: ', calib['dist'])

# undistort 2D points
xy_undistorted = cv2.undistortPoints(points, calib['mtx'], calib['dist'])
fx = calib['mtx'][0][0]
fy = calib['mtx'][1][1]
cx = calib['mtx'][0][2]
cy = calib['mtx'][1][2]
print('fx: ', fx, 'fy: ', fy, 'cx: ', cx, 'cy: ', cy)
print('xy_undistorted shape  : ', xy_undistorted.shape)
print('xy_undistorted[:,0,0]  : ', xy_undistorted[:,0,0])

# A necessary step to calculate the normalization factor
xy_undistorted[:,0,0] = xy_undistorted[:,0,0]*fx+ cx  # fx: focal length, cx: boresight
xy_undistorted[:,0,1] = xy_undistorted[:,0,1]*fy+cy

# plotting 
fig, ax = plt.subplots()
sizes = len(df.xObject)*[3]
ax.scatter(df['xObject'], df['yObject'], c='black', s=sizes, label='orig', alpha=0.8) # original
ax.scatter(xy_undistorted[:,0,0], xy_undistorted[:,0,1], c='blue', s=sizes, label='corrected', alpha=0.8) #undistored
ax.legend()
fig.suptitle(filename, fontsize=16)
plt.savefig(os.path.join("Output", filename+"_plot.png")) # save to figure
plt.show()

# save to file
df = pd.DataFrame({"xObject_corrected" : xy_undistorted[:,0,0], "yObject_corrected" : xy_undistorted[:,0,1]})
df.to_csv(os.path.join("Output", "dataframeOutput", filename+"_corrected.csv"), index=True)


