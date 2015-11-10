import httplib2
import sys
import os
import oauth2client
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from oauth2client import client
from httplib2 import Http
from oauth2client import tools
import re

class Calendar(object): # I combined two versions of authentication from Google into one .
    def __init__(self):
        self.credentials = self.get_credentials()
        credentials = self.credentials
        if credentials is None or credentials.invalid:
            credentials = run(flow, storage)
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.service = build('calendar', 'v3', http=http)

    def get_credentials(self):
    # Obtains locally stored credentials. Obtains from web, if not locally stored. Slightly modified, but mostly Google's code
        try:
            import argparse
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        except ImportError:
            flags = None
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Calendar API'
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-api-quickstart.json')
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatability with Python 2.6
                credentials = tools.run(flow, store)
            print 'Storing credentials to ' + credential_path
        return credentials

    def addEvent(self, text):
        service = self.service
        event = service.events().quickAdd(calendarId='primary', text= 'text').execute()
    
    def getEvents(self):
        events = []
        rawEvents = self.service.events().list(calendarId = 'primary').execute()
        return rawEvents['items']

    def getEventTime(self, event):
        try:
            eventStartTime = event['start']['dateTime']
            eventEndTime = event['end']['dateTime']
            timeIndex = eventStartTime.find('T') + 1
            eventStartTime = str(eventStartTime[timeIndex:timeIndex+5])
            eventEndTime = str(eventEndTime[timeIndex:timeIndex+5])
            eventDate = str(event['start']['dateTime'][:10])
            return (eventDate, eventStartTime, eventEndTime)
        except:
            eventDate = str(event['start']['date'])
            return eventDate
    
    def retrieveEventId(self,task):
        for event in self.getEvents():
            print event
            matches = 0.0
            total = len(event)
            eventSummary = str(event['summary'])
            for word in task:
                print type(eventSummary)
                if re.search(r'%s' % word, eventSummary, re.IGNORECASE) != None:
                    matches += 1
            if matches/total > 0.5:
                eventID = event['id']
        return str(eventID)

    def removeEvent(self, event):
        self.service.events().delete(calendarId = 'primary', eventId = '%s' % retrieveEventId(event)).execute()

    def addEvent(self,event):
        self.service.events().quickAdd(calendarId = 'primary', text = event).execute()

# print Calendar().retrieveEventId('Call fake girlfriend')