import Adafruit_PCA9685

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
            self.set(self.nchannels*[0])

    def set(self, setp):
        self.setp = setp[:6]
        if self.controller is not None:
            for i,v in enumerate(self.setp):
                if v>=0:
                    if v > 100.0: v = 100.0
                    v_pwm = (0xfff-int(v*0xfff/100.0))
                    self.controller.set_pwm(i, 0, v_pwm)

    def close(self):
        if self.controller is not None:
            self.set(self.nchannels*[0])
