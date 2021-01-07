import os
from dotenv import load_dotenv
from mycroft import MycroftSkill, intent_file_handler
import caldav
from icalendar import Calendar, Event

from pathlib import Path


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
      # self.url = "https://" + self.USERNAME + ":" + self.PASSWORD + "@next.social-robot.info/nc/remote.php/dav"
      self.client = caldav.DAVClient(url=self.URL, username=self.USERNAME, password=self.PASSWORD)
      self.principal = self.client.principal()
      self.calendars = self.principal.calendars()
      self.calendar = self.calendars[0]
      self.log.info("USING CALENDAR: " + str(self.calendar))

    @intent_file_handler('getAppointment.intent')
    def get_next_appointment(self, message):
      events = self.calendar.events()
      if len(events) != 0:
        next_event = events[0]
      else: 
        self.speak("You have nothing to do.")
        


def create_skill():
    return Calendar()

