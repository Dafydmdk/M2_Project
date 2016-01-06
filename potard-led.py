import os
import logging
import re
import sys


class Ain:
    def __init__(self, number):
        self.number =  number
        os.popen('echo cape-bone-iio > /sys/devices/bone_capemgr.*/slots')

        self.ocp = self.find_pattern('/sys/devices', 'ocp.[0-9]')
        self.helper = self.find_pattern('/sys/devices/' + self.ocp,
                                        'helper.[0-9]+')

    def find_pattern(self, where, pattern):
        dirs = os.listdir(where)
        if dirs:
            for el in dirs:
                matchs = re.findall(pattern, el)
                if matchs:
                    return matchs[0]
                else:
                    logging.critical('Unable to find '+ where)
                    sys.exit(1)
        else:
            logging.critical('Unable to find ' + where)
            sys.exit(1)

    def value(self):
        with open('/sys/devices/' + self.ocp + '/' + self.helper + '/AIN' +
                          self.number) as f:
            return f.read()


class Gpio:
    def __init__(self, gpio):
        self.gpio = gpio
        self.path = '/sys/class/gpio/' + self.gpio + '/'
        with open('/sys/class/gpio/export', 'w') as f:
            f.write(self.gpio[4:])

    def __del__(self):
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write(self.gpio[4:])

    def value(self):
        with open(self.path + 'direction', 'w') as f:
            f.write('0')
        with open(self.path + 'value') as f:
            return f.read()

    def set_value(self, value):
        with open(self.path + 'direction', 'w') as f:
            f.write('1')
        with open(self.path + 'value', 'w') as f:
            f.write(value)


if __name__ == '__main__':
    led_r = Gpio('gpio07')
    led_g = Gpio('gpio50')
    led_b = Gpio('gpio51')
    pot = Ain('5')
