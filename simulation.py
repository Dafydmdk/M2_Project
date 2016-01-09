import os
import logging
import sys


class Ain:
    def __init__(self, number, test=False):
        self.number = number
        if test:
            self.sys_path = './'
            self.ocp = 'ocp.3'
            self.helper = 'helper.13'
        else:
            self.sys_path = '/sys/devices/'
            os.popen('echo cape-bone-iio > ' +
                     self.sys_path + 'bone_capemgr.*/slots')
            self.ocp = self.find_pattern(self.sys_path, 'ocp')
            self.helper = self.find_pattern(self.sys_path + self.ocp,
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
            with open(self.sys_path +
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
    def __init__(self, gpio, test=False):
        self.gpio = gpio
        self.test = test
        if self.test:
            self.sys_path = './'
        else:
            self.sys_path = '/sys/class/'
        self.path = self.sys_path + 'gpio/' + self.gpio + '/'
        try:
            with open(self.sys_path + 'gpio/export', 'w') as f:
                f.write(self.gpio[4:])
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)

    def __del__(self):
        if not self.test:
            try:
                with open(self.sys_path + 'gpio/unexport', 'w') as f:
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
    def __init__(self, gpio, test=False):
        super().__init__(gpio, test)

    def on(self):
        self.set_value('1')

    def off(self):
        self.set_value('0')


class GoogleAgendaApi:
    def __init__(self):
        pass


class Simulation:
    def __init__(self, test=False):
        self.led_r = Led('gpio07', test)  # maybe wrong
        self.led_g = Led('gpio50', test)
        self.led_b = Led('gpio51', test)
        self.pot = Ain('5', test)
        self.__heat = False
        self.__clim = False

    def temp_int(self):
        return (float(self.pot.value()) * 15.0 / 1800.0) + 10.0

    @property
    def heat(self):
        return self.__heat

    @heat.setter
    def heat(self, boolean):
        self.__heat = boolean
        self.on_state_changed()

    @property
    def clim(self):
        return self.__clim

    @clim.setter
    def clim(self, boolean):
        self.__clim = boolean
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
