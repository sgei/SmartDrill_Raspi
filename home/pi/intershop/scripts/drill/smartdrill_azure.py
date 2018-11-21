#!/usr/bin/python

import sys, os, datetime, re, threading, traceback, subprocess
import RPi.GPIO as GPIO
import iothub_client
import inotify.adapters, inotify.constants
import json
import fcntl

import logging
try:
  inotify.adapters._LOGGER.addHandler(logging.StreamHandler(sys.stderr))

except ( AttributeError, ):
  pass

# LED Azure Sync #################################################################################
LED1_PORT = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED1_PORT, GPIO.OUT)
T1 = None
T1_TIME = 1.0

def t1_action():
  GPIO.output(LED1_PORT, GPIO.LOW)

##################################################################################################

# ISO timestamp with UTC offset
def get_timestamp():
  now = datetime.datetime.now()
  utcnow = datetime.datetime.utcnow()

  delta = now - utcnow

  hh, mm = divmod((delta.days * 24 * 60 * 60 + delta.seconds + 30) / 60, 60)

  return '%s%+03d:%02d' % ( now.isoformat().rsplit('.')[0], hh, mm, )

### globals

# SmartDrill connection string
CONNECTION_STRING = ''

DRILL_DAT = '/home/pi/intershop/scripts/drill/drill.dat'
DRILL_DAT_LOCK = os.path.join(os.path.dirname(DRILL_DAT), '.' + os.path.basename(DRILL_DAT))
DRILL_DAT_LOCK = DRILL_DAT

DRILL_VAL = '/tmp/drill.val'
DRILL_VAL_LOCK = os.path.join(os.path.dirname(DRILL_VAL), '.' + os.path.basename(DRILL_VAL))
DRILL_VAL_LOCK = DRILL_VAL

# directories as lock target?

if DRILL_DAT_LOCK != DRILL_DAT and not os.path.exists(DRILL_DAT_LOCK):
  try:
    os.makedirs(DRILL_DAT_LOCK)

  except ( OSError, IOError, ):
    traceback.print_exc()
    DRILL_DAT_LOCK = DRILL_DAT

if DRILL_VAL_LOCK != DRILL_VAL and not os.path.exists(DRILL_VAL_LOCK):
  try:
    os.makedirs(DRILL_VAL_LOCK)

  except ( OSError, IOError, ):
    traceback.print_exc()
    DRILL_VAL_LOCK = DRILL_VAL

### file i/o

def map_drill_dat(lines):
  data = {}
  for line in lines:
    line = line.strip()
    if line.startswith('#'):
      continue

    t = line.split('=', 1)
    if len(t) < 2:
      continue

    key = t[0].strip().lower()
    val = t[1].strip()
    try:
      val = int(val, 10)

    except ( ValueError, ):
      try:
        val = float(val)
      
      except ( ValueError, ):
        pass

    data[key] = val

  return data

def read_drill_file(filename, lockname):
  lock = locked = f = None
  data = {}
  try:
    if lockname:
      try:
        lock = os.open(lockname, os.O_RDONLY)
        fcntl.flock(lock, fcntl.LOCK_SH)

      except ( OSError, IOError, ):
        traceback.print_exc()
        locked = False

      else:
        locked = True

    f = None
    if not lock is None and lockname == filename:
      try:
        f = os.fdopen(lock, 'r')

      except ( OSError, IOError, ):
        traceback.print_exc()

    if f is None:
      f = os.open(filename, 'r')

    data.update(map_drill_dat(f))

  except ( OSError, IOError, ):
    traceback.print_exc()
    data = None

  finally:
    try:
      if locked:
        fcntl.flock(lock, fcntl.LOCK_UN)

      if not f is None:
        if not lock is None and lock == f.fileno():
          lock = None

        f.close()

      if not lock is None:
        os.close(lock)

    except ( OSError, IOError, ):
      traceback.print_exc()

    finally:
      f = None
      
  return data

def get_drill_val():
  data = read_drill_file(DRILL_VAL, DRILL_VAL_LOCK)
  if data is None:
    return None

  data['timestamp'] = get_timestamp()
  return json.dumps(data)

DRILL_DAT_TWIN = None
DRILL_DAT_SEQ = None

def get_drill_dat():
  global DRILL_DAT_SEQ

  data = read_drill_file(DRILL_DAT, DRILL_DAT_LOCK)
  if data is None:
    return None

  if not DRILL_DAT_TWIN is None:
    reset_old = DRILL_DAT_TWIN.get('reset', None)
    if not reset_old is None:
      reset_new = data.get('reset', None)
      if not reset_new is None and reset_new < reset_old:
        return None

      data['reset'] = ( reset_new, reset_old )[ reset_new is None ]

  seq = data.pop('seq', None)
  if not seq is None:
    if not DRILL_DAT_SEQ is None:
      if seq != DRILL_DAT_SEQ:
        return None

    else:
      DRILL_DAT_SEQ = seq

  data['seq'] = None 
  return json.dumps(data)

