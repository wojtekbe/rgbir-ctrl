#!/bin/bash
gst-launch-1.0 -vvv udpsrc port=5000 ! application/x-rtp ! rtph264depay ! avdec_h264 ! xvimagesink sync=false
