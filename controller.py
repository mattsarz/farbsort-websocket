import datetime

import Adafruit_BBIO.GPIO as GPIO

from color_detector import ColorDetector


class Controller(object):
  _CONVEYOR = "P8_11"
  _COMPRESSOR = "P8_13"
  _VALVE1 = "P8_12"
  _VALVE2 = "P9_25"
  _VALVE3 = "P9_27"
  _PULSECOUNTER = "P8_15"
  _LIGHTBARRIER1 = "P8_16"
  _LIGHTBARRIER2 = "P9_24"

  def __init__(self):
    print "Controller.init()..."
    self._current_output_values = dict()
    self._last_input_values = dict()
    GPIO.setup(self._CONVEYOR, GPIO.OUT)
    self.conveyor = GPIO.HIGH
    GPIO.setup(self._COMPRESSOR, GPIO.OUT)
    self.compressor = GPIO.LOW
    GPIO.setup(self._VALVE1, GPIO.OUT)
    self.valve1 = GPIO.LOW
    GPIO.setup(self._VALVE2, GPIO.OUT)
    self.valve2 = GPIO.LOW
    GPIO.setup(self._VALVE3, GPIO.OUT)
    self.valve3 = GPIO.LOW
    GPIO.setup(self._PULSECOUNTER, GPIO.IN)
    GPIO.setup(self._LIGHTBARRIER1, GPIO.IN)
    GPIO.setup(self._LIGHTBARRIER2, GPIO.IN)
    self._color_detector = ColorDetector(debug=False)

  def on_poll(self):
    #print "polling..."
    self._get_input(self._PULSECOUNTER)
    self._get_input(self._LIGHTBARRIER1)
    self._get_input(self._LIGHTBARRIER2)
    self._color_detector.poll()

  @property
  def conveyor(self):
    return self._current_output_values.get(self._CONVEYOR, None)

  @conveyor.setter
  def conveyor(self, value):
    return self._set_output(self._CONVEYOR, value)

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
  def lightbarrier1(self):
    return self._get_input(self._LIGHTBARRIER1)

  @property
  def lightbarrier2(self):
    return self._get_input(self._LIGHTBARRIER2)

  def _get_input(self, pin):
    now = datetime.datetime.now()
    value = GPIO.input(pin)
    last_value = self._last_input_values.get(pin, None)
    if value != last_value:
      #print "%s: pin %s changed: %s -> %s" % (now.isoformat(), pin, last_value, value)
      self._last_input_values[pin] = value
    return value

  def __del__(self):
    print "Controller.delete()..."
    self.conveyor = GPIO.LOW
    self.compressor = GPIO.LOW
