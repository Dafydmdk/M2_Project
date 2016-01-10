from IO import *
from Google import *
import datetime
import time
from influxdb import InfluxDBClient


class Simulation:
    def __init__(self, test=False):
        self.led_r = Led('gpio07', test)  # maybe wrong
        self.led_g = Led('gpio50', test)
        self.led_b = Led('gpio51', test)
        self.pot = Ain('5', test)
        self.__heat = False
        self.__clim = False
        self.gaapi = GoogleAgendaApi('./client_id.json')

    @property
    def temp_int(self):
        return (float(self.pot.value) * 15.0 / 1800.0) + 10.0

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

    def run(self):
        event_list = self.gaapi.create_google_event_list()
        now = datetime.datetime.now()
        hour = now.strftime('%H')
        min = now.strftime('%M')
        float_curent_hour = float(hour) + float(min)/60.0
        for event in event_list:
            if event.begin.to_float_hour() <= float_curent_hour:
                if event.end.to_float_hour() >= float_curent_hour:
                    if float(event.temp) - self.temp_int >= 0.5:
                        self.heat = True
                    elif float(event.temp) - self.temp_int <= -0.5:
                        self.clim = True
                    else:
                        self.clim = False
                        self.heat = False

    def send_to_influxdb(self):
        client = InfluxDBClient('5.196.8.140',
                                8086,
                                'ISEN',
                                'ISEN29',
                                'thermostat')
        json_body = [
            {
                "measurement": "temp_interieure",
                "tags": {
                    "binome": "Dubrulle_Paillot"
                },
                "fields": {
                    "value": self.temp_int
                }
            }
        ]
        client.write_points(json_body)
        json_body = [
            {
                "measurement": "climatisation",
                "tags": {
                    "binome": "Dubrulle_Paillot"
                },
                "fields": {
                    "value": 1 if self.clim else 0
                }
            }
        ]
        client.write_points(json_body)
        json_body = [
            {
                "measurement": "chauffage",
                "tags": {
                    "binome": "Dubrulle_Paillot"
                },
                "fields": {
                    "value": 1 if self.heat else 0
                }
            }
        ]
        client.write_points(json_body)

    def main_loop(self):
        while True:
            self.run()
            time.sleep(60)


if __name__ == '__main__':
    sim = Simulation()
    sim.main_loop()
