import Adafruit_PCA9685

ALL_CHANNELS = -1
class LEDs:
    def __init__(self, l):
        self.nchannels = 6
        self.setp = self.nchannels*[0.0]

        #detect controller
        try:
            self.controller = Adafruit_PCA9685.PCA9685(address=0x41, busnum=0)
        except IOError:
            l.error("PCA9685 not connected?")
            self.controller = None

        #config
        if self.controller is not None:
            self.controller.set_pwm_freq(60)
            self.set(self, self.nchannels*[0])

    def set(self, data=None, chn=ALL_CHANNELS, val=0):
        if self.controller is not None:
            if data is None:
                if (chn==ALL_CHANNELS):
                    self.setp = self.nchannels*[val]
                else:
                    self.setp = self.nchannels*[-1]
                    self.setp[chn] = val

            print(self.setp)
            for i in range(self.nchannels):
                if self.setp[i]>=0:
                    if self.setp[i]>100.0: self.setp=100.0
                    v_pwm = (0xfff-int(self.setp[i]*0xfff/100.0))
                    self.controller.set_pwm(i, 0, v_pwm)

    def close(self):
        if self.controller is not None:
            self.set(self.nchannels*[0])
