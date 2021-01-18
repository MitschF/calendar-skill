import os
from dotenv import load_dotenv
from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
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

      # placeholder for creating new events
      self.new_Event = {
        "description" : "placeholder description",
        "start" : datetime.now(),
        "allday" : True
        }

    @intent_file_handler("getAppointment.intent")
    def get_next_appointment(self, message):
      events = self.cal.date_search(datetime.now())

      if len(events) == 0:
        self.speak("You have nothing to do!")
      else:
        event_list = []

        for event in events:
          e = event.instance.vevent
          event_list.append(e)

        event_list.sort(key=lambda e: e.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
        next_event = event_list[0]
        if next_event.dtstart.value.strftime("%H:%M") == "00:00":
          # This is an "allday" event
          event_time = next_event.dtstart.value.strftime("%d.%m.%Y")
          self.speak("Next Appointment: {event_summary} on {event_time}".format(event_time=event_time, event_summary=next_event.summary.value,))
        else:
          # This is a "normal" event
          event_time = next_event.dtstart.value.strftime("%H:%M")
          event_date = next_event.dtstart.value.strftime("%d.%m.%Y")
          self.speak("Next Appointment: {event_summary} on {event_date} at {event_time}".format(event_time=event_time, event_date=event_date, event_summary=next_event.summary.value,))
      
          # TODO: überprüfen, ob Skill abschmiert wenn Event ohne Titel in Kalender eingetragen wird 


    @intent_file_handler("createAppointment.intent")
    def get_next_appointment(self, message):
      self.speak("Description?", expect_response=True)

    @intent_handler(IntentBuilder("createIntent").require("description"))
    def create_appointment(self, message):
      self.log.info(message.data.get('utterance'))
      self.new_Event[description] = message.data.get('utterance')
      self.speak("Staring time?", expect_response=True)

    @intent_handler(IntentBuilder("createIntent").require("start"))
    def create_appointment(self, message):
      self.log.info(message.data.get('utterance'))
      self.new_Event[start] = message.data.get('utterance')
      self.speak("Allday?", expect_response=True)

    @intent_handler(IntentBuilder("createIntent").require("allday"))
    def create_appointment(self, message):
      self.log.info(message.data.get('utterance'))
      self.new_Event[allday] = message.data.get('utterance')
      self.speak("done", new_Event)

        
def create_skill():
    return Calendar()

