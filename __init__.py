from mycroft import MycroftSkill, intent_file_handler


class Calendar(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('calendar.intent')
    def handle_calendar(self, message):
        self.speak_dialog('calendar')


def create_skill():
    return Calendar()

