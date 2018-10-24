#!/usr/bin/env python2.7
from camera import Camera
import cv2
cam = Camera()
img = cam.get_frame()
fname="frame.pgm"
print("Saving into " + fname + " " + str(img.shape[1]) + "x" + str(img.shape[0]) + " " + str(img.size) + "B")
cv2.imwrite(fname, img)
cam.close()