def set_drill_dat(changes, filename = DRILL_DAT, lockname = DRILL_DAT_LOCK):
  global DRILL_DAT_SEQ

  lock = locked = f = None
  data = {}
  try:
    if lockname:
      try:
        lock = os.open(
          lockname, ( os.O_RDONLY, os.O_RDWR )[ filename == lockname ]
        )
        fcntl.flock(lock, fcntl.LOCK_EX)

      except ( OSError, IOError, ):
        traceback.print_exc()
        locked = False

    else:
      locked = True

    f = None
    if not lock is None and lockname == filename:
      try:
        f = os.fdopen(lock, 'r+')

      except ( OSError, IOError, ):
        traceback.print_exc()

    if f is None:
      f = open(filename, 'r+')

    lines = ()
    for line in f:
      line = line.rstrip()
      if line.lstrip().startswith('#'):
        lines += ( line, )
        continue

      t = line.lstrip().split('=', 1)
      if len(t) < 2:
        lines += ( line, )
        continue

      key = t[0].strip().lower()
      if key == 'seq':
        continue

      if not key in changes:
        lines += ( line, )
        continue

      m = re.search(r'^\s+', t[1])
      spc = m.group(0) if not m is None else ''
      lines += ( '%s=%s%s' % ( t[0], spc, changes[key], ), )
      changes.pop(key)

    if not DRILL_DAT_SEQ is None:
      DRILL_DAT_SEQ += 1

    else:
      DRILL_DAT_SEQ = 0

    changes['seq'] = DRILL_DAT_SEQ
    for key, val in changes.items():
      lines += ( '%s=%s' % ( key.upper(), val, ), )

    f.seek(0, os.SEEK_SET)
    for line in lines:
      f.write('%s\n' % ( line, ))

    f.truncate()      
    f.flush()

    data.update(map_drill_dat(lines))
    data.pop('seq', None)

  except ( OSError, IOError, ):
    traceback.print_exc()
    data = None

  finally:
    try:
      if locked:
        fcntl.flock(lock, fcntl.LOCK_UN)
   
      if not f is None:
        if not lock is None and lock == f.fileno():
          lock = None

        f.close()
         
      if not lock is None:
        os.close(lock)

    except ( OSError, IOError, ):
      traceback.print_exc()

    finally:
      f = None

  if data is None:
    return None

  if not DRILL_DAT_TWIN is None:
    DRILL_DAT_TWIN.update(data)

  return json.dumps(data)

### azure i/o

# send IoT event, keep current message

DRILL_VAL_JSON = None

# called if message was processed or timed out
# resend on timeout
def send_confirmation_callback(message, result, client):
    global DRILL_VAL_JSON

    print ( "Confirmation received for message with result = %s" % (result) )
    map_properties = message.properties()
    print ( "    message_id: %s" % message.message_id )
    print ( "    correlation_id: %s" % message.correlation_id )
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )

    if result == iothub_client.IoTHubClientConfirmationResult.OK:
      DRILL_VAL_JSON = None

    elif DRILL_VAL_JSON:
      send_drill_val(client, DRILL_VAL_JSON)

def send_drill_val(client, data):
  global T1, T1_TIME

  if client.get_send_status() != iothub_client.IoTHubClientStatus.IDLE:
    return

  if client.DEBUG:
    print >> sys.stderr, os.linesep.join(( 
      l.rstrip() 
      for l in json.dumps(json.loads(data), indent = 4, sort_keys = True).splitlines()
    ))

  client.send_event_async(
    iothub_client.IoTHubMessage(data), send_confirmation_callback, client
  )
  try:
    # Puls Azure LED
    GPIO.output(LED1_PORT, GPIO.HIGH)
    T1 = threading.Timer(T1_TIME, t1_action)
    T1.start()

  except:
    traceback.print_exc()

DRILL_VAL_JSON_LAST = None

def do_drill_val(client):
  global DRILL_VAL_JSON, DRILL_VAL_JSON_LAST

  data = get_drill_val()
  if data and data != DRILL_VAL_JSON_LAST:
    print >> sys.stderr, DRILL_VAL
    DRILL_VAL_JSON_LAST = DRILL_VAL_JSON = data
    send_drill_val(client, data)

# send IoT device twin update, keep current local status

DRILL_DAT_JSON = None

def send_drill_dat(client, data):
  global T1, T1_TIME

  if client.DEBUG:
    print >> sys.stderr, os.linesep.join(( 
      l.rstrip() 
      for l in json.dumps(json.loads(data), indent = 4, sort_keys = True).splitlines()
    ))

  client.send_reported_state(
    data, len(data), send_reported_state_callback, client
  )
  try:
    # Puls Azure LED
    GPIO.output(LED1_PORT, GPIO.HIGH)
    T1 = threading.Timer(T1_TIME, t1_action)
    T1.start()

  except:
    traceback.print_exc()

DRILL_DAT_JSON_LAST = None

