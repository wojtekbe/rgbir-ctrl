#!/usr/bin/env python2.7
import time
import sys

import logging
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
l = logging.getLogger(__name__)

from camera import Camera
import numpy as np
import cv2

#import dataout
import sensors
import lights

PREVIEW=True

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

cam = Camera()
spec = sensors.Spectro()
leds = lights.LEDs(l)

#calib_lights(led_v=15)

if PREVIEW:
    out_h264 = cv2.VideoWriter("appsrc ! videoconvert ! omxh264enc insert-sps-pps=true ! rtph264pay ! udpsink host=192.168.1.84 port=5000 sync=false", 0, 25.0, (640, 480))

try:
    while True:
        img = cam.get_frame()

        #convert color depth: 10b -> 16b
        img = (img / 4).astype(np.uint8)

        #demosaic as RGB
        #img_raw_cvt = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2BGR)

        #demosaic as RGBIR
        (img_rgb, img_ir) = demosaic(img)

        if PREVIEW:
            img_prev = cv2.resize(img_rgb, (640, 480)).astype(np.uint8)
            out_h264.write(img_prev)

        #turn off all lights)
        leds.set(chn=lights.ALL_CHANNELS, val=0)


except KeyboardInterrupt:
    cam.close()
    if PREVIEW:
        out_h264.release()
    spec.close()
    leds.close()
