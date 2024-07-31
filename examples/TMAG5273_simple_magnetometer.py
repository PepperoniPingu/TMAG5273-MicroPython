from XRPLib.defaults import *
import time

from TMAG5273 import HallSensor

hall_sensor = HallSensor.get_default_tmag()

# Polling data from the IMU
def tmag_test():
    while True:
        hall_x = hall_sensor.get_mag_x()
        hall_y = hall_sensor.get_mag_y()
        hall_z = hall_sensor.get_mag_z()
        
        print(f"X: {hall_x:>8.3f} mT  Y: {hall_y:>8.3f} mT  Z: {hall_z:>8.3f} mT")

        time.sleep(0.1)

tmag_test()