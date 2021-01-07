from dotenv import load_dotenv
from mycroft import MycroftSkill, intent_file_handler

from pathlib import Path
env_path = Path('./auth') / '.env'
load_dotenv(dotenv_path=env_path)

class Calendar(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('calendar.intent')
    def handle_calendar(self, message):
        print(USERNAME)
        self.speak_dialog('calendar')
        


def create_skill():
    return Calendar()

