#!/usr/bin/env python2.7
import time
import sys
import os

import v4l2
import fcntl
import mmap
import select
import time

import numpy as np
import cv2

sys.path.append(os.path.join(sys.path[0], "AS7262_Pi/"))
import AS7262_Pi

import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=0)
pwm.set_pwm_freq(60)

W = 1920
H = 1080

#TODO: demosaic arr (RGB+I) with G doubling
#TODO: 3d print AS726x handle
#TODO: features vs lighting opt. alg. (1. find optimal lighting)
#TODO: own demosaic alg. (2. find optimal demosaic scheme)

def get_frame():
    #open
    vd = open('/dev/video0', 'rb+', buffering=0)

    #quercap
    cp = v4l2.v4l2_capability()
    fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)

    #s_fmt
    fmt = v4l2.v4l2_format()
    fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    fmt.fmt.pix.width = W
    fmt.fmt.pix.height = H
    fmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_SBGGR10
    fmt.fmt.pix.field = v4l2.V4L2_FIELD_NONE
    fcntl.ioctl(vd, v4l2.VIDIOC_S_FMT, fmt) # set whatever default settings we got before

    fmt = v4l2.v4l2_format()
    fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    fcntl.ioctl(vd, v4l2.VIDIOC_G_FMT, fmt)
    framesize = fmt.fmt.pix.sizeimage

    #reqbufs
    req = v4l2.v4l2_requestbuffers()
    req.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    req.memory = v4l2.V4L2_MEMORY_MMAP
    req.count = 1
    fcntl.ioctl(vd, v4l2.VIDIOC_REQBUFS, req)

    buffers = []
    for ind in range(req.count):
        #querybufs
        buf = v4l2.v4l2_buffer()
        buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = v4l2.V4L2_MEMORY_MMAP
        buf.index = ind
        fcntl.ioctl(vd, v4l2.VIDIOC_QUERYBUF, buf)

        #mmap
        mm = mmap.mmap(vd.fileno(), buf.length, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=buf.m.offset)
        buffers.append(mm)

        #qbuf
        fcntl.ioctl(vd, v4l2.VIDIOC_QBUF, buf)

    #streamon
    buf_type = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
    fcntl.ioctl(vd, v4l2.VIDIOC_STREAMON, buf_type)

    #select
    t0 = time.time()
    max_t = 1
    ready_to_read, ready_to_write, in_error = ([], [], [])
    while len(ready_to_read) == 0 and time.time() - t0 < max_t:
        ready_to_read, ready_to_write, in_error = select.select([vd], [], [], max_t)

    #dqbuf
    buf = v4l2.v4l2_buffer()
    buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    buf.memory = v4l2.V4L2_MEMORY_MMAP
    fcntl.ioctl(vd, v4l2.VIDIOC_DQBUF, buf)

    #do something with this buffer
    mm = buffers[buf.index]
    frame = mm.read(framesize)
    #save as jpg using opencv/numpy
    arr = np.fromstring(frame, dtype=np.uint16).reshape(H, W)
    cv2.imwrite('image.jpg', arr)
    arr_rgb = cv2.cvtColor(arr, cv2.COLOR_BAYER_GR2BGR)
    cv2.imwrite('image_rgb.jpg', arr_rgb)
    #save RAW
    out = open("image.raw", "wb")
    out.write(frame)
    out.close()

    #qbuf
    fcntl.ioctl(vd, v4l2.VIDIOC_QBUF, buf)

    #streamoff
    fcntl.ioctl(vd, v4l2.VIDIOC_STREAMOFF, buf_type)

    #close
    vd.close()

get_frame()

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

for c in xrange(6):
    pwm.set_pwm(c, 0, 0xfff)

chn = 0

try:
    #spec.enable_main_led()
    while True:
        chn = (chn+1)%6
        pwm.set_pwm(chn, 0, 0xfef)
        time.sleep(0.1)
        pwm.set_pwm(chn, 0, 0xfff)

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
    spec_vs.set_measurement_mode(3)
    spec_ir.set_measurement_mode(3)
    #spec.disable_main_led()
