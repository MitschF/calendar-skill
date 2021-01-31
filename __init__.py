import os
from dotenv import load_dotenv
from mycroft import MycroftSkill, intent_file_handler, intent_handler, util
from adapt.intent import IntentBuilder
import caldav
from datetime import date, datetime, timedelta
from icalendar import Calendar as iCal
from icalendar import Event



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

    @intent_file_handler("get.appointment.intent")
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




    @intent_file_handler("get.appointments.from.time.period.intent")
    def get_appointment_from_time_period(self, message):
      # extract start time from input
      formatted_start_time = util.parse.extract_datetime(message.data.get("start_time"), anchorDate=datetime.now())
      self.log.info("formatted start time: ") 
      self.log.info(formatted_start_time) 

      # extract end time from input if present
      if message.data.get("end_time") != None:
        formatted_end_time = util.parse.extract_datetime(message.data.get("end_time"), anchorDate=datetime.now()) 
        # search for events in time period with specified end
        events = self.cal.date_search(formatted_start_time[0], formatted_end_time[0])
      else:
        # search for events in time period without specified end
        events = self.cal.date_search(formatted_start_time[0], formatted_start_time[0] + timedelta(days = 1))
        # TODO: Zeitspanne nimmt vorherigen Tag mit rein (z.B. March 3 liefert ganztägige events von 2. und 3. märz)

      if len(events) == 0:
        self.speak("You have nothing to do!")
      else:
        event_list = []

        for event in events:
          e = event.instance.vevent
          event_list.append(e)
          #self.log.info(event)

        event_list.sort(key=lambda e: e.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
        for next_event in event_list:
          if next_event.dtstart.value.strftime("%H:%M") == "00:00":
            # This is an "allday" event
            event_time = next_event.dtstart.value.strftime("%d.%m.%Y")
            self.speak("Next Appointment: {event_summary} on {event_time}".format(event_time=event_time, event_summary=next_event.summary.value,))
          else:
            # This is a "normal" event
            event_time = next_event.dtstart.value.strftime("%H:%M")
            event_date = next_event.dtstart.value.strftime("%d.%m.%Y")
            self.speak("Next Appointment: {event_summary} on {event_date} at {event_time}".format(event_time=event_time, event_date=event_date, event_summary=next_event.summary.value,))



    # TODO mehrtägige Events bis jetzt noch nicht unterstützt
    @intent_file_handler("create.appointment.intent")
    def create_appointment(self, message):
      description = formatted_start_date = formatted_start_time = formatted_end_time = None

      # extract description from input if present
      if message.data.get("description") != None:
        description = message.data.get("description")
        self.log.info("description: ")
        self.log.info(description)
      else:
        # cancel current event creating because of missing description
        self.speak("Creation canceled. No description for the new event was specified.")
        return

      # extract start date from input if present
      if message.data.get("start_date") != None:
        formatted_start_date = util.parse.extract_datetime(message.data.get("start_date"), anchorDate=datetime.now()) 
        self.log.info("formatted start date: ")
        self.log.info(formatted_start_date)
      else:
        # cancel current event creating because of missing start date
        self.speak("Creation canceled. No starting date for the new event was specified.")
        return

      # extract start time from input if present
      if message.data.get("start_time") != None:
        formatted_start_time = util.parse.extract_number(message.data.get("start_time")) 
        self.log.info("formatted start time: ")
        self.log.info(formatted_start_time)

      # extract end time from input if present
      if message.data.get("end_time") != None:
        formatted_end_time = util.parse.extract_number(message.data.get("end_time")) 
        self.log.info("formatted end time: ")
        self.log.info(formatted_end_time)


      # create new iCal event from input wildcards
      new_event = Event()
      new_event.add("summary", description)
      
      if formatted_start_time == None:
        # TODO: falls besonders fleißig: rausfinden, ob Zeitangabe direkt mit Uhrzeit gemacht wurde
              # z.b. march 1 2021 9am, wenn ja, dann nicht als ganztägig speichern
        # no start time specified, creating all-day event
        new_event.add("dtstart", formatted_start_date[0].date())
        new_event.add("dtend", formatted_start_date[0].date() + timedelta(days = 1))
      else:
        new_event.add("dtstart", formatted_start_date[0] + timedelta(hours = formatted_start_time))
        if formatted_end_time == None:
          # no end time specified, creating 1 hour event
          new_event.add("dtend", formatted_start_date[0] + timedelta(hours = formatted_start_time + 1))
        else:
          new_event.add("dtend", formatted_start_date[0] + timedelta(hours = formatted_end_time))
            

      # create wrapping iCal calendar object
      iCal_wrapper = iCal()
      iCal_wrapper.add_component(new_event)

      # save new event with caldav
      self.cal.save_event(iCal_wrapper)

      self.speak("New event created.")

        
def create_skill():
    return Calendar()

