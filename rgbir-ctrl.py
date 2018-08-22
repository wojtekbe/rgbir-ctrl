#!/usr/bin/env python2.7
import time
import sys
import os

import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
l = logging.getLogger(__name__)

from camera import Camera
import numpy as np
import cv2
DISPLAY = False

sys.path.append(os.path.join(sys.path[0], "AS7262_Pi/"))
import AS7262_Pi

import Adafruit_PCA9685
#TODO: do not fail if chip not connected
try:
    lights = Adafruit_PCA9685.PCA9685(address=0x41, busnum=0)
    lights.set_pwm_freq(60)
except IOError:
    l.error("PCA9685 not connected?")
    lights = None

#TODO: demosaic arr (RGB+I) with G doubling
#TODO: 3d print AS726x handle
#TODO: features vs lighting opt. alg. (1. find optimal lighting)
#TODO: own demosaic alg. (2. find optimal demosaic scheme)

cam = Camera()

spec_vis = AS7262_Pi.AS726X(busnum=0)
spec_vis.soft_reset()
spec_vis.set_gain(3)
spec_vis.set_integration_time(50)
spec_vis.set_measurement_mode(2)

spec_ir = AS7262_Pi.AS726X(busnum=1)
spec_ir.soft_reset()
spec_ir.set_gain(3)
spec_ir.set_integration_time(50)
spec_ir.set_measurement_mode(2)

if lights is not None:
    for chn in xrange(6):
        lights.set_pwm(chn, 0, 0xfff)

chn = 0

try:
    #spec.enable_main_led()
    while True:
        img = cam.get_frame()
        print img.size
        print img.shape
        img = img * 64
        if DISPLAY:
            cv2.imshow('image', img)
            cv2.waitKey(1)

        if lights is not None:
            chn = (chn+1)%6
            lights.set_pwm(chn, 0, 0xfef)
            time.sleep(0.1)
            lights.set_pwm(chn, 0, 0xfff)

        results_vis = spec_vis.get_calibrated_values()

        print("Red    :" + str(results_vis[0]))
        print("Orange :" + str(results_vis[1]))
        print("Yellow :" + str(results_vis[2]))
        print("Green  :" + str(results_vis[3]))
        print("Blue   :" + str(results_vis[4]))
        print("Violet :" + str(results_vis[5]) + "\n")

        results_ir = spec_ir.get_calibrated_values()

        print("IR 1:" + str(results_ir[0]))
        print("IR 2:" + str(results_ir[1]))
        print("IR 3:" + str(results_ir[2]))
        print("IR 4:" + str(results_ir[3]))
        print("IR 5:" + str(results_ir[4]))
        print("IR 6:" + str(results_ir[5]) + "\n")

except KeyboardInterrupt:
    if DISPLAY:
        cv2.destroyAllWindows()
    cam.close()
    spec_vis.set_measurement_mode(3)
    spec_ir.set_measurement_mode(3)
    #spec.disable_main_led()
