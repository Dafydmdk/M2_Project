import sys
import logging
import os
import time


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
                     self.sys_path + 'bone_capemgr.9/slots')
            time.sleep(1)
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

    @property
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

    @property
    def value(self):
        try:
            with open(self.path + 'direction', 'w') as f:
                f.write('0')
            with open(self.path + 'value') as f:
                return f.read()
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)

    @value.setter
    def value(self, value):
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
        self.value = '1'

    def off(self):
        self.value = '0'
