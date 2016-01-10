import os
import shutil
import unittest

import simulation


class TestAin(unittest.TestCase):
    def test_pattern_ocp(self):
        print('Test - ocp.x detection', end='')
        ain = simulation.Ain('5', True)
        if not os.path.exists('./ocp.3'):
            os.makedirs('./ocp.3')
        match_folder = ain.find_pattern('./', 'ocp')
        self.assertEqual(match_folder, 'ocp.3')
        print(' - OK')
        shutil.rmtree('./ocp.3', ignore_errors=True)

    def test_pattern_helper(self):
        print('Test - helper.xy detection', end='')
        ain = simulation.Ain('5', True)
        if not os.path.exists('./helper.13'):
            os.makedirs('./helper.13')
        match_folder = ain.find_pattern('./', 'helper')
        self.assertEqual(match_folder, 'helper.13')
        print(' - OK')
        shutil.rmtree('./helper.13', ignore_errors=True)

    def test_value(self):
        print('Test - value get', end='')
        ain = simulation.Ain('5', True)
        if not os.path.exists('./ocp.3/helper.13'):
            os.makedirs('./ocp.3/helper.13')
        with open('./ocp.3/helper.13/AIN5', 'w') as f:
            f.write('42')
        value = ain.value
        self.assertEqual(value, '42')
        print(' - OK')
        shutil.rmtree('./ocp.3/helper.13', ignore_errors=True)
        os.rmdir('./ocp.3')


class TestGpio(unittest.TestCase):
    def test_init_del(self):
        print('Test - Gpio class init and del', end='')
        if not os.path.exists('./gpio'):
            os.makedirs('./gpio')
        gpio = simulation.Gpio('gpio60', True)
        with open('./gpio/export') as f:
            value = f.read()
            self.assertEqual(value, '60')
        shutil.rmtree('./gpio', ignore_errors=True)
        print(' - OK')

    def test_value_read(self):
        print('Test - Gpio class value read', end='')
        if not os.path.exists('./gpio/gpio60'):
            os.makedirs('./gpio/gpio60')
        with open('./gpio/gpio60/value', 'w') as f:
            f.write('42')
        gpio = simulation.Gpio('gpio60', True)
        value = gpio.value
        self.assertEqual(value, '42')
        with open('./gpio/gpio60/direction') as f:
            value = f.read()
            self.assertEqual(value, '0')
        shutil.rmtree('./gpio', ignore_errors=True)
        print(' - OK')

    def test_value_write(self):
        print('Test - Gpio class value write', end='')
        if not os.path.exists('./gpio/gpio60'):
            os.makedirs('./gpio/gpio60')
        gpio = simulation.Gpio('gpio60', True)
        gpio.value = '42'
        with open('./gpio/gpio60/value') as f:
            value = f.read()
            self.assertEqual(value, '42')
        with open('./gpio/gpio60/direction') as f:
            value = f.read()
            self.assertEqual(value, '1')
        shutil.rmtree('./gpio', ignore_errors=True)
        print(' - OK')


class TestLed(unittest.TestCase):
    def test_on(self):
        print('Test - Led on', end='')
        if not os.path.exists('./gpio/gpio60'):
            os.makedirs('./gpio/gpio60')
        led = simulation.Led('gpio60', True)
        led.on()
        with open('./gpio/gpio60/value') as f:
            value = f.read()
            self.assertEqual(value, '1')
        shutil.rmtree('./gpio', ignore_errors=True)
        print(' - OK')

    def test_off(self):
        print('Test - Led off', end='')
        if not os.path.exists('./gpio/gpio60'):
            os.makedirs('./gpio/gpio60')
        led = simulation.Led('gpio60', True)
        led.off()
        with open('./gpio/gpio60/value') as f:
            value = f.read()
            self.assertEqual(value, '0')
        shutil.rmtree('./gpio', ignore_errors=True)
        print(' - OK')


class TestSimulation(unittest.TestCase):
    def test_temperature(self):
        print('Test - Simulation temperature', end='')
        if not os.path.exists('./ocp.3/helper.13'):
            os.makedirs('./ocp.3/helper.13')
        if not os.path.exists('./gpio/gpio07'):
            os.makedirs('./gpio/gpio07')
        if not os.path.exists('./gpio/gpio50'):
            os.makedirs('./gpio/gpio50')
        if not os.path.exists('./gpio/gpio51'):
            os.makedirs('./gpio/gpio51')
        sim = simulation.Simulation(True)
        with open('./ocp.3/helper.13/AIN5', 'w') as f:
            f.write('0')
        value = sim.temp_int
        self.assertEqual(value, 10.0)
        with open('./ocp.3/helper.13/AIN5', 'w') as f:
            f.write('1800')
        value = sim.temp_int
        self.assertEqual(value, 25.0)
        print(' - OK')
        shutil.rmtree('./ocp.3/helper.13', ignore_errors=True)
        shutil.rmtree('./gpio', ignore_errors=True)
        os.rmdir('./ocp.3')


class TestGoogleEvent(unittest.TestCase):
    def test_class(self):
        print('Test - Google Event class creation', end='')
        ev = {'organizer': {'displayName': 'Thermostat', 'email':\
              'qi81udh8n9num6oquladg0go0g@group.calendar.google.com', 'self\
              ': True}, 'start': {'dateTime': '2016-01-09T10:30:00Z'}, 'cre\
              ated': '2016-01-09T22:15:50.000Z', 'sequence': 0, 'end': {'da\
              teTime': '2016-01-09T11:30:00Z'}, 'summary': '18', 'reminders\
              ': {'useDefault': True}, 'creator': {'displayName': 'Kévin Dl\
              le', 'email': 'kevin.dubrulle@gmail.com'}, 'id': '8mo045m0nrq\
              ev091i26u8vkq04', 'updated': '2016-01-09T22:15:50.663Z', 'eta\
              g': '""2904755501326000""', 'iCalUID': '8mo045m0nrqev091i26u8vk\
              q04@google.com', 'htmlLink': 'https://calendar.google.com/cal\
              endar/event?eid=OG1vMDQ1bTBucnFldjA5MWkyNnU4dmtxMDQgcWk4MXVka\
              DhuOW51bTZvcXVsYWRnMGdvMGdAZw', 'status': 'confirmed', 'kind'
              : 'calendar#event'}
        event = simulation.GoogleEvent(ev)
        self.assertIsNotNone(event)
        print(' - OK')


class TestGoogleAgandaApi(unittest.TestCase):
    def test_get_cred(self):
        print('Test - Google Agenda credentials', end='')
        gaapi = simulation.GoogleAgendaApi('./client_id.json')
        self.assertIsNotNone(gaapi)
        print(' - OK')

    def test_get_events(self):
        print('Test - Google Agenda events - PLEASE CREATE ONE BEFORE', end='')
        gaapi = simulation.GoogleAgendaApi('./client_id.json')
        self.assertIsNotNone(gaapi.get_events())
        print(' - OK')


if __name__ == '__main__':
    unittest.main()
