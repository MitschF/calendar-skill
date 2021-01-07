import os
from dotenv import load_dotenv
from mycroft import MycroftSkill, intent_file_handler
import caldav

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

    @intent_file_handler('getAppointment.intent')
    def get_next_appointment(self, message):
      self.speak(str(self.principal.calendars()))
        


def create_skill():
    return Calendar()

