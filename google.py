import sys
import logging
import re
import datetime
import os
import httplib2
import oauth2client
import apiclient.discovery
import influx


class MyTime:
    def __init__(self, time):
        str_list = time.split(':')
        if len(str_list) == 3:
            self.__hour = str_list[0]
            self.__min = str_list[1]
            self.__sec = str_list[2]
        else:
            logging.error('Unable to create a MyTime')
            sys.exit(1)

    @property
    def hour(self):
        return self.__hour

    @hour.setter
    def hour(self, hour):
        self.__hour = hour

    @property
    def min(self):
        return self.__min

    @min.setter
    def min(self, min):
        self.__min = min

    @property
    def sec(self):
        return self.__sec

    @sec.setter
    def sec(self, sec):
        self.__sec = sec

    def to_float_hour(self):
        float_min = float(self.min) / 60.0
        return float(self.hour) + float_min


class GoogleEvent:
    def __init__(self, event):
        if event:
            self.__temp = event['summary']
            self.__begin = self.parse_time(event['start']['dateTime'])
            self.__end = self.parse_time(event['start']['dateTime'])
        else:
            logging.warning('No event')
            self.__temp = '16'
            self.__begin = MyTime('00:00:00')
            self.__end = MyTime('23:59:59')

    def parse_time(self, time):
        matchs = re.findall('T.+Z', time)
        if matchs:
            matchs[0] = matchs[0].replace('T', '')
            matchs[0] = matchs[0].replace('Z', '')
        else:
            logging.error('Bad time format')
            self.__temp = '16'
            self.__begin = MyTime('00:00:00')
            self.__end = MyTime('23:59:59')
        return MyTime(matchs[0])

    @property
    def temp(self):
        return self.__temp

    @property
    def begin(self):
        return self.__begin

    @property
    def end(self):
        return self.__end


class GoogleAgendaApi:
    def __init__(self, cred_file):
        self.cred = self.get_cred(cred_file)
        self.service = self.get_service()

    def get_cred(self, cred_file):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart.json')
        store = oauth2client.file.Storage(credential_path)
        cred = store.get()
        if not cred or cred.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(
                    cred_file,
                    'https://www.googleapis.com/auth/calendar')
            flow.user_agent = 'Thermostat'

        if not cred:
            logging.critical('Unable to get credentials')
            sys.exit(1)
        return cred

    def get_service(self):
        http = httplib2.Http()
        http = self.cred.authorize(http)
        service = apiclient.discovery.build("calendar", "v3", http=http)
        return service

    def get_events(self):
        now = datetime.date.today()
        events = self.service.events().list(
            calendarId='qi81udh8n9num6oquladg0go0g@group.calendar.google.com',
            singleEvents=True,
            maxResults=10,
            orderBy='startTime',
            timeMin=now.strftime('%Y-%m-%dT00:00:00+01:00'),
            timeMax=now.strftime('%Y-%m-%dT23:59:59+01:00'),
        ).execute()

        return events['items']

    def send_events_to_influxdb(self, events):
        binome = "Dubrulle_Paillot"
        for event in events:
            now = datetime.date.today()
            json_body = [
                {
                    "measurement": "consigne",
                    "tags": {
                        "binome": binome
                    },
                    "time": now.strftime('%Y-%m-%dT{h}:{m}.000000000Z'.format(
                        h=event.begin.hour,
                        m=event.begin.min
                    )),
                    "fields": {
                        "value": event.temp
                    }
                }
            ]
            influx.send_data(json_body)

    def create_google_event_list(self):
        events = list(GoogleEvent(el) for el in self.get_events())
        self.send_events_to_influxdb(events)
        return events
