#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import datetime
import os
from subprocess import Popen, PIPE, STDOUT
import gammu

import getpass

#print(os.getlogin())
#print(getpass.getuser())
numbers = ["+436507348434", "+436644139604"]
number = numbers[1]
com = ""

def send_sms(text):
    global sm
    #command = "echo " + text + " | gammu -c /etc/gammu-smsdrc sendsms TEXT +436507348434"
    message= {
    "Text": text,
    "SMSC": {"Location":1},
    "Number": number,
    }
    sm.SendSMS(message)
    print("%s - Antwort SMS gesendet" % datetime.datetime.now())
    #inp, stream = os.popen(command)
    #output = stream.read()
    #p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    #output = p.stdout.read()
    #print(output)
    """if "OK" in str(output):
        print("SMS gesendet")
    if "Fehler" in str(output):
        print("SMS senden fehlgeschlagen:")
        print(output)
    """
    return

def check_sms(sm, type, data):
    #global sm
    global number
    global com
    #print("check")
    try:
        message = sm.GetNextSMS(Folder=0,Start=True)
        sm.DeleteSMS(Folder=0, Location=message[0]["Location"])
        if message[0]["Number"] not in numbers:
            return "wrong number"
        com = message[0]["Text"]
        com = com.lower()
        print(str(datetime.datetime.now()), " - Nachricht angekommen von", message[0]["Number"], " Kommando: ", com)
        number = message[0]["Number"]
        #return com
        #print(message["Number"], message["Text"])
    except gammu.ERR_EMPTY:
        #print("empty")
        com = "empty"
    #print(message)

def take_pic():
    out = os.popen("/bin/bash /home/pi/take_picture.sh")
    return



print("%s - SMS Verbindung erzeugen" % datetime.datetime.now())
sm = gammu.StateMachine()
print("%s - Lese Konfiguration" % datetime.datetime.now())
sm.ReadConfig(Filename="/etc/gammu-smsdrc")
print("%s - SMS Initialisierung starten" % datetime.datetime.now())
initialize = True
while initialize:
    try:
        sm.Init()
        initialize = False
    except gammu.ERR_DEVICENOTEXIST:
        print("%s - Modem nicht gefunden. Suche in 10 Sekunden erneut" % datetime.datetime.now())
        time.sleep(10)
print("%s - SMS Initialisierung erfolgreich" % datetime.datetime.now())
#print(sm)
#sm.Init()

# BCM GPIO-Referenen verwenden (anstelle der Pin-Nummern)
# und GPIO-Eingang definieren
GPIO.setmode(GPIO.BCM)
GPIO_PIR = 17

print("%s - Kommunikation mit Sensor gestartet (CTRL-C to exit)" % datetime.datetime.now())

# Set pin as input
GPIO.setup(GPIO_PIR,GPIO.IN)

# Initialisierung
Read  = 0
State = 0
anzahl = 1
erste = ""
gesamt = 0
run = False
isrunning = False
com = ""
strange = 0

print("%s - Warten, bis Sensor im Ruhezustand ist ..." % datetime.datetime.now())
#send_sms("bla")
# Schleife, bis PIR == 0 ist
while GPIO.input(GPIO_PIR) != 0:
  time.sleep(0.1)
print("%s - Bereit..." % datetime.datetime.now())

starttime = datetime.datetime.now()

# Callback-Funktion
def MOTION(PIR_GPIO):
  global anzahl
  global erste
  global gesamt
  global strange
  event = datetime.datetime.now()
  ev2=str(event)
  nachricht =  ev2 + " - " + str(anzahl) +".Bewegung erkannt"
  gesamt += 1
  #print("Gesamtanzahl an Bewegungen:  %s " % gesamt)
  print(nachricht)
  if anzahl == 1:
      erste = event
      anzahl += 1
  else:
      #print("gültig")
      dif = event - erste
      if dif.total_seconds() < 60:
         #print(dif.total_seconds())
         anzahl += 1
      else:
          print("%s - Nicht genügend Bewegungen im Zeitraum von 1 Minute. Anzahl wird zurückgesetzt" % datetime.datetime.now())
          anzahl = 1
  if anzahl == 5:
      text = "%s - Aussergewöhnliche Bewegung erkannt." % datetime.datetime.now()
      strange += 1
      print(text)
      send_sms(text)
      #print("SMS gesendet")
      anzahl = 1

  #time.sleep(3)
  print("%s - Sensor zurückgesetzt" % datetime.datetime.now())
  return





sm.SetIncomingCallback(check_sms)

try:
  sm.SetIncomingSMS(Enable=True)
  send_sms("%s - Alarmanlage ist startbereit" % datetime.datetime.now())
  while True:
    #print(running)
    #sm.SetIncomingCallback(Callback = check_sms)
    time.sleep(1)
    #com = check_sms()
    #print(com)
    status = sm.GetModel() #need to keep callback active
    if com == "status" and run==True:
        uptime = datetime.datetime.now() - starttime
        nachricht =  str(datetime.datetime.now()) + " - Überwachung läuft seit: " + str(starttime) + ". Aussergewöhnliche Bewegungen registriert: "+str(strange)+". Gesamtbewegungen registriert: " + str(gesamt)
        print(nachricht)
        send_sms(nachricht)
    elif com == "status" and run==False:
        nachricht = "%s - Überwachung ist deaktiviert" % datetime.datetime.now()
        send_sms(nachricht)
        print(nachricht)
    elif com == "start":
        print("%s - Überwachung wird gestartet" % datetime.datetime.now())
        GPIO.add_event_detect(GPIO_PIR, GPIO.RISING, callback=MOTION)
        print("%s - Warten auf Bewegung" % datetime.datetime.now())
        run = True
        starttime = datetime.datetime.now()
        send_sms("Überwachung wurde gestartet am %s" % starttime)
    elif com == "stop":
        print("%s - Überwachung wird gestoppt" % datetime.datetime.now())
        GPIO.remove_event_detect(GPIO_PIR)
        send_sms("%s - Überwachung wurde gestoppt." % datetime.datetime.now())
        run = False
    elif com == "bild":
        print("%s - Bild wird gemacht" % datetime.datetime.now())
        take_pic()
        send_sms("%s - Bild wurde per email gesendet." % datetime.datetime.now())
    elif com == "wrong number":
        print("%s - Kommando von falscher Nummer gesendet. Wird ignoriert" % datetime.datetime.now())
    elif com =="":
        continue
    else:
        print("%s - Kommando nicht erkannt" % datetime.datetime.now())
    com = ""
except KeyboardInterrupt:
  # Programm beenden
  print("%s - Ende..." % datetime.datetime.now())
  GPIO.cleanup()