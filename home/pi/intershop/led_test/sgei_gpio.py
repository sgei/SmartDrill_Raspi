import threading
import RPi.GPIO as GPIO

class OUT_BLINK():

  def __init__(self, port, time):
    self.thread = None
    self.event = None
    self.port = port
    self.time = time

  def __action(self):
    while True:
      GPIO.output(self.port, GPIO.HIGH)
      self.event.wait(self.time)
      if self.event.isSet():
        break

      GPIO.output(self.port, GPIO.LOW)
      self.event.wait(self.time)
      if self.event.isSet():
        break

    GPIO.output(self.port, GPIO.LOW)

  def start(self):
    self.event = threading.Event()
    self.thread = threading.Thread(target = self.__action)
    self.thread.setDaemon(True)
    self.thread.start()

  def stop(self):
    if not self.thread is None:
     try:
       self.event.set()
       self.thread.join()

     finally:
       self.thread = None
       self.event = None

class OUT_3LEDS():

  def __init__(self, port1, port2, port3, time):
    self.thread = None
    self.event = None
    self.port1 = port1
    self.port2 = port2
    self.port3 = port3
    self.time = time

  def __action(self):
    while True:
      GPIO.output(self.port1, GPIO.HIGH)
      GPIO.output(self.port2, GPIO.LOW)
      GPIO.output(self.port3, GPIO.LOW)
      self.event.wait(self.time)
      if self.event.isSet():
        break

      GPIO.output(self.port1, GPIO.LOW)
      GPIO.output(self.port2, GPIO.HIGH)
      GPIO.output(self.port3, GPIO.LOW)
      self.event.wait(self.time)
      if self.event.isSet():
        break

      GPIO.output(self.port1, GPIO.LOW)
      GPIO.output(self.port2, GPIO.LOW)
      GPIO.output(self.port3, GPIO.HIGH)
      self.event.wait(self.time)
      if self.event.isSet():
        break

    GPIO.output(self.port1, GPIO.LOW)
    GPIO.output(self.port2, GPIO.LOW)
    GPIO.output(self.port3, GPIO.LOW)

  def start(self):
    self.event = threading.Event()
    self.thread = threading.Thread(target = self.__action)
    self.thread.setDaemon(True)
    self.thread.start()

  def stop(self):
    if not self.thread is None:
     try:
       self.event.set()
       self.thread.join()

     finally:
       self.thread = None
       self.event = None