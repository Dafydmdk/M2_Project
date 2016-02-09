"""
Simulation module, must be called as main.
"""

import datetime
import influx
import bone
import google


class Simulation:

    """
    Handle heating or air conditioning state change, regarding the
    inside temperature (potentiometer) and the command (Google Calendar)
    Change leds' state according to the heating or the air conditioning
    state.
    """

    def __init__(self, test=False):

        """
        Simulation class' constructor.
        :param test: If true, change the gpios' path to allow a test on
        something else than a BeagleBone
        """

        self.led_r = bone.Led('gpio07', test)  # maybe wrong
        self.led_g = bone.Led('gpio50', test)
        self.led_b = bone.Led('gpio51', test)
        self.pot = bone.Ain('5', test)
        self.__heat = False
        self.__clim = False
        self.gaapi = google.GoogleAgendaApi('./client_id.json')

    @property
    def temp_int(self):

        """
        Property to get the float version of the inside temperature, from the
        potentiometer. It is an affine function :
        potentiometer: 0 mV to 1800 mV
        return: 10.0°C to 25.0°C
        :return: The float version of the inside temperature.
        """

        return (float(self.pot.value) * 15.0 / 1800.0) + 10.0

    @property
    def heat(self):

        """
        Getter property for the __heat variable.
        :return: __heat variable.
        """

        return self.__heat

    @heat.setter
    def heat(self, boolean):

        """
        Setter property for the __heat variable
        :param boolean: New __heat state: True or False
        """

        self.__heat = boolean
        self.on_state_changed()

    @property
    def clim(self):

        """
        Getter property for the __clim variable.
        :return: __clim variable.
        """

        return self.__clim

    @clim.setter
    def clim(self, boolean):

        """
        Setter property for the __clim variable
        :param boolean: New __clim state: True or False
        """

        self.__clim = boolean
        self.on_state_changed()

    def on_state_changed(self):

        """
        Change the IOs' state according to the air conditioning or the heating
        state.
        Heat? Red led.
        Air conditioning? Blue led.
        No? Green led.
        """

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

    def run(self):

        """
        Start one simulation's cycle:
            Get the Google Calendar events' list.
            Get the current time.
            For each Google event, if the current hour is in the hour range of
            the event:
                If the difference between the command temperature and the
                inside temperature is more or equal than 0.5°C:
                    Put the heating on.
                Else if the difference between the command temperature and the
                inside temperature is less or equal than -0.5°C:
                    Put the air conditioning on.
                Else:
                    Put both off.
            Send the data to InfluxDB.
        """

        event_list = self.gaapi.create_google_event_list()
        now = datetime.datetime.now()
        hour = now.strftime('%H')
        minu = now.strftime('%M')
        float_current_hour = float(hour) + float(minu) / 60.0
        temp = 16.0
        for event in event_list:
            if event.begin.to_float_hour() <= float_current_hour:
                if event.end.to_float_hour() >= float_current_hour:
                    temp = float(event.temp)
        if temp - self.temp_int >= 0.5:
            self.__heat = True
        elif temp - self.temp_int <= -0.5:
            self.__clim = True
        else:
            self.__clim = False
            self.__heat = False
        self.send_to_influxdb()

    def send_to_influxdb(self):

        """
        Send the inside temperature, the air conditioning state and the heating
        state to InfluxDB.
        Obviously, no unittest for this method, because otherwise it would
        pollute the ISEN's InfluxDB, and it would be a shame...
        """

        binome = "Dubrulle_Paillot"

        json_body = [
            {
                "measurement": "temp_interieure",
                "tags": {
                    "binome": binome
                },
                "fields": {
                    "value": self.temp_int
                }
            }
        ]
        influx.send_data(json_body)

        json_body = [
            {
                "measurement": "climatisation",
                "tags": {
                    "binome": binome
                },
                "fields": {
                    "value": 1 if self.clim else 0
                }
            }
        ]
        influx.send_data(json_body)

        json_body = [
            {
                "measurement": "chauffage",
                "tags": {
                    "binome": binome
                },
                "fields": {
                    "value": 1 if self.heat else 0
                }
            }
        ]
        influx.send_data(json_body)


if __name__ == '__main__':
    Simulation().run()
