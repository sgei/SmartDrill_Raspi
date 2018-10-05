#!/usr/bin/python
# shutdown Raspberry Pi via button

import RPi.GPIO as GPIO
import os, time, sys, threading
from filelock import FileLock

DAT_FILE = '/home/pi/intershop/scripts/drill/drill.dat'
LOCK_FILE = '/home/pi/intershop/scripts/drill/lock_local'

BUTTON_DRILL_PORT = 23
BUTTON_BATTERY_PORT = 4
LED_MODE1_PORT = 24
LED_MODE2_PORT = 22
LED_MODE3_PORT = 27

MODE = 0
MODE1_TIME = 0
MODE2_TIME = 0
MODE3_TIME = 0
DEGLITCH_TIME = 0.03
DRILL_TIME = 0
LOCK_CLOUD = 0
LOCK_LOCAL = 0

COMMAND = ''

# ****************************************************************************************************
# Initialize GPIO, BMC pin number

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON_DRILL_PORT, GPIO.IN)
GPIO.setup(BUTTON_BATTERY_PORT, GPIO.IN)

GPIO.setup(LED_MODE1_PORT, GPIO.OUT)
GPIO.setup(LED_MODE2_PORT, GPIO.OUT)
GPIO.setup(LED_MODE3_PORT, GPIO.OUT)

# initial output value
GPIO.output(LED_MODE1_PORT, GPIO.LOW)
GPIO.output(LED_MODE2_PORT, GPIO.LOW)
GPIO.output(LED_MODE2_PORT, GPIO.LOW)

# ****************************************************************************************************
# functions

def read_drill_dat(value):
  VALUE = ''
  rlock = FileLock(DAT_FILE, exclusive = False) # shared lock -> Lesen
  rlock.lock()
  try:
    for line in file(DAT_FILE):
      line = line.strip()
      if line.startswith('#'):
        continue

      t = line.split('=', 1)
      if len(t) < 2:
        continue

      if t[0].strip() == value:
        VALUE = int(t[1].strip())

  finally:
    rlock.unlock()
    return VALUE

def write_drill_dat():
  wlock = FileLock(DAT_FILE, exclusive = True) # exclusive lock -> zum Schreiben
  wlock.lock()
  try:
    os.system(COMMAND)

  finally:
    wlock.unlock()

def check_locked():
  global COMMAND

  if os.path.exists(LOCK_FILE):
    COMMAND = "sed -i 's/LOCK_LOCAL=.*/LOCK_LOCAL=" + '1' + "/' " + str(DAT_FILE)
    write_drill_dat()
    return 1
  else:
    COMMAND = "sed -i 's/LOCK_LOCAL=.*/LOCK_LOCAL=" + '0' + "/' " + str(DAT_FILE)
    write_drill_dat()
    return 0

def loop():
  global MODE, LOCK_CLOUD, LOCK_LOCAL

  MODE = read_drill_dat('MODE')
  LOCK_CLOUD = read_drill_dat('LOCK_CLOUD')
  LOCK_LOCAL = int(check_locked())

  print "MODE=%d | LOCK_CLOUD=%d | LOCK_LOCAL=%d" % ( MODE, LOCK_CLOUD, LOCK_LOCAL )

# ****************************************************************************************************
# Button: DRILL

DRILL_DEGLITCH = None

def drill_deglitch(pin, pin_state_required):
  pin_state_actual = GPIO.input(pin)
  if pin_state_actual == pin_state_required:
    drill_buttonISR(pin, int(pin_state_actual != 0))

