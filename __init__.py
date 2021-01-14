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
          event_date = next_event.dtstart.value.strftime("%d.%m.%Y")
          self.speak("Next Appointment: {event_summary} on {event_date}"
          .format(event_date=event_date, event_summary=next_event.summary.value,))
        else:
          # This is a "normal" event
          event_time = next_event.dtstart.value.strftime("%H:%M")
          event_date = next_event.dtstart.value.strftime("%d.%m.%Y")
          self.speak("Next Appointment: {event_summary} on {event_date} at {event_time}"
          .format(event_time=event_time, event_date=event_date, event_summary=next_event.summary.value,))
      
    # TODO: setAppointment
        
def create_skill():
    return Calendar()

