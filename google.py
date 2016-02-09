"""
This module handle the Google API, to get Google Calendar events.
"""

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

    """
    This class handle a personalized time, for some syntax sugar later.
    """

    def __init__(self, time):

        """
        Class constructor
        :param time: Python's time which initialize this class.
        """

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

        """
        Getter property for the __hour variable.
        :return: __hour variable.
        """

        return self.__hour

    @hour.setter
    def hour(self, hour):

        """
        Setter property for the __hour variable
        :param boolean: New __hour value
        """

        self.__hour = hour

    @property
    def min(self):

        """
        Getter property for the __min variable.
        :return: __min variable.
        """

        return self.__min

    @min.setter
    def min(self, min):

        """
        Setter property for the __min variable
        :param boolean: New __min value
        """

        self.__min = min

    @property
    def sec(self):

        """
        Getter property for the __sec variable.
        :return: __sec variable.
        """

        return self.__sec

    @sec.setter
    def sec(self, sec):

        """
        Setter property for the __sec variable
        :param boolean: New __sec value
        """

        self.__sec = sec

    def to_float_hour(self):

        """
        Calcul the float hour: ex : 12H30 => 12.5
        :return: The float hour
        """

        float_min = float(self.min) / 60.0
        return float(self.hour) + float_min


class GoogleEvent:

    """
    This class construct a new google event, easier to use.
    """

    def __init__(self, event):

        """
        Class constructor, constructed with the begin and the end hour of the Google event.
        :param event: The bare google event.
        """

        if event:
            self.__temp = event['summary']
            self.__begin = self.parse_time(event['start']['dateTime'])
            self.__end = self.parse_time(event['end']['dateTime'])
        else:
            logging.warning('No event')
            self.__temp = '16'
            self.__begin = MyTime('00:00:00')
            self.__end = MyTime('23:59:59')

    def parse_time(self, time):

        """
        Parse the JSON date format, and return a MyTime object constructed with the hour and the minute.
        :param time: JSON time
        :return: a MyTime constructed with the current hour.
        """

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

        """
        Getter property for the __temp variable.
        :return: __temp variable.
        """

        return self.__temp

    @property
    def begin(self):

        """
        Getter property for the __begin variable.
        :return: __begin variable.
        """

        return self.__begin

    @property
    def end(self):

        """
        Getter property for the __end variable.
        :return: __end variable.
        """

        return self.__end


class GoogleAgendaApi:

    """
    This class encapsulate the Google Agenda Api, to make it more simple.
    """

    def __init__(self, cred_file):

        """
        Constructor
        :param cred_file: The JSON credit file to connect on GAAPI
        """

        self.cred = self.get_cred(cred_file)
        self.service = self.get_service()

    def get_cred(self, cred_file):

        """
        Get the authorized credential
        :param cred_file: The JSON credit file to connect on GAAPI
        :return: The authorized credential
        """

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

        """
        Get the GAAPI service.
        :return: The GAAPI service.
        """

        http = httplib2.Http()
        http = self.cred.authorize(http)
        service = apiclient.discovery.build("calendar", "v3", http=http)
        return service

    def get_events(self):

        """
        Return the Agenda event list for the current day.
        :return: The Agenda event list for the current day.
        """

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

        """
        Send the event information to InfluxDB.
        :param events: The day events.
        """

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

        """
        Create a list with all the events.
        :return: A list with all the events.
        """

        events = list(GoogleEvent(el) for el in self.get_events())
        self.send_events_to_influxdb(events)
        return events
