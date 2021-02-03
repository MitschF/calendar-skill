
from mycroft import MycroftSkill, intent_file_handler, intent_handler, util
import caldav
from datetime import date, datetime, timedelta
from icalendar import Calendar as iCal
from icalendar import Event


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
        self.client = caldav.DAVClient(
            url=URL, username=USERNAME, password=PASSWORD)
        self.principal = self.client.principal()
        self.calendars = self.principal.calendars()
        self.cal = self.calendars[0]
        self.log.info("USING CALENDAR: " + str(self.cal))

    def output_event(self, event):
        """
        Function that returns a formatted string

        Args:
            event (caldav.objects.Event): Calendar-Object
        Returns:
            string - String in the form of "{event_summary} on {event_date}" or 
            "{event_summary} on {event_date} at {event_time}", 
            depending on whether the event is all-day or not.
        """
        e = event.instance.vevent
        if e.dtstart.value.strftime("%H:%M") == "00:00":
            self.log.info(type(event))
            # This is an "allday" event
            event_date = e.dtstart.value.strftime("%d. of %B, %Y")
            return("{event_summary} on {event_date}"
                   .format(event_date=event_date, event_summary=e.summary.value, ))
        else:
            # This is a "normal" event
            event_time = e.dtstart.value.strftime("%H:%M")
            event_date = e.dtstart.value.strftime("%d. of %B, %Y")
            return("{event_summary} on {event_date} at {event_time}"
                   .format(event_time=event_time, event_date=event_date, event_summary=e.summary.value, ))

    @intent_file_handler('what.is.next.intent')
    def handle_what_is_next(self, message):
        events = self.cal.date_search(datetime.now())
        events.sort(
            key=lambda e: e.instance.vevent.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
        if len(events) == 0:
            self.speak("You have nothing to do!")
        else:
            next_event = events[0]
            self.speak("Your next appointment is: " +
                       self.output_event(next_event))

    @intent_handler('what.are.next.intent')
    def handle_what_are_next(self, message):
        number_attr = message.data.get('number')
        number = 3 if number_attr is None else int(number_attr)

        events = self.cal.date_search(datetime.now())
        if len(events) == 0:
            self.speak("You have nothing to do!")
        else:
            events.sort(
                key=lambda e: e.instance.vevent.dtstart.value.strftime("%Y-%m-%d, %H:%M"))

            next_events = events[:number]
            self.speak("Your next " + str(len(next_events)) + " events are: ")
            for e in next_events:
                self.speak(self.output_event(e))

    @intent_file_handler("get.appointments.from.time.period.intent")
    def get_appointment_from_time_period(self, message):
        # extract start time from input
        formatted_start_time = util.parse.extract_datetime(
            message.data.get("start_time"), anchorDate=datetime.now())

        # extract end time from input if present
        if message.data.get("end_time") != None:
            formatted_end_time = util.parse.extract_datetime(
                message.data.get("end_time"), anchorDate=datetime.now())
            # search for events in time period with specified end
            events = self.cal.date_search(
                formatted_start_time[0], formatted_end_time[0])
        else:
            # search for events in time period without specified end
            events = self.cal.date_search(
                formatted_start_time[0], formatted_start_time[0] + timedelta(days=1))

        if len(events) == 0:
            self.speak("You have nothing to do!")
        else:
            events.sort(
                key=lambda e: e.instance.vevent.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
            for next_event in events:
                self.speak(self.output_event(next_event))

    @intent_file_handler("create.appointment.intent")
    def create_appointment(self, message):
        description = formatted_start_date = formatted_start_time = formatted_end_time = None

        # extract description from input if present
        if message.data.get("description") != None:
            description = message.data.get("description")
        else:
            # cancel current event creating because of missing description
            self.speak(
                "Creation canceled. No description for the new event was specified.")
            return

        # extract start date from input if present
        if message.data.get("start_date") != None:
            formatted_start_date = util.parse.extract_datetime(
                message.data.get("start_date"), anchorDate=datetime.now())
        else:
            # cancel current event creating because of missing start date
            self.speak(
                "Creation canceled. No starting date for the new event was specified.")
            return

        # extract start time from input if present
        if message.data.get("start_time") != None:
            formatted_start_time = util.parse.extract_number(
                message.data.get("start_time"))

        # extract end time from input if present
        if message.data.get("end_time") != None:
            formatted_end_time = util.parse.extract_number(
                message.data.get("end_time"))

        # create new iCal event from input wildcards
        new_event = Event()
        new_event.add("summary", description)

        if formatted_start_time == None:
            # no start time specified, creating all-day event
            new_event.add("dtstart", formatted_start_date[0].date())
            new_event.add(
                "dtend", formatted_start_date[0].date() + timedelta(days=1))
        else:
            new_event.add(
                "dtstart", formatted_start_date[0] + timedelta(hours=formatted_start_time))
            if formatted_end_time == None:
                # no end time specified, creating 1 hour event
                new_event.add(
                    "dtend", formatted_start_date[0] + timedelta(hours=formatted_start_time + 1))
            else:
                new_event.add(
                    "dtend", formatted_start_date[0] + timedelta(hours=formatted_end_time))

        # create wrapping iCal calendar object
        iCal_wrapper = iCal()
        iCal_wrapper.add_component(new_event)

        # save new event with caldav
        self.cal.save_event(iCal_wrapper)

        self.speak("New event successfully created.")

    @intent_handler('delete.event.intent')
    def delete_event(self, message):
        name = message.data.get('name')
        if name:
            events = list(filter(
                lambda e: name.lower() in e.instance.vevent.summary.value.lower(), self.cal.date_search(datetime.now())))
            events.sort(
                key=lambda e: e.instance.vevent.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
            event_names = []
            if len(events) == 0:
                self.speak("You have nothing to do!")
            else:
                for event in events:
                    event_names.append(event.instance.vevent.summary.value)

                def confirm_delete(self, i):
                    """
                    Poses a "yes / no" question that the user must answer 
                    and deletes the event if the answer is yes

                    Args:
                        i (number): Index of events-List
                    """
                    confirm_delete = self.ask_yesno('do.you.want.to.delete', {
                                                    'event_name': event_names[i]})
                    if confirm_delete == 'yes':
                        events[i].delete()
                        self.speak('Event {name} deleted.'.format(
                            name=event_names[i]))
                    else:
                        self.speak('Okay, I won\'t touch a thing')

                if len(events) == 1:
                    confirm_delete(self, 0)
                elif len(events) > 1:
                    self.speak('You have {length} events containing "{name}".'.format(
                        name=name, length=len(events)))
                    selection = self.ask_selection(
                        event_names, 'Which one do you want do delete?')
                    index = event_names.index(selection)
                    confirm_delete(self, index)
                else:
                    self.speak('You have no events containing "{name}".'
                               .format(name=name))

    @intent_handler('rename.event.intent')
    def rename_event(self, message):
        name = message.data.get('name')
        new_name = message.data.get('new_name')
        if name:
            events = list(filter(
                lambda e: name.lower() in e.instance.vevent.summary.value.lower(), self.cal.date_search(datetime.now())))
            events.sort(
                key=lambda e: e.instance.vevent.dtstart.value.strftime("%Y-%m-%d, %H:%M"))
            event_names = []
            if len(events) == 0:
                self.speak("You have nothing to do!")
            else:
                for event in events:
                    event_names.append(event.instance.vevent.summary.value)

                def rename_event(self, i):
                    """
                    Deletes event at given index

                    Args:
                        i (number): Index of events-List
                    """
                    event = events[i]
                    event.instance.vevent.summary.value = new_name
                    event.save()
                    self.speak("Renamed event {name} to {new_name}.".format(
                        name=event_names[i], new_name=new_name))

                if len(events) == 1:
                    rename_event(self, 0)
                elif len(events) > 1:
                    self.speak('You have {length} events containing "{name}".'.format(
                        name=name, length=len(events)))
                    selection = self.ask_selection(
                        event_names, 'Which one do you want do rename?')
                    index = event_names.index(selection)
                    rename_event(self, index)
                else:
                    self.speak('You have no events containing "{name}".'
                               .format(name=name))


def create_skill():
    return Calendar()
