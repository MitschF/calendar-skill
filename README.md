# <img src="https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/calendar-alt.svg" card_color="#392897" width="50" height="50" style="vertical-align:bottom"/> Calendar

## About
Calendar app, lets the user create a new appointment

## Getting started
For this skill to work you need to have a working mycroft system.

Type the following commands to install the skill:
```
cd <PATH-TO-MYCROFT-CORE>
source .venv/bin/activate
msm install https://github.com/MitschF/calendar-skill
```

Now open https://account.mycroft.ai/skills and provide the name, password and URL to the skill settings. 

## Tags
#Calendar
#Appoinment
#Event
#Assistant
#Caldav
#Nextcloud

## possible commands to create new events
create event "lecture" at "march 1st"
create event "lecture" at "march 1st" starting at "9" o'clock
create event "lecture" at "march 1st" starting at "9" o'clock till "11" o'clock

create event "today" named "lecture"
create event "today" starting at "9" o'clock with named "lecture"
create event "today" starting at "9" o'clock till "11" o'clock named "lecture"

create event "5 days from now" named "lecture"
create event "5 days from now" starting at "9" o'clock with named "lecture"
create event "5 days from now" starting at "9" o'clock till "11" o'clock named "lecture"

create event on "tuesday" named "lecture"
create event on "tuesday" starting at "9" o'clock named "lecture"
create event on "tuesday" starting at "9" o'clock till "11" o'clock named "lecture"


TODO:
create event "lecture" at "march 1st 2021 9am"
create event "lecture" at "march 1st 2021 9am" till "march 1st 2021 11am"

# Dokumentation
Voraussetzung für das Nachvollziehen der einzelnen Punkte ist ein korrekt eingerichtetes Mycroft System. Wie das geht, steht [hier](https://github.com/MycroftAI/mycroft-core) beschrieben. 
## Einen Skill anlegen
In der [offiziellen Mycroft Dokumentation](https://mycroft-ai.gitbook.io/docs/skill-development/introduction/your-first-skill#mycroft-skills-kit-msk) stehen die nötigen Schritte zur Erstellung eines ersten eigenen Skills. Wir haben zur Erstellung des Skills gebrauch vom "Mycroft Skills Kit" (MSK) gemacht, welches mit Mycroft installiert wird. 

Der Befehl `mycroft-msk create` in einem Terminal-Fenster führt einen durch die Initialisierung des Skills. Im folgenden Dialog wird nach Name, Beispielsätzen, Antworten, Beschreibung, Kategorien und Tags gefragt. Aus den Antworten erstellt das Programm ein "Skelett" des Skills, welches nun befüllt werden kann.

Zusätzlich wird gefragt, ob ein Github-Repository erstellt werden soll.

## Geheime Variablen
Wir haben einige Daten, die nicht öffentlich zugänglich sein dürfen, wie den Caldav / Nextcloud Benutzernamen, das Passwort und die URL. 

Um es dem Skill zu ermöglichen, auf diese Werte zuzugreifen, gibt es mehrere Möglichkeiten. Naheliegend ist das Auslesen einer Datei, welche nicht im Repository liegt, wie auch das [Nutzen einer .env-Datei](https://github.com/theskumar/python-dotenv). Darüber hinaus gibt es jedoch auch einen Weg, wie der Nutzer die Daten über die Web-Oberfläche anpassen kann.


## .env-Datei
Anfangs war die .env-Datei unser gewählter Weg. Im Repository gab es eine Datei names `default.env`. Der Nutzer des Skills musste die Datei kopieren und die Kopie umbenennen in `.env`. Dort mussten nun die Werte `USERNAME`, `PASSWORD` und `URL` entsprechend angepasst werden. Mithilfe des Python-Moduls `python-dotenv` war es nun möglich, die Werte aus der Datei auszulesen.

Dieser Weg ist jedoch nicht intuitiv und sehr schwer umzusetzen, wenn der Endnutzer sich nicht mit der Bedienung von Computern und Dateien auskennt.

## Mycroft Web-Oberfläche
Aus unserer Sicht ist dies der beste Ansatz. Der anfangs erstellte Skill bringt eine Datei namens `settingsmetadata.yaml` mit. Diese kann der Entwickler anpassen und mit zusätzlichen Feldern versehen. Mycroft erkennt diese Datei und ermöglicht es mit ihrer Hilfe dem User, die entsprechenden Felder über die Web-Oberfläche anzupassen. 

Auszug aus der `settingsmetadata.yaml`:
```yaml
- name: Caldav
      fields:
        - type: label
          label: Skill for Calendar-Management
        - name: username
          type: text
          label: Username
          value: ""
        - name: password
          type: password
          label: Password
          value: ""
        - name: url
          label: Url
          type: text
          value: "https://YOUR.CALENDAR.URL/remote.php/dav"
```


