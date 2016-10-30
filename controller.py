import datetime

import Adafruit_BBIO.GPIO as GPIO

from color_detector import ColorDetector


class Controller(object):
  _MOTOR = "P8_11"
  _COMPRESSOR = "P8_13"
  _VALVE1 = "P8_12"
  _VALVE2 = "P9_25"
  _VALVE3 = "P9_27"
  _PULSECOUNTER = "P8_15"
  _LIGHTBARRIER1 = "P8_16"
  _LIGHTBARRIER2 = "P9_24"
  _LIGHTBARRIER3 = "P8_14"
  _LIGHTBARRIER4 = "P8_17"
  _LIGHTBARRIER5 = "P8_19"
  _PULSECOUNTER_LAST_CHANGE_TO_TIMEOUT_IN_SECONDS = 1.0

  def __init__(self):
    print "Controller.init()..."
    self._current_output_values = dict()
    self._input_values = dict()
    self._last_input_values = dict()
    GPIO.setup(self._MOTOR, GPIO.OUT)
    self.motor = GPIO.LOW
    self._conveyor_running = False
    print "conveyor=stopped"
    GPIO.setup(self._COMPRESSOR, GPIO.OUT)
    self.compressor = GPIO.LOW
    GPIO.setup(self._VALVE1, GPIO.OUT)
    self.valve1 = GPIO.LOW
    GPIO.setup(self._VALVE2, GPIO.OUT)
    self.valve2 = GPIO.LOW
    GPIO.setup(self._VALVE3, GPIO.OUT)
    self.valve3 = GPIO.LOW
    GPIO.setup(self._PULSECOUNTER, GPIO.IN)
    self._pulsecounter = 0
    GPIO.setup(self._LIGHTBARRIER1, GPIO.IN)
    self._color_detector = ColorDetector(debug=True)
    GPIO.setup(self._LIGHTBARRIER2, GPIO.IN)
    GPIO.setup(self._LIGHTBARRIER3, GPIO.IN)
    GPIO.setup(self._LIGHTBARRIER4, GPIO.IN)
    GPIO.setup(self._LIGHTBARRIER5, GPIO.IN)
    self._start_timestamps = []
    self._scheduled_colordetect_timestamps = []
    self._scheduled_pusher_actions = []

  def on_poll(self):
    #print "polling..."
    self._get_input(self._PULSECOUNTER)
    if self._conveyor_running:
      seconds_since_last_change = datetime.datetime.now() - self._pulsecounter_last_change
      if seconds_since_last_change.total_seconds() > self._PULSECOUNTER_LAST_CHANGE_TO_TIMEOUT_IN_SECONDS:
        self._conveyor_running = False
        print "conveyor=stopped"
    self._get_input(self._LIGHTBARRIER1)
    self._get_input(self._LIGHTBARRIER2)
    self._get_input(self._LIGHTBARRIER3)
    self._get_input(self._LIGHTBARRIER4)
    self._get_input(self._LIGHTBARRIER5)

    self._check_scheduled_colordetector_actions()
    self._check_scheduled_pusher_actions()

  @property
  def motor(self):
    return self._current_output_values.get(self._MOTOR, None)

  @motor.setter
  def motor(self, value):
    return self._set_output(self._MOTOR, value)

  @property
  def compressor(self):
    return self._current_output_values.get(self._COMPRESSOR, None)

  @compressor.setter
  def compressor(self, value):
    return self._set_output(self._COMPRESSOR, value)

  @property
  def valve1(self):
    return self._current_output_values.get(self._VALVE1, None)

  @valve1.setter
  def valve1(self, value):
    return self._set_output(self._VALVE1, value)

  @property
  def valve2(self):
    return self._current_output_values.get(self._VALVE2, None)

  @valve2.setter
  def valve2(self, value):
    return self._set_output(self._VALVE2, value)

  @property
  def valve3(self):
    return self._current_output_values.get(self._VALVE3, None)

  @valve3.setter
  def valve3(self, value):
    return self._set_output(self._VALVE3, value)

  def _set_output(self, pin, value):
    last_value = self._current_output_values.get(pin, None)
    now = datetime.datetime.now()
    #print "%s: pin %s changed: %s -> %s" % (now.isoformat(), pin, last_value, value)
    GPIO.output(pin, value)
    self._current_output_values[pin] = value

  @property
  def pulsecounter(self):
    return self._pulsecounter

  @property
  def conveyor(self):
    return self._conveyor_running

  @property
  def lightbarrier1(self):
    return self._get_input(self._LIGHTBARRIER1)

  @property
  def lightbarrier2(self):
    return self._get_input(self._LIGHTBARRIER2)

  def _get_input(self, pin):
    last_value = self._last_input_values[pin] = self._input_values.get(
      pin, None)
    value = GPIO.input(pin)
    if value != last_value:
      self._on_input_change(pin, value, last_value)
      self._input_values[pin] = value
    return value

  def _on_input_change(self, pin, value, last_value):
    now = datetime.datetime.now()
    if pin == self._PULSECOUNTER:
      if last_value is None:
        return
      self._pulsecounter += 1
      #print "%s: pulsecounter=%u" % (now.isoformat(), self.pulsecounter)
      self._pulsecounter_last_change = now
      if not self._conveyor_running:
        self._conveyor_running = True
        print "conveyor=running"
      return

    print "%s: pin %s changed: %s -> %s" % (
      now.isoformat(), pin, last_value, value)

    if pin == self._LIGHTBARRIER1:
      if last_value == GPIO.LOW and value == GPIO.HIGH:
        self._start_timestamps.append(now)
      if last_value == GPIO.HIGH and value == GPIO.LOW:
        color_detect_timestamp = now + datetime.timedelta(seconds=1.215)
        self._scheduled_colordetect_timestamps.append(color_detect_timestamp)
        self._scheduled_colordetect_timestamps.sort()
    elif pin == self._LIGHTBARRIER2:
      if last_value == GPIO.HIGH and value == GPIO.LOW:
        self._pulsecounter = 0
        print "pulsecounter=%u" % self.pulsecounter
      elif last_value == GPIO.LOW and value == GPIO.HIGH:
        try:
          start_timestamp = self._start_timestamps.pop(0)
          duration = now - start_timestamp
          print "object took %s between LB1 and LB2" % duration
        except IndexError:
          print "Hoppla, no corresponding start timestamp found."

        #push_begin_timestamp = now + datetime.timedelta(seconds=.690)
        #push_begin_timestamp = now + datetime.timedelta(seconds=1.662)
        push_begin_timestamp = now + datetime.timedelta(seconds=2.741)
        self._scheduled_pusher_actions.append((push_begin_timestamp, GPIO.HIGH))
        push_end_timestamp = push_begin_timestamp + datetime.timedelta(seconds=.3)
        self._scheduled_pusher_actions.append((push_end_timestamp, GPIO.LOW))
        self._scheduled_pusher_actions.sort()

  def _check_scheduled_pusher_actions(self):
    try:
      timeout, value = self._scheduled_pusher_actions[0]
      now = datetime.datetime.now()
      if timeout <= now:
        print "%s: Timeout -> push" % now.isoformat()
        #self.valve1 = value
        #self.valve2 = value
        self.valve3 = value
        del self._scheduled_pusher_actions[0]
    except IndexError:
      pass

  def _check_scheduled_colordetector_actions(self):
    try:
      timeout = self._scheduled_colordetect_timestamps[0]
      now = datetime.datetime.now()
      if timeout <= now:
        print "%s: Timeout -> color-detect" % now.isoformat()
        self._color_detector.poll()
        del self._scheduled_colordetect_timestamps[0]
    except IndexError:
      pass

  def __del__(self):
    print "Controller.delete()..."
    self.motor = GPIO.LOW
    self.compressor = GPIO.LOW
