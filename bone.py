"""
This module handle the IOs with the BeagleBone.
It provides methods to access and configure easily the gpios, the leds and the ain.
"""

import sys
import logging
import os
import time


class Ain:

    """
    Ain class, which configure the AIN and provide methods to access it.
    """

    def __init__(self, number, test=False):

        """
        Ain class' constructor.
        :param number: What for the BeagleBone's AIN number.
        :param test: If true, change the gpios' path to allow a test on something else than a BeagleBone.
        """

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

        """
        Internal function which find a pattern given in parameter in the folder list of the parameter where.
        :param where: Root folder, where the research begin
        :param pattern: Wanted name pattern.
        :return: Name of the found folder, or exit the program if not found.
        """

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

        """
        Property to get the value giver by the AIN.
        :return: String version of the value.
        """

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

    """
    Gpio class, which configure the GPIOs and provide methods to access it.
    """

    def __init__(self, gpio, test=False):

        """
        Gpio class' constructor.
        :param gpio: What for the BeagleBone's GPIO number.
        :param test: If true, change the gpios' path to allow a test on something else than a BeagleBone.
        """

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
            logging.warning('GPIO already exported')
        print('GPIO opened: ' + self.path)

    @property
    def value(self):

        """
        Property to get the value giver by the Gpio.
        :return: String version of the value.
        """

        try:
            with open(self.path + 'direction', 'w') as f:
                f.write('in')
            with open(self.path + 'value') as f:
                return f.read()
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)

    @value.setter
    def value(self, value):

        """
        Property to set a new value to Gpio.
        """

        try:
            with open(self.path + 'direction', 'w') as f:
                f.write('out')
            with open(self.path + 'value', 'w') as f:
                f.write(value)
        except IOError:
            logging.critical('Unable to open the gpio path')
            sys.exit(1)


class Led(Gpio):

    """
    Led class, which configure the GPIOs and provide methods to access it.
    Inherit from Gpio
    """

    def __init__(self, gpio, test=False):

        """
        Led class' constructor.
        :param gpio: What for the BeagleBone's GPIO number.
        :param test: If true, change the gpios' path to allow a test on something else than a BeagleBone.
        """

        super().__init__(gpio, test)

    def on(self):

        """
        Put the led on.
        """

        self.value = '1'

    def off(self):

        """
        Put the led off.
        """

        self.value = '0'