# Interrupt routine
def drill_buttonISR(pin, pin_state = -1):
  global DRILL_DEGLITCH, DRILL_TIME, MODE1_TIME, MODE2_TIME, MODE3_TIME, COMMAND

  if not DRILL_DEGLITCH is None:
    if pin_state == -1:
      DRILL_DEGLITCH.cancel()

    DRILL_DEGLITCH = None

  if pin_state == -1:
    DRILL_DEGLITCH = threading.Timer(DEGLITCH_TIME, drill_deglitch, args = ( pin, GPIO.input(pin), ))
    DRILL_DEGLITCH.start()
    return    

  # button pressed
  if pin_state:

    DRILL_TIME = time.time()

    if MODE == 1:
      GPIO.output(LED_MODE1_PORT, GPIO.HIGH)
      GPIO.output(LED_MODE2_PORT, GPIO.LOW)
      GPIO.output(LED_MODE3_PORT, GPIO.LOW)
      print "MODE = %d" % MODE
    elif MODE == 2:
      GPIO.output(LED_MODE1_PORT, GPIO.LOW)
      GPIO.output(LED_MODE2_PORT, GPIO.HIGH)
      GPIO.output(LED_MODE3_PORT, GPIO.LOW)
      print "MODE = %d" % MODE
    elif MODE == 3:
      GPIO.output(LED_MODE1_PORT, GPIO.LOW)
      GPIO.output(LED_MODE2_PORT, GPIO.LOW)
      GPIO.output(LED_MODE3_PORT, GPIO.HIGH)
      print "MODE = %d" % MODE
    else:
      GPIO.output(LED_MODE1_PORT, GPIO.LOW)
      GPIO.output(LED_MODE2_PORT, GPIO.LOW)
      GPIO.output(LED_MODE3_PORT, GPIO.LOW)
      print "MODE = %d" % MODE

  # button released
  else:
    GPIO.output(LED_MODE1_PORT, GPIO.LOW)
    GPIO.output(LED_MODE2_PORT, GPIO.LOW)
    GPIO.output(LED_MODE3_PORT, GPIO.LOW)
    DRILL_TIME = time.time() - DRILL_TIME

    if MODE == 1:
      MODE1_TIME = int(MODE1_TIME) + int(DRILL_TIME)
      print "MODE = %d | DRILL_TIME = %d | MODE%d_TIME = %d" % ( MODE, DRILL_TIME, MODE, MODE1_TIME )
      COMMAND = "sed -i 's/USAGE_TIME_MODE_" + str(MODE) + "=.*/USAGE_TIME_MODE_" + str(MODE) + "=" + str(MODE1_TIME) + "/' " + str(DAT_FILE)
    elif MODE == 2:
      MODE2_TIME = int(MODE2_TIME) + int(DRILL_TIME)
      print "MODE = %d | DRILL_TIME = %d | MODE%d_TIME = %d" % ( MODE, DRILL_TIME, MODE, MODE2_TIME )
      COMMAND = "sed -i 's/USAGE_TIME_MODE_" + str(MODE) + "=.*/USAGE_TIME_MODE_" + str(MODE) + "=" + str(MODE2_TIME) + "/' " + str(DAT_FILE)
    elif MODE == 3:
      MODE3_TIME = int(MODE3_TIME) + int(DRILL_TIME)
      print "MODE = %d | DRILL_TIME = %d | MODE%d_TIME = %d" % ( MODE, DRILL_TIME, MODE, MODE3_TIME )
      COMMAND = "sed -i 's/USAGE_TIME_MODE_" + str(MODE) + "=.*/USAGE_TIME_MODE_" + str(MODE) + "=" + str(MODE3_TIME) + "/' " + str(DAT_FILE)
    else:
      pass

    write_drill_dat()

# ****************************************************************************************************
# Button: BATTERY    

BATTERY_DEGLITCH = None

def battery_deglitch(pin, pin_state_required):
  pin_state_actual = GPIO.input(pin)
  if pin_state_actual == pin_state_required:
    battery_buttonISR(pin, int(pin_state_actual != 0))

# Interrupt routine
def battery_buttonISR(pin, pin_state = -1):
  global BATTERY_DEGLITCH

  if not BATTERY_DEGLITCH is None:
    if pin_state == -1:
      BATTERY_DEGLITCH.cancel()

    BATTERY_DEGLITCH = None

  if pin_state == -1:
    BATTERY_DEGLITCH = threading.Timer(DEGLITCH_TIME, battery_deglitch, args = ( pin, GPIO.input(pin), ))
    BATTERY_DEGLITCH.start()
    return    

  # button pressed
  if pin_state:
    HEALTH = 'Faulty'

  # button released
  else:
    HEALTH = 'Good'

  print "HEALTH = %s" % HEALTH

  COMMAND = "sed -i 's/HEALTH=.*/HEALTH=" + str(HEALTH) + "/' " + str(DAT_FILE)
  write_drill_dat()

# ****************************************************************************************************
# INTERRUPS

# Switch on the interrupts for the buttons
GPIO.add_event_detect(BUTTON_DRILL_PORT, GPIO.BOTH, callback=drill_buttonISR)
GPIO.add_event_detect(BUTTON_BATTERY_PORT, GPIO.BOTH, callback=battery_buttonISR)

while True:
  try:
    loop()
    time.sleep(2)
  except KeyboardInterrupt:

    GPIO.remove_event_detect(BUTTON_DRILL_PORT)
    GPIO.remove_event_detect(BUTTON_BATTERY_PORT)
    GPIO.cleanup()

    print ("\nBye")
    sys.exit(0)