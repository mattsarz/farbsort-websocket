import datetime

class ADC(object):
  _STATE_IDLE = 1
  _STATE_DESCEND = 2
  _STATE_ASCEND = 3
  _LIMIT_TOLERANCE = 20
  _NO_OBJECT_LIMIT = 1228 - _LIMIT_TOLERANCE
  _BLUE_OBJECT_LIMIT = 1199 + _LIMIT_TOLERANCE
  _RED_OBJECT_LIMIT = 908 + _LIMIT_TOLERANCE
  _WHITE_OBJECT_LIMIT = 862 + _LIMIT_TOLERANCE

  def __init__(self, debug=False):
    self._debug = debug
    self._last_adc_value = None
    self._state = None
    self._last_state = None

  def poll(self):
    adc_value = self.raw_value()
    if self._last_adc_value is None:
      self.eval_state(adc_value)
      self.eval_object_color(adc_value)
      self._last_state = self._state
    self._last_adc_value = adc_value

  def eval_state(self, adc_value):
    if adc_value >= self._NO_OBJECT_LIMIT:
      if self._state != self._STATE_IDLE:
        print "adc: state=idle"
      self._state = self._STATE_IDLE
    elif adc_value <= self._last_adc_value:
      if self._state != self._STATE_DESCEND:
        print "adc: state=descend"
      self._state = self._STATE_DESCEND
    else:
      if self._state != self._STATE_ASCEND:
        print "adc: state=ascend"
      self._state = self._STATE_ASCEND

  def eval_object_color(self, adc_value):
      if ((self._state == self._STATE_ASCEND) and
          (self._last_state == self._STATE_DESCEND)):
        if self._last_adc_value < self._WHITE_OBJECT_LIMIT:
          print "adc: Got WHITE object"
        elif self._last_adc_value < self._RED_OBJECT_LIMIT:
          print "adc: Got RED object"
        elif self._last_adc_value < self._BLUE_OBJECT_LIMIT:
          print "adc: Got BLUE object"

  def raw_value(self):
    with open("/sys/bus/iio/devices/iio:device0/in_voltage0_raw") as f:
      adc_value = int(f.read())
      if self._debug:
        print "adc: AIN0=%u" % adc_value
      return adc_value
