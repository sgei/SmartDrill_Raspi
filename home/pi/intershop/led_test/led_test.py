#!/usr/bin/python
# test input buttons and outputs (leds)

import RPi.GPIO as GPIO
import subprocess, time, sys, threading
from sgei_gpio import OUT_3LEDS

IN_PORT1 = 23       # Input-Button 1 (battery defective)
IN_PORT2 = 4        # Input-Button 2 (drill)
LED = None          # LED object
LED1_PORT = 24      # GPIO-BCM Port (LED green MODE 1)
LED2_PORT = 22      # GPIO-BCM Port (LED green MODE 2)
LED3_PORT = 27      # GPIO-BCM Port (LED green MODE 3)
LED_TIME = 0.2      # ON/OFF time

# Initialize GPIO, BMC pin number
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN_PORT1, GPIO.IN)
GPIO.setup(IN_PORT2, GPIO.IN)
GPIO.setup(LED1_PORT, GPIO.OUT)
GPIO.setup(LED2_PORT, GPIO.OUT)
GPIO.setup(LED3_PORT, GPIO.OUT)

# initial output value
GPIO.output(LED1_PORT, GPIO.LOW)
GPIO.output(LED2_PORT, GPIO.LOW)
GPIO.output(LED3_PORT, GPIO.LOW)

# Interrupt routine for button1
def button1ISR(pin):
  global STATE, LED, LED1_PORT, LED2_PORT, LED3_PORT, LED_TIME

  # button pressed
  if (GPIO.input(pin)):

    if LED is None:
      LED = OUT_3LEDS(LED1_PORT, LED2_PORT, LED3_PORT, LED_TIME)
      LED.start()

  # button released
  else:
    pass

# Interrupt routine for button2
def button2ISR(pin):
  global STATE, LED

  # button pressed
  if (GPIO.input(pin)):

    if not LED is None:
      LED.stop()
      LED = None

  # button released
  else:
    pass

# Switch on the interrupt for the buttons
GPIO.add_event_detect(IN_PORT1, GPIO.RISING, callback=button1ISR)
GPIO.add_event_detect(IN_PORT2, GPIO.RISING, callback=button2ISR)

while True:
  try:
    time.sleep(300)
  except KeyboardInterrupt:

    if not LED is None:
      LED.stop()
      LED = None

    GPIO.cleanup()

    print ("\nBye")
    sys.exit(0)