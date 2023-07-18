import sys

import cv2
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi


class Life2Coding(QDialog):
    def __init__(self):
        super(Life2Coding, self).__init__()
        loadUi('life2coding.ui', self)
        self.image = None
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)

        self.trackButton.setCheckable(True)
        self.trackButton.toggled.connect(self.track_webcam_color)
        self.track_Enabled=False

        self.color1_Button.clicked.connect(self.setColor1)

    def track_webcam_color(self, status):
        if status:
            self.track_Enabled=True
            self.trackButton.setText('Stop Tracking')
        else:
            self.track_Enabled= False
            self.trackButton.setText('Track Color')

    def setColor1(self):
        self.color1_lower = np.array([self.hMin.value(), self.sMin.value(), self.vMin.value()], np.uint8)
        self.color1_upper = np.array([self.hMax.value(), self.sMax.value(), self.vMax.value()], np.uint8)

        self.color1_Label.setText('Min :'+str(self.color1_lower) + ' Max: '+str(self.color1_upper))


    def start_webcam(self):
        self.capture=cv2.VideoCapture(2)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.image=cv2.flip(self.image, 1)
        self.displayImage(self.image, 1)

        hsv=cv2.cvtColor(self.image,  cv2.COLOR_BGR2HSV)

        color_lower= np.array([self.hMin.value(), self.sMin.value(), self.vMin.value()], np.uint8)
        color_upper = np.array([self.hMax.value(), self.sMax.value(), self.vMax.value()], np.uint8)

        color_mask=cv2.inRange(hsv, color_lower, color_upper)
        self.displayImage(color_mask, 2)

        if (self.track_Enabled and self.color1_Check.isChecked()):
            trackedImage=self.track_colored_object(self.image.copy())
            self.displayImage(trackedImage,1)
        else:
            self.displayImage(self.image,1)

    def track_colored_object(self,img):
        blur=cv2.blur(img, (3,3))
        hsv=cv2.cvtColor(img,  cv2.COLOR_BGR2HSV)

        color_mask=cv2.inRange(hsv, self.color1_lower, self.color1_upper)
        erode=cv2.erode(color_mask, None, iteration=2)
        dilate = cv2.dilate(erode, None, iteration=10)

        kernelOpen=np.ones((5,5))
        kernelClose=np.ones((20,20))

        maskOpen=cv2.morphologyEx(dilate, cv2.MORPH_OPEN, kernelOpen)
        maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)

        (_, contours, hierarchy) = cv2.findContours(maskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area=cv2.contourArea(cnt)
            if (area > 5000):
                x, y, w, h=cv2.boundingRect(cnt)
                img=cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
                cv2.putText(img, 'Object Detected', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return img
                
                


    def stop_webcam(self):
        self.timer.stop()

    def displayImage(self, img, window=1):
        qformat=QImage.Format_Indexed8
        if len(img.shape)==3:  #[0]=row, [1]=cols, [2]=channels
            if img.shape[2]==4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        # BGR >> RGB
        outImage = outImage.rgbSwapped()

        if window==1:
            self.imgLabel1.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel1.setScaledContents(True)
        if window==2:
            self.processedLabel.setPixmap(QPixmap.fromImage(outImage))
            self.processedLabel.setScaledContents(True)


if __name__=='__main__':
    app=QApplication(sys.argv)
    window = Life2Coding()
    window.setWindowTitle('Life2Coding PyQt5 Tutorials')
    window.show()
    sys.exit(app.exec_())
