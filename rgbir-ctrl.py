#!/usr/bin/env python2.7
import time
import sys
import os

sys.path.append(os.path.join(sys.path[0], "AS7262_Pi/"))
import AS7262_Pi as spec

import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=0)
pwm.set_pwm_freq(60)

spec.soft_reset()
spec.set_gain(3)
spec.set_integration_time(50)
spec.set_measurement_mode(2)

#turn of all leds
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

        results = spec.get_calibrated_values()

        print("Red    :" + str(results[0]))
        print("Orange :" + str(results[1]))
        print("Yellow :" + str(results[2]))
        print("Green  :" + str(results[3]))
        print("Blue   :" + str(results[4]))
        print("Violet :" + str(results[5]) + "\n")

except KeyboardInterrupt:
    spec.set_measurement_mode(3)
    #spec.disable_main_led()
