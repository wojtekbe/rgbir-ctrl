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

#demosaic to RGB and IR (separately)
def demosaic(img):
    (h, w) = img.shape

    #copy G -> IR
    img_g = np.copy(img)
    img_g[1:h:2, 0:w:2] = img[0:h:2, 1:w:2]

    #copy IR -> new image
    img_ir = np.zeros((h/2, w/2), img.dtype)
    img_ir = img[1:h:2, 0:w:2]

    #demosaic
    img_rgb = cv2.cvtColor(img_g, cv2.COLOR_BAYER_RG2BGR)

    return (img_rgb, img_ir)


#TODO: 3d print AS726x handle
#TODO: features vs lighting opt. alg. (1. find optimal lighting)
#TODO: own demosaic alg. (2. find optimal demosaic scheme)

cam = Camera()
spec = sensors.Spectro()
leds = lights.LEDs(l)

#calib_lights(led_v=15)

try:
    while True:
        img = cam.get_frame()
        print img.size
        print img.shape

        #color depth: 10b -> 16b
        img = img * 64
        cv2.imwrite('frame_raw.png', img)

        img_raw_cvt = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2BGR)
        cv2.imwrite('frame_raw_cvt.png', img_raw_cvt)

        (img_rgb, img_ir) = demosaic(img)
        cv2.imwrite('frame_rgb.png', img_rgb)
        cv2.imwrite('frame_ir.png', img_ir)

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
