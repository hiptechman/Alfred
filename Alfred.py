import speech_recognition as sr
import re
from gtts import gTTS
from subprocess import call
from alfredCalendar import Calendar
from alfredWolframAlpha import WolframAlpha
import datetime
import string

class Alfred(object):
    """Personal voice assistant"""
    def __init__(self):
        # Create Google Calendar API and Wolfram Alpha API instances.
        self.calendar = Calendar()
        self.wa = WolframAlpha()
    
    def pronounce(self,text):
        # Voice to pronounce anything.
        tts = gTTS(text) # Send text to Google's servers
        tts.save('speak.mp3') # Save as audio file.
        return call(['mpg123', 'speak.mp3']) # Play audio file using subprocess

    def mic(self): # Adapted from module's site http://goo.gl/NaEhB5
        """Records voice input from user"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print "Recording..."
            audio = r.listen(source)
            print 'done'
            text = r.recognize(audio)
            print 'You said: %s' % str(text)
        return str(text)

    def whatDoYouWant(self):
        """Takes user's request"""
        self.pronounce('What would you like me to do?')
        request = self.mic()
        # Use regular expressions to designate which app handles request.
        if re.match(r'I need homework help', request, re.IGNORECASE) != None:
            self.wolframAlpha()
        elif re.search(r'Remove', request, re.IGNORECASE) != None:
            remove()
        elif re.match(r'Do i have time to', request, re.IGNORECASE) != None:
            self.checkAvailablity(request[17:]) # Remove anything not containing the task (17 characters before actual task).
        elif re.match(r'Move', request, re.IGNORECASE) != None:
            self.moveFile()
            
    def wolframAlpha(self):
        """Sends requests to WolframAlpha"""
        self.pronounce('Sure, what would you like me to find out?')
        query = self.mic()
        print "You asked me %s" %query
        result = self.wa.wolframAlphaQuery(query) # Get result from WolframAlpha's servers
        self.pronounce(result)
        print "The anser is %s" %result
        self.pronounce('Is that all?')
        query = self.mic()
        if re.search(r'No', query, re.IGNORECASE):
            self.wolframAlpha()

    def extractTime(self,task):
        """Finds and converts time in task to useable format"""
        meridiem = 'None' # Used to determine a.m. or p.m. later on. 
        if "o'clock" in task:
            # Time should be within below index once we find where o'clock starts.
            endFindTime = task.find("o'clock")
            startFindTime = endFindTime-2
            # Find any numbers within indices to use as hour. 
            time = re.findall('\d+', task[startFindTime:endFindTime])[0]
        else:
            try: 
                timeIndex = task.find(':')
                try:
                    # Extract numeric time if time in hh:mm format.
                    # Numberic offsets are for locating time to the left and right of the colon. 
                    if type(int(task[timeIndex-2])== int):
                        time = task[timeIndex-2:timeIndex] + ':' + task[timeIndex+1:timeIndex+3]
                except:
                    # If time is in h:mm format, convert to hh:mm format. 
                    time = '0' + task[timeIndex-1] + ':' + task[timeIndex+1:timeIndex+3]
            except:
                # If no time was given, request it and start over.
                self.pronounce('What time?')
                time = self.mic()
                time = self.extractTime(task)
        if 'a.m.' in task:
            meridiem = 'a.m.'
        elif 'p.m.' in task:
            meridiem = 'p.m.'
        else:
            # Ask whether time is a.m. or p.m. 
            while re.search(r'No', meridiem, re.IGNORECASE) == None:
                self.pronounce('In the morning?')
                meridiem = self.mic()
            if re.search(r'No', meridiem, re.IGNORECASE) != None:
                meridiem = 'p.m.'
            else:
                meridiem = 'a.m.'
        # 
        if len(time) == 1:
            time = '0' + str(time)
        if meridiem == 'p.m.':
            print time
            if len(time) < 4:
                time = str(int(time[:2]) + 12) + time[3:]
            else: 
                if time[1] != ':':
                    time = str(int(time[0:2]) + 12) + ':' + time[3:]
                else: 
                    time = str(int(time[0]) + 12) + ':' + time[2:]
        return time
    
    def convertTomorrow(self):
        # Credit to @voyager from stackoverflow for solution to find tomorrow's date 
        month = str(datetime.datetime.now() + datetime.timedelta(days = 1))[5:7]
        day = str(datetime.datetime.now() + datetime.timedelta(days = 1))[8:10]
        year = str(datetime.datetime.now() + datetime.timedelta(days = 1))[:4]
        return (month, day, year)

    def checkAvailablity(self, task):
        """Checks whether you have time to complete a certain task"""
        monthsToNumbers = {'january': '01', 'february': '02', 'march':'03', 'april': '04', 'may': '05', 'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12'}
        # Convert 'tomorrow' to correct date format.
        if 'tomorrow' in task:
            (month, day, year) = self.convertTomorrow()
            date = '%s-%s-%s' % (year, month, day)
        else:
            listDate = task.split()
            for word in listDate:
                for dictMonth in monthsToNumbers.keys():
                    if word == dictMonth:
                        month = monthsToNumbers[dictMonth]
                dayIndex = task.find('st')
                if dayIndex == -1:
                    dayIndex = task.find('th')
            if task[dayIndex-2].isspace() != True:
                day = task[dayIndex-2:dayIndex]
            else:
                day = '0' + task[dayIndex-1]
            yearIndex = task.find('20')
            year = task[yearIndex:yearIndex+4]
            date = '%s-%s-%s' % (year, month, day)
        startTime = self.extractTime(task)
        self.pronounce('When will this event end?')
        response = self.mic()
        endTime = self.extractTime(response)
        events = self.calendar.getEvents()
        for event in events:
            try:
                (scheduledEventDate, scheduledEventStartTime, scheduledEventEndTime) = self.calendar.getEventTime(event)
            except:
                continue
            if date == scheduledEventDate:
                if startTime <= scheduledEventEndTime:
                    if endTime > scheduledEventStartTime:
                        self.pronounce('Unfortunately you have a conflicting event')
            else:
                self.pronounce('You have no conflicting events at that time. Would you like to add an event?')
                response = self.mic()
                response = response.lower()
                if re.match(r'yes', response, re.IGNORECASE) != None:
                    self.pronounce('How long will this event last?')
                    timeLimit = self.mic()
                    task += ' for '
                    task += timeLimit
                    self.calendar.addEvent(task)
                    self.pronounce('Event created successfully!')
                    break

    def removeEvent(self, event):
        eventID = self.calendar.retrieveEventId(event)
        try:
            self.calendar.removeEvent(eventID)
            self.pronounce('Event removed successfully.')
        except:
            self.pronounce('No matching event found.')

    def moveFile(self, file, destination):
        call(['cp', 'file', 'destination'])

    def copyFile(self, file, destination):
        call(['mv', 'file', 'destination'])
Alfred().whatDoYouWant()