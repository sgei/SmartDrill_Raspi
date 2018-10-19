#!/usr/bin/python

import time, sys, os
import requests
from filelock import FileLock

URL = 'https://deviceservicea.azurewebsites.net/devices/473095323502/paidUnits'
USAGE_TIME_MODE_1 = 0
USAGE_TIME_MODE_2 = 0
USAGE_TIME_MODE_3 = 0
TIME_USED = 0
TIME_PAID = 0
AMOUNT = 10
WALLET = 50
LOWER_PERCENTAGE = 0.8
UPPER_PERCENTAGE = 0.9
DAT_FILE = '/home/pi/intershop/scripts/drill/drill.dat'
LOCK_FILE = 'lock_local'
TIME = ''

def deleteFile(file):
  if os.path.exists(file):
    os.remove(file)

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

def send():
  r = requests.post(URL, data = str(TIME_PAID * (10**18)))
  #print(r.status_code)
  print "[%s] eth-pi: transaction has been sent" % ( TIME )

def loop():
  global TIME, USAGE_TIME_MODE_1, USAGE_TIME_MODE_2, USAGE_TIME_MODE_3, TIME_USED, TIME_PAID

  TIME =  time.strftime("%d %b %Y %H:%M:%S")

  USAGE_TIME_MODE_1 = read_drill_dat('USAGE_TIME_MODE_1')
  USAGE_TIME_MODE_2 = read_drill_dat('USAGE_TIME_MODE_2')
  USAGE_TIME_MODE_3 = read_drill_dat('USAGE_TIME_MODE_3')

  TIME_USED = USAGE_TIME_MODE_1 + USAGE_TIME_MODE_2 + USAGE_TIME_MODE_3

  #print "TIME_USED=%d | TIME_PAID=%d" % ( TIME_USED, TIME_PAID )
  print "\n"
  print "[%s] eth-pi: time used is %d seconds" % ( TIME, TIME_USED )
  print "[%s] eth-pi: time paid is %d seconds" % ( TIME, TIME_PAID )
  
  if ( TIME_USED == 0 ):
    if ( TIME_PAID != AMOUNT ):
      deleteFile(LOCK_FILE)
      TIME_PAID = AMOUNT
      send()

  if ( TIME_USED < TIME_PAID ):
    print "[%s] eth-pi: time_usage < time_paid" % ( TIME )
    print "[%s] eth-pi: device can stay activated" % ( TIME )

  if ( TIME_USED < TIME_PAID * UPPER_PERCENTAGE ):
    if ( TIME_USED >= TIME_PAID * LOWER_PERCENTAGE ):
      print "[%s] eth-pi: time_usage near to time_paid" % ( TIME )
  else:
    if ( TIME_PAID < WALLET ):
      TIME_PAID = TIME_PAID + AMOUNT
      send()

  if ( TIME_PAID == WALLET ):
    if ( TIME_USED < WALLET):
      print "[%s] eth-pi: waiting for last usage" % ( TIME )
    else:
      f = open(LOCK_FILE, "w")
      print "[%s] eth-pi: lock file has been created" % ( TIME )
      print "[%s] eth-pi: shutdown device" % ( TIME )

while True:
  try:
    loop()
    time.sleep(2)
  except KeyboardInterrupt:

    print ("\nBye")
    sys.exit(0)