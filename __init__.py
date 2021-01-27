import os
from dotenv import load_dotenv
from mycroft import MycroftSkill, intent_file_handler, intent_handler
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

      self.register_entity_file('number.entity')

      # open connection to calendar
      self.client = caldav.DAVClient(url=self.URL, username=self.USERNAME, password=self.PASSWORD)
      self.principal = self.client.principal()
      self.calendars = self.principal.calendars()
      self.cal = self.calendars[0]
      self.log.info("USING CALENDAR: " + str(self.cal))

    def output_event(self, event):
      if event.dtstart.value.strftime("%H:%M") == "00:00":
        # This is an "allday" event
        event_date = event.dtstart.value.strftime("%d.%m.%Y")
        return("{event_summary} on {event_date}"
        .format(event_date=event_date, event_summary=event.summary.value,))
      else:
        # This is a "normal" event
        event_time = event.dtstart.value.strftime("%H:%M")
        event_date = event.dtstart.value.strftime("%d.%m.%Y")
        return("{event_summary} on {event_date} at {event_time}"
        .format(event_time=event_time, event_date=event_date, event_summary=event.summary.value,))

    @intent_file_handler('what.is.next.intent')
    def handle_what_is_next(self, message):
      events = self.cal.date_search(datetime.now())      
      if len(events) != 0:
        event_list = []
        for event in events:
          e = event.instance.vevent
          event_list.append(e)

        event_list.sort(key=lambda e: e.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
        next_event = event_list[0]
        self.speak("Your next appointment is: " + self.output_event(next_event))
      else:
        self.speak("You have nothing to do!")
      
    @intent_handler('what.are.next.intent')
    def handle_what_are_next(self, message):
      number_attr = message.data.get('number')
      number = 3 if number_attr is None else int(number_attr)

      events = self.cal.date_search(datetime.now())
      if len(events) != 0:
        event_list = []
        for event in events:
          e = event.instance.vevent
          event_list.append(e)

        event_list.sort(key=lambda e: e.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
        next_events = event_list[:number]
        self.speak("Your next " + str(len(next_events)) + " events are: ")
        for e in next_events:
          self.speak(self.output_event(e))
      else:
        self.speak("You have nothing to do!")
        
def create_skill():
    return Calendar()

