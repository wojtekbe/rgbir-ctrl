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

#import dataout
import sensors
import lights

def calib_lights(led_v):
    for i in range(6):
        leds.set(chn=lights.ALL_CHANNELS, val=0)
        leds.set(chn=i, val=led_v)
        time.sleep(1)
        sp_data = spec.get()
        print(sp_data)
        #dataout.log([i] + sp_data)

#TODO: demosaic arr (RGB+I) with G doubling
#TODO: 3d print AS726x handle
#TODO: features vs lighting opt. alg. (1. find optimal lighting)
#TODO: own demosaic alg. (2. find optimal demosaic scheme)

cam = Camera()
spec = sensors.Spectro()
leds = lights.LEDs(l)

calib_lights(led_v=15)

try:
    while True:
        img = cam.get_frame()
        print img.size
        print img.shape
        img = img * 64
        if DISPLAY:
            cv2.imshow('image', img)
            cv2.waitKey(1)

        #turn off all lights)
        leds.set(chn=lights.ALL_CHANNELS, val=0)

        time.sleep(1)

except KeyboardInterrupt:
    if DISPLAY:
        cv2.destroyAllWindows()
    cam.close()
    spec.close()
    leds.close()
