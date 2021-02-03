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


___
___

# Dokumentation
Voraussetzung für das Nachvollziehen der einzelnen Punkte ist ein korrekt eingerichtetes Mycroft System. Wie das geht, steht [hier](https://github.com/MycroftAI/mycroft-core) beschrieben. 
## Einen Skill anlegen
In der [offiziellen Mycroft Dokumentation](https://mycroft-ai.gitbook.io/docs/skill-development/introduction/your-first-skill#mycroft-skills-kit-msk) stehen die nötigen Schritte zur Erstellung eines ersten eigenen Skills. Wir haben zur Erstellung des Skills gebrauch vom "Mycroft Skills Kit" (MSK) gemacht, welches mit Mycroft installiert wird. 

Der Befehl `mycroft-msk create` in einem Terminal-Fenster führt einen durch die Initialisierung des Skills. Im folgenden Dialog wird nach Name, Beispielsätzen, Antworten, Beschreibung, Kategorien und Tags gefragt. Aus den Antworten erstellt das Programm ein "Skelett" des Skills, welches nun befüllt werden kann.

Zusätzlich wird gefragt, ob ein Github-Repository erstellt werden soll.

## Geheime Variablen
Wir haben einige Daten, die nicht öffentlich zugänglich sein dürfen, wie den Caldav / Nextcloud Benutzernamen, das Passwort und die URL. 

Um es dem Skill zu ermöglichen, auf diese Werte zuzugreifen, gibt es mehrere Möglichkeiten. Naheliegend ist das Auslesen einer Datei, welche nicht im Repository liegt, wie auch das [Nutzen einer .env-Datei](https://github.com/theskumar/python-dotenv). Darüber hinaus gibt es jedoch auch einen Weg, wie der Nutzer die Daten über die Web-Oberfläche anpassen kann.


### .env-Datei
Anfangs war die .env-Datei unser gewählter Weg. Im Repository gab es eine Datei names `default.env`. Der Nutzer des Skills musste die Datei kopieren und die Kopie umbenennen in `.env`. Dort mussten nun die Werte `USERNAME`, `PASSWORD` und `URL` entsprechend angepasst werden. Mithilfe des Python-Moduls `python-dotenv` war es nun möglich, die Werte aus der Datei auszulesen.

Dieser Weg ist jedoch nicht intuitiv und sehr schwer umzusetzen, wenn der Endnutzer sich nicht mit der Bedienung von Computern und Dateien auskennt.

### Mycroft Web-Oberfläche
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

Screenshot der [Weboberfläche](https://home.mycroft.ai/skills):

![Weboberfläche: Skill-Konfiguration](documentation/assets/mycroft-web-skill-config.jpg)

Auf diese Weise ist es jedem Nutzer einfach möglich, die Zugangsdaten anzupassen, unabhängig vom eigenen technischen Verständnis. Innerhalb des Skills kann man jetzt wie folgt auf die Variablen zugreifen:
```python
USERNAME = self.settings.get('username')
PASSWORD = self.settings.get('password')
URL = self.settings.get('url')

self.client = caldav.DAVClient(url=URL, username=USERNAME, password=PASSWORD)
```

## Hauptaufgabe: Nächsten Termin zurückgeben
Die Hauptaufgabe, die der Skill zu erfüllen hat, ist das Zurückgeben des nächsten Termines, wenn man ihn fragt. 

### Vorüberlegung
Bei der Progammierung einer Funktion für einen Sprachassistenten gibt es verschiedene Überlegungen, die man sich im Voraus machen muss, unter Anderem:
- Wie aktiviere ich die Funktion?
- Gibt es Parameter?
- Was soll der Assitent antworten?

Die Basisaufgabe macht einem die Vorüberlegung relativ einfach.

Die Funktion wird aktiviert durch die Frage nach dem nächsten Termin in Form von **"What's my next appointment?"** Der Nutzer könnte diese Frage jedoch auch auf eine andere Art und Weise stellen, z.B. **"next event"**. 

Es gibt keine Parameter, wie Datum, Uhrzeit oder Anzahl der Antworten, da konkret nach dem **einen** nächsten Termin gefragt wird.

Aber was soll der Assistent antworten? Wir haben uns dafür entschieden, den Namen des nächsten Termins, sowie Datum und bei Bedarf die Uhrzeit zurückzugeben. Eine antwort würde also wie folgt aussehen:
- Wenn der nächste Termin ganztägig ist: **"Next appointment: Christmas on 24. of December, 2021"**
- Wenn der nächste Termin nicht ganztägig ist: **"Next appointment: Lecture on 3. of February, 2021 at 14:15"**

### Programmierung
Bei der Programmierung des Skills haben wir Gebrauch der [Mycroft Skill Struktur](https://mycroft-ai.gitbook.io/docs/skill-development/skill-structure) gemacht. Wichtig sind hier die [__init__.py](https://mycroft-ai.gitbook.io/docs/skill-development/skill-structure#__init__-py), welche die tatsächliche Programmier-Logik beinhaltet, sowie der [locale-Ordner](https://mycroft-ai.gitbook.io/docs/skill-development/skill-structure#vocab-dialog-and-locale-directories), in dem Dateien stehen, welche sich um den Dialog mit Mycroft kümmern. 
#### Dialog (locale-Ordner)
Dateien mit der Endung `.intent` beinhalten Sätze, die der Nutzer sagen soll, damit Mycroft reagiert. Dateien mit der Endung `.dialog` beinhalten Sätze, die Mycroft antwortet. Dann gibt es noch Dateien mit der Endung `.entity`. In dieser wird die "Form" einer Eingabe definiert. Die Entity-Dateien arbeiten immer zusammen mit einer .intent-Datei. [Mehr dazu hier.](https://mycroft-ai.gitbook.io/docs/mycroft-technologies/padatious#creating-entities)

Was der Nutzer sagen muss, um den Skill zu aktivieren steht in der Datei `locale/en-us/what.is.next.intent` geschrieben. Diese beinhaltet folgendes:

```
((what is | what's) (my | the) | ) next (event | appointment)
```

Der Satz oben kann unter anderem aufgelöst werden in: 
- what is my next appointment
- what's the next event
- my next event
- next appointment

Mehr dazu [hier](#-Intent-Organisation).

#### Programmierlogik (__init__.py)

## Bonusaufgaben

### Terminabfrage im gewünschten Zeitraum
Zusätzlich zur Rückgabe des nächsten Termins bietet unser Skill dem Benutzer die Möglichkeit, Termine, welche in einem bestimmten Zeitraum liegen zu erfragen. Die Funktionalität unterscheidet sich dabei nicht stark von der Hauptaufgabe. Sie wird lediglich um zwei Parameter erweitert. 

Beim Abfragen der Termine eines Zeitraumes ist es notwendig, dass der Benutzer den Start- und Endzeitpunkt festlegt um die gewünschten Termine einzugrenzen. Dieser Start- und Endzeitpunkt wird im `.intent` File mit sogennanten {Wildcards} hinterlegt (z.B. "get events from {start_time} till {end_time}"). Da die Wildcards Zeitangaben beinhalten, ist ein Parser notwendig, der die Benutzereingaben in die passenden Datumsformate umwandelt, die zur Weiterverarbeitung notwendig sind. Mehr Informationen dazu in den Kapiteln [Wildcards](###-Wildcards) und [Parser](###-Parser).


Die Terminabfrage im gewünschten Zeitraum unterstützt folgende Funktionalität: 
- Ausgabe aller Termine vom genannten Startdatum bis zum genannten Enddatum
- Ausgabe aller Termine im Kalender, die nach dem genannten Startdatum liegen

Mögliche Erweiterungen:
- Ausgabe aller Termine für den gennanten Zeitraum in Zeiteinheiten (z.B. "get events for the next 2 weeks")
    - im `.intent` File bereits hinterlegt, aber noch nicht ausimplementiert 


### Erstellung von Terminen
Das Anlegen eines neuen Termins benötigt zusätzliche Parameter in der Benutzereingabe im Vergleich zur Terminabfrage im gewünschten Zeitraum.

Durch diese zusätzlichen Parameter wird auch das `.intent` File komplizierter. Der Benutzer soll aber nicht an eine feste Sprechweise gebunden sein, wenn er einen neuen Termin anlegen will. Zum Beispiel kann ein neuer Termin sowohl über den Befehl 
- "create appointment lecture on monday from 9 o'clock till 11 o'clock" 

als auch 
- "create appointment on monday from  9 o'clock till 11 o'clock with description lecture"

erstellt werden. Damit beide Möglichkeiten unterstützt werden, wird das `.intent` File automatisch doppelt so groß.

Genauso wie bei der Terminabfrage im gewünschten Zeitraum sind auch hier [Wildcards](###-Wildcards) und [Parser](###-Parser) notwendig.

Die Erstellung von Terminen unterstützt folgende Funktionalität: 
- Erstellung eines ganztätigen Termins am gennanten Tag mit gennanten Beschreibung
- Erstellung eines Termins am gennanten Tag mit gennanten Beschreibung mit zusätzlich definiertem Start- und Endzeitpunkt
- Erstellung eines Termins am gennanten Tag mit gennanten Beschreibung mit zusätzlich definiertem Startpunkt und 1 stündiger Dauer


Mögliche Erweiterungen:
- Erstellung von mehrtägigen Terminen
- Erstellung von Todos 


## Mycroft Zusatzfunktionen
Für die Erfüllung der Bonusaufgaben waren einige zusätzliche Mycroft Funktionalitäten notwendig. Die wichtigsten werden in den nächsten Kapiteln beschrieben. 

### Wildcards
Wildcards können im `.intent` File an den gewünschten Stellen plaziert werden und dienen als Platzhalter für Parameter bei der Benutzereingabe. So kann zum Beispiel im `.intent` File der Satz 

```delete event {name}``` 

hinterlegt werden. Dabei wird automatisch die Eingabe des Benutzers, welche nach dem Wort "event" folgt in {name} abgespeichert. Im Skill selbst kann auf diesen Wert über 

```name = message.data.get("name")``` 

zugegriffen werden und somit zur Weiterverarbeitung an andere Funktionen übergeben werden.


### Entity
Zusätzlich können zu den Wildcards Entities definiert werden, welche in speziellen `.entity` Files hinterlegt werden. Ist zu einer Wildcard ein `.entity` File vorhanden, dann kann diese Wildcard nur Werte annehmen, die im `.entity` File definiert sind (ähnlich [enumeration types](https://en.wikipedia.org/wiki/Enumerated_type) die aus anderen Programmierkontexten bekannt sind). 

In unserem Fall haben wird Entities genutzt, um die Eingabe von Zahlen zu beschränken. Bei der Frage an Mycroft "what are my next 11 appointments" ist die Zahl 11 eine Wildcard, die zusätzlich Teil von  ```number.entity``` ist. Das `.entity` File legt in unserem Fall nur fest, wie viele Stellen die Wildcard haben darf. In unserem Fall sind nur ein- und zweistellige Werte gültig, welche durch die beiden Werte ```#``` und ```##``` im .entity` File erlaubt werden.

Entities bieten viele Möglichkeiten Benutzereingaben geziehlt einzuschränken, um auslösen von Funktionen mit falschen Eingaben zu vermeiden. Sie sind also nicht zur eigentlichen Funktionalität des Skills notwendig, helfen aber bei der Qualitätsssicherung.


### Parser
Da unser Skill mit einem Kalender arbeitet, werden bei Benutzereingaben oft Datumsangaben benötigt. Diese Angaben können vom Benutzer in verschiedenen Formen eigegeben werden, werden aber von den darunterliegenden Funktionen oft in einem bestimmten Format benötigt. 

Wir haben dafür folgende von Mycroft erstellten [Parser](https://mycroft-core.readthedocs.io/en/latest/source/mycroft.util.parse.html) im "util"-Package verwendet. 

```mycroft.util.parse.extract_datetime``` kann zusammen mit einer Wildcard dazu verwendet werden, eine Benutzereingabe (z.B. zu einem Startdatum einer Terminsuche) direkt in ein [datetime](https://docs.python.org/3/library/datetime.html)-Objekt zu parsen. Dabei ist zu erwähnen, dass die Eingabe in vielen Verschiedenen Formen erkannt wird. 

Mögliche Eingabeformate beispielhaft:
- today/tomorrow
- 5 days from today 
- monday
- march 1
- march 1st
- march 1 2021 10am

```mycroft.util.parse.extract_number``` kann zusammen mit einer Wildcard dazu verwendet werden, eine Benutzereingabe direkt in einen Wert vom Typ ```int``` oder ```float``` zu parsen.

### Intent Organisation
`.intent` Files können im Verlauf der Entwicklung eines Skills immer größer werden, da man dem Benutzer verschiedene Möglichkeiten angeboten will, um die Skills zu bediehnen. Um unnötige Schreibarbeit zu vermeiden bietet Mycroft [Klammer-Schreibweisen](https://mycroft-ai.gitbook.io/docs/mycroft-technologies/padatious#parentheses-expansion) an, die simple ```either or``` Logik unterstützen. 

Dabei können Klammern und senkrechte Striche ("|") verwendet werden um festzulegen, dass jeweils nur eines der beiden Elemente in der Klammer auftreten muss. Das Element vor oder nach dem senkrechten Strich kann auch weggelassen werden, um auszudrücken, dass ein Element oder "nichts" in der Benutzereingabe vorkommen darf.

Hier ein Beispiel aus einem unserer Files, bei dem Klammern verschachtelt werden und zusätzlich mit Wildcards ergänzt werden.

```create (appointment | event) {description} on {start_date} ( | (from | starting at) {start_time} o'clock ( | till {end_time} o'clock))``` 

```create (appointment | event) on {start_date} ( | (from | starting at) {start_time} o'clock ( | till {end_time}) o'clock) with (name | description) {description}``` 

Diese beiden Zeilen können mit folgenden Benutzereingaben übereinstimmen (mit Beispielhaften Werten für die Wildcards)

- create event "lecture" at "march 1st"
- create event "lecture" at "march 1st" starting at "9" o'clock
- create event "lecture" at "march 1st" starting at "9" o'clock till "11" o'clock
- create event "today" named "lecture"
- create event "today" starting at "9" o'clock with named "lecture"
- create event "today" starting at "9" o'clock till "11" o'clock named "lecture"
- create event "5 days from now" named "lecture"
- create event "5 days from now" starting at "9" o'clock with named "lecture"
- create event "5 days from now" starting at "9" o'clock till "11" o'clock named "lecture"
- create event on "tuesday" named "lecture"
- create event on "tuesday" starting at "9" o'clock named "lecture"
- create event on "tuesday" starting at "9" o'clock till "11" o'clock named "lecture"

Dieses Beispiel zeigt die Mächtigkeit dieses Mycroft Features und die Notwendigkeit, dieses einzusetzen, wenn man einen Skill erstellen möchte, der vom Benutzer leicht bediehnbar ist. 



## Fazit

