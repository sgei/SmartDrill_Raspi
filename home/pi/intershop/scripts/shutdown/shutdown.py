#!/usr/bin/python
# shutdown Raspberry Pi via button

import RPi.GPIO as GPIO
import subprocess, time, sys, syslog, threading, signal
from sgei_gpio import OUT_BLINK

IN_PORT = 17                  # Input Shutdown-Button
LED1 = None                   # yellow LED object (Shutdown-LED)
LED1_PORT = 18                # GPIO-BCM Port
LED1_TIME = 0.2               # ON/OFF time for LED flashing
STATE = 0                     # program state
T1 = None                     # timer object for first press duration
T1_TIME = 2.0                 # timer time
T2 = None                     # timer object for LED flashing time
T2_TIME = 5.0                 # timer time
STATE_LCK = threading.Lock()  # lock object to make STATE atomic

# Initialize GPIO, BMC pin number
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN_PORT, GPIO.IN)
GPIO.setup(LED1_PORT, GPIO.OUT)

# initial output value
GPIO.output(LED1_PORT, GPIO.LOW)

def SET_STATE(state):
  global STATE
  STATE_LCK.acquire()
  try:
    STATE = state

  finally:
    STATE_LCK.release()

def t1_action():
  global LED1

  SET_STATE(2)

  LED1 = OUT_BLINK(LED1_PORT, LED1_TIME)
  LED1.start()

  print "STATE = %d - T1 beendet, LED blinkt" % (STATE,)

def t2_action():
  SET_STATE(0)
  if not LED1 is None:
    LED1.stop()

  print "STATE = %d - T2 beendet, RESET" % (STATE,)

DEGLITCH = None
DEGLITCH_TIME = 0.03

def deglitch(pin, pin_state_required):
  pin_state_actual = GPIO.input(pin)
  if pin_state_actual == pin_state_required:
    buttonISR(pin, int(pin_state_actual != 0))

# Interrupt routine for shutdown button
def buttonISR(pin, pin_state = -1):
  global T1, T2, DEGLITCH

  if not DEGLITCH is None:
    if pin_state == -1:
      DEGLITCH.cancel()

    DEGLITCH = None

  if pin_state == -1:
    DEGLITCH = threading.Timer(DEGLITCH_TIME, deglitch, args = ( pin, GPIO.input(pin), ))
    DEGLITCH.start()
    return    

  # button pressed
  if pin_state:
    if STATE == 0:
      SET_STATE(1)

      T1 = threading.Timer(T1_TIME, t1_action)
      T1.start()

      print "STATE = %d - T1 gestartet" % (STATE,)

    if STATE == 2:
      T1 = None
      SET_STATE(3)

      if not T2 is None:
        T2.cancel()
        T2 = None

      print "STATE = %d - T2 abgebrochen, SHUTDOWN" % (STATE,)

  # button released
  else:
    if STATE == 1:
      if not T1 is None:
        T1.cancel()
        T1 = None

      SET_STATE(0)

      print "STATE = %d - T1 abgebrochen" % (STATE,)

    if STATE == 2:
      T1 = None
      T2 = threading.Timer(T2_TIME, t2_action)
      T2.start()

      print "STATE = %d - T2 gestartet, warte auf Taste" % (STATE,)

  if STATE == 3:
    if not LED1 is None:
      LED1.stop()

    SET_STATE(0)
    GPIO.output(LED1_PORT, GPIO.HIGH)

    #print "Shutdown..."
    syslog.syslog('Shutdown: System halted');
    subprocess.call(['shutdown', '-h', 'now'], shell=False)

# Switch on the interrupt for the shutdown button
GPIO.add_event_detect(IN_PORT, GPIO.BOTH, callback=buttonISR)

def signal_term_handler(signal, frame):
  GPIO.remove_event_detect(IN_PORT)
  print ("\nKilled!")
  sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)

syslog.syslog('Shutdown.py started');
while True:
  try:
    time.sleep(300)
  except KeyboardInterrupt:

    if not LED1 is None:
      LED1.stop()

    GPIO.remove_event_detect(IN_PORT)
    GPIO.cleanup()

    syslog.syslog('Shutdown terminated (Keyboard)');
    print ("\nBye")
    sys.exit(0)