import os
import logging
import sys


class Ain:
    def __init__(self, number, test=False):
        if not test:
            self.number =  number
            os.popen('echo cape-bone-iio > /sys/devices/bone_capemgr.*/slots')
            self.ocp = self.find_pattern('/sys/devices', 'ocp')
            self.helper = self.find_pattern('/sys/devices/' + self.ocp,
                                            'helper')

    def find_pattern(self, where, pattern):
        dirs = os.listdir(where)
        if dirs:
            matchs = list((ele for ele in dirs if not ele.find(pattern)))
            if matchs:
                return matchs[0]
            else:
                logging.critical('Unable to find pattern ' + pattern)
                sys.exit(1)
        else:
            logging.critical('Unable to find folder ' + where)
            sys.exit(1)

    def value(self):
        try:
            with open('/sys/devices/' +
                              self.ocp +
                              '/' +
                              self.helper +
                              '/AIN' +
                              self.number) as f:
                return f.read()
        except IOError:
            logging.critical('Unable to open the AIN path')
            sys.exit(1)


class Gpio:
    def __init__(self, gpio):
        self.gpio = gpio
        self.path = '/sys/class/gpio/' + self.gpio + '/'
        try:
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(self.gpio[4:])
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)

    def __del__(self):
        try:
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(self.gpio[4:])
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)

    def value(self):
        try:
            with open(self.path + 'direction', 'w') as f:
                f.write('0')
            with open(self.path + 'value') as f:
                return f.read()
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)

    def set_value(self, value):
        try:
            with open(self.path + 'direction', 'w') as f:
                f.write('1')
            with open(self.path + 'value', 'w') as f:
                f.write(value)
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)


class Led(Gpio):
    def __init__(self, gpio):
        super().__init__(gpio)

    def on(self):
        self.set_value('1')

    def off(self):
        self.set_value('0')


class Simulation:
    def __init__(self):
        self.led_r = Led('gpio07') # maybe wrong
        self.led_g = Led('gpio50')
        self.led_b = Led('gpio51')
        self.pot = Ain('5')
        self.heat = False
        self.clim = False

    def temperature(self):
        return ( float(self.pot.value()) * 15.0 / 1800.0 ) + 10.0

    @property
    def heat(self):
        return self.heat

    @heat.setter
    def heat(self, boolean):
        self.heat = boolean
        self.on_state_changed()

    @property
    def clim(self):
        return self.clim

    @clim.setter
    def clim(self, boolean):
        self.clim = boolean
        self.on_state_changed()

    def on_state_changed(self):
        if self.heat:
            self.led_r.on()
        else:
            self.led_r.off()

        if self.clim:
            self.led_b.on()
        else:
            self.led_b.off()

        if not self.heat and not self.clim:
            self.led_g.on()
        else:
            self.led_g.off()
