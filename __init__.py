from mycroft import MycroftSkill, intent_file_handler, intent_handler
import caldav
from datetime import date, datetime
from icalendar import Calendar as iCal

class Calendar(MycroftSkill):
    def __init__(self):
      MycroftSkill.__init__(self)

    def initialize(self):
      # get USERNAME and PASSWORD from mycroft skill-settings 
      # https://account.mycroft.ai/skills
      USERNAME = self.settings.get('username')
      PASSWORD = self.settings.get('password')
      URL = self.settings.get('url')

      self.register_entity_file('number.entity')

      # open connection to calendar
      self.client = caldav.DAVClient(url=URL, username=USERNAME, password=PASSWORD)
      self.principal = self.client.principal()
      self.calendars = self.principal.calendars()
      self.cal = self.calendars[0]
      self.log.info("USING CALENDAR: " + str(self.cal))

    def output_event(self, event):
      if event.dtstart.value.strftime("%H:%M") == "00:00":
        # This is an "allday" event
        event_date = event.dtstart.value.strftime("%d. of %B, %Y")
        return("{event_summary} on {event_date}"
        .format(event_date=event_date, event_summary=event.summary.value,))
      else:
        # This is a "normal" event
        event_time = event.dtstart.value.strftime("%H:%M")
        event_date = event.dtstart.value.strftime("%d. of %B, %Y")
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
        
    @intent_handler('delete.event.intent')
    def delete_event(self, message):
      name = message.data.get('name')
      if name:
        events = self.cal.date_search(datetime.now())
        event_list = {
          "data": [],
          "names": []
        }
        if len(events) != 0:
          for event in events:
            e = event.instance.vevent
            if name.lower() in e.summary.value.lower():
              event_list["data"].append(event)
              event_list["names"].append(e.summary.value)
        
        if len(event_list["names"]) == 1:
          confirm_delete = self.ask_yesno('do.you.want.to.delete', {'event_name': event_list["names"][0]})
          if confirm_delete == 'yes':
            event_list["data"][0].delete()
            self.speak('Event {name} deleted.'.format(name=event_list["names"][0]))
          else:
            self.speak('Okay, I won\'t touch a thing')
        else:
          self.speak('You have {length} events containing "{name}".'.format(name=name, length=len(event_list["names"])))
          selection = self.ask_selection(event_list["names"], 'Which one do you want do delete?')
          index = event_list["names"].index(selection)

          confirm_delete = self.ask_yesno('do.you.want.to.delete', {'event_name': event_list["names"][index]})
          if confirm_delete == 'yes':
            event_list["data"][index].delete()
            self.speak('Event {name} deleted.'.format(name=event_list["names"][index]))
          else:
            self.speak('Okay, I won\'t touch a thing')
                  


def create_skill():
    return Calendar()

