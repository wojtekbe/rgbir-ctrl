import os
import sys
sys.path.append(os.path.join(sys.path[0], "AS7262_Pi/"))
import AS7262_Pi

class Spectro:
    def __init__(self):
        self.R = 12 * [0]
        self.spec_vis = AS7262_Pi.AS726X(busnum=0)
        self.spec_ir = AS7262_Pi.AS726X(busnum=1)

        self.spec_vis.soft_reset()
        self.spec_ir.soft_reset()

        self.spec_vis.set_gain(3)
        self.spec_ir.set_gain(3)
        self.spec_vis.set_integration_time(50)
        self.spec_ir.set_integration_time(50)
        self.spec_vis.set_measurement_mode(2)
        self.spec_ir.set_measurement_mode(2)

    def get(self):
        results_vis = self.spec_vis.get_calibrated_values()
        results_ir = self.spec_ir.get_calibrated_values()
        self.R = [r for r in results_vis+results_ir]
        return self.R

    def close(self):
        self.spec_vis.set_measurement_mode(3)
        self.spec_ir.set_measurement_mode(3)

    def show(self):
        print(self.R)
