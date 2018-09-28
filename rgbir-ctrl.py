#!/usr/bin/env python2.7
import time
import sys

import logging
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
l = logging.getLogger(__name__)

from camera import Camera
import numpy as np
import cv2
DISPLAY = False

import sensors
import lights

#TODO: demosaic arr (RGB+I) with G doubling
#TODO: 3d print AS726x handle
#TODO: features vs lighting opt. alg. (1. find optimal lighting)
#TODO: own demosaic alg. (2. find optimal demosaic scheme)

cam = Camera()
spec = sensors.Spectro()
lights = lights.LEDs(l)

try:
    while True:
        img = cam.get_frame()
        print img.size
        print img.shape
        img = img * 64
        if DISPLAY:
            cv2.imshow('image', img)
           cv2.waitKey(1)

        spec.get()
        spec.show()

        lights.set([4, 0, 0, 0, 2, 0])

except KeyboardInterrupt:
    if DISPLAY:
        cv2.destroyAllWindows()
    cam.close()
    spec.close()
    lights.close()