def do_drill_dat(client, data = None):
  global DRILL_DAT_JSON, DRILL_DAT_JSON_LAST

  if data is None:
    data = get_drill_dat()

  if data and data != DRILL_DAT_JSON_LAST:
    print >> sys.stderr, DRILL_DAT
    DRILL_DAT_JSON_LAST = DRILL_DAT_JSON = data
    send_drill_dat(client, data)

# from iothub device sample
def receive_message_callback(message, client):
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    return iothub_client.IoTHubMessageDispositionResult.ACCEPTED

# called if reported state was received
# might handle status code (status_code = 400 seems ok?)
def send_reported_state_callback(status_code, client):
    global DRILL_DAT_JSON

    print ( "Confirmation for reported state received with:\nstatus_code = [%d]" % (status_code) )
    DRILL_DAT_JSON = None

# called upon connection, try to send current outstanding updates
def device_twin_callback(update_state, payload, client):
    global DRILL_DAT_TWIN

    print ( "\nTwin callback called with:\nupdateStatus = %s" % (update_state) )
    data = json.loads(payload)
    if client.DEBUG:
      print >> sys.stderr, os.linesep.join(( 
        l.rstrip() 
        for l in json.dumps(data, indent = 4, sort_keys = True).splitlines()
      ))

    desired = None
    if update_state == iothub_client.IoTHubTwinUpdateState.COMPLETE:
      if DRILL_DAT_JSON:
        send_drill_dat(client, DRILL_DAT_JSON)

      if DRILL_VAL_JSON:
        send_drill_val(client, DRILL_VAL_JSON)

      DRILL_DAT_TWIN = data['reported']
      desired = data['desired']

    elif update_state == iothub_client.IoTHubTwinUpdateState.PARTIAL:
      desired = data

    if desired:
      changes = {}
      for key in ( 'reset', 'mode', 'lock_cloud', 'lock_local', 'gps_latitude', 'gps_longitude', ):
        desired_val = desired.get(key, None)
        if desired_val is None:
          continue

        reported_val = DRILL_DAT_TWIN.get(key, None)
        if desired_val != reported_val:
          changes[key] = desired_val

      if changes:
        if 'reset' in changes:
          for mode in ( 1, 2, 3, ):
            changes['usage_time_mode_%u' % ( mode, )] = 0
            try:
              # Reset Mode
              #subprocess.call(('' % ( mode, ), '', ))
              pass
              
            except:
              import traceback; traceback.print_exc()

        data = set_drill_dat(changes)
        do_drill_dat(client, data)

def init_client(debug):
  client = iothub_client.IoTHubClient(
    CONNECTION_STRING, iothub_client.IoTHubTransportProvider.MQTT
  )
  # messageTimeout - the maximum time in milliseconds until a message times out.
  # The timeout period starts at IoTHubClient.send_event_async.
  # By default, messages do not expire.
  MESSAGE_TIMEOUT = 5000
  # set the time until a message times out
  client.set_option("messageTimeout", MESSAGE_TIMEOUT)

  # to enable MQTT logging set to 1
  client.set_option("logtrace", int(bool(debug)))

  client.set_message_callback(receive_message_callback, client)
  client.set_device_twin_callback(device_twin_callback, client)

  client.DEBUG = debug
  return client

# main loop, wait for file changes, send updates
def main():
  def usage():
    sys.stderr.write('%s [--debug]\n' % (
      os.path.basename(sys.argv[0]),
    ))

  import getopt
  
  try:
    opts, args = getopt.gnu_getopt(
      sys.argv[1:], '', ( 'debug', )
    )

    opts = dict(opts)

    ( debug, ) = (
      k in opts for k in ( '--debug', )
    )

  except ( getopt.GetoptError, ):
    usage()
    return 2

  i = inotify.adapters.Inotify()
  i.add_watch(os.path.dirname(DRILL_DAT))
  i.add_watch(os.path.dirname(DRILL_VAL))
  try:
    while True:
      client = init_client(debug)
      try:
        # send initial messages
        do_drill_val(client)
        do_drill_dat(client)

        # look for file changes 
        for event in i.event_gen():
          if event is None or not event[3]:
            continue

          fn = os.path.join(event[2], event[3])
          if not fn in ( DRILL_VAL, DRILL_DAT, ):
            continue

          hdr = event[0]
          if hdr.mask & (
               inotify.constants.IN_CLOSE_WRITE | 
               inotify.constants.IN_MOVED_TO      # sed -i moves to
          ):
            if fn == DRILL_VAL:
              do_drill_val(client)

            elif fn == DRILL_DAT:
              do_drill_dat(client)

      except ( iothub_client.IoTHubClientError, ):
        traceback.print_exc()

      except ( KeyboardInterrupt, ):
        break

      finally:
        del(client)
        client = None

  finally:
    i.remove_watch(os.path.dirname(DRILL_VAL))
    i.remove_watch(os.path.dirname(DRILL_DAT))

sys.exit(main())