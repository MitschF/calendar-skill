import os
from dotenv import load_dotenv
from mycroft import MycroftSkill, intent_file_handler
import caldav
from datetime import date, datetime
from icalendar import Calendar as iCal



class Calendar(MycroftSkill):
    def __init__(self):
      MycroftSkill.__init__(self)

    def initialize(self):
      # get USERNAME and PASSWORD from .env
      load_dotenv()
      self.USERNAME = os.getenv("USERNAME")
      self.PASSWORD = os.getenv("PASSWORD")
      self.URL = os.getenv("URL")
      # open connection to calendar
      self.client = caldav.DAVClient(url=self.URL, username=self.USERNAME, password=self.PASSWORD)
      self.principal = self.client.principal()
      self.calendars = self.principal.calendars()
      self.cal = self.calendars[0]
      self.log.info("USING CALENDAR: " + str(self.cal))

    @intent_file_handler('getAppointment.intent')
    def get_next_appointment(self, message):
      next_events = self.cal.date_search(
          start=datetime.now()
      )
      if len(next_events) != 0:
        next_event = next_events[0]
        result = iCal.from_ical(next_event.data)
        for component in result.walk():
          if component.name == "VEVENT":
            result.summary = component.get('summary')
        self.speak("Next appointment: " + result.summary)
        # TODO: Uhrzeit / Datum ausgeben
      else: 
        self.speak("You have nothing to do.")
      
    # TODO: setAppointment
        


def create_skill():
    return Calendar()

