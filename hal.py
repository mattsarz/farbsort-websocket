import datetime


class HAL_base(object):
  MOTOR_PIN = "P8_11"
  COMPRESSOR_PIN = "P8_13"
  VALVE1_PIN = "P8_12"
  VALVE2_PIN = "P9_25"
  VALVE3_PIN = "P9_27"
  PULSECOUNTER_PIN = "P8_15"
  LIGHTBARRIER1_PIN = "P8_16"
  LIGHTBARRIER2_PIN = "P9_24"
  LIGHTBARRIER3_PIN = "P8_14"
  LIGHTBARRIER4_PIN = "P8_17"
  LIGHTBARRIER5_PIN = "P8_19"

  def __init__(self, verbose=False):
    self._verbose = verbose
    if self._verbose:
      print "init HAL..."
    self._output_values = {}
    self._last_input_values = {}
    self._on_input_change_callback_func = None
    self._analog_input_values = {}

  def _handle_input_change(self, pin, value):
    last_value = self._last_input_values.get(pin, None)
    self._last_input_values[pin] = value
    if value != last_value:
      if self._verbose:
        print "input %s changed: %s -> %s..." % (pin, last_value, value)
      if self._on_input_change_callback_func:
        if self._verbose:
          print "calling callback..."
        self._on_input_change_callback_func(pin, value, last_value)
      else:
        if self._verbose:
          print "no callback"
    return value

  def register_on_input_change_callback(self, func):
    self._on_input_change_callback_func = func

  def set_output(self, pin, value):
    now = datetime.datetime.now()
    if self._verbose:
      print "%s: setting %s to %s" % (now.isoformat(), pin, value)
    self._output_values[pin] = value

  def get_output(self, pin):
    return self._output_values.get(pin, None)


class HAL(HAL_base):
  def __init__(self, **kwargs):
    super(HAL, self).__init__(**kwargs)
    global GPIO
    import Adafruit_BBIO.GPIO as GPIO
    GPIO.setup(self.MOTOR_PIN, GPIO.OUT)
    GPIO.setup(self.COMPRESSOR_PIN, GPIO.OUT)
    GPIO.setup(self.VALVE1_PIN, GPIO.OUT)
    GPIO.setup(self.VALVE2_PIN, GPIO.OUT)
    GPIO.setup(self.VALVE3_PIN, GPIO.OUT)
    GPIO.setup(self.PULSECOUNTER_PIN, GPIO.IN)
    GPIO.setup(self.LIGHTBARRIER1_PIN, GPIO.IN)
    GPIO.setup(self.LIGHTBARRIER2_PIN, GPIO.IN)
    GPIO.setup(self.LIGHTBARRIER3_PIN, GPIO.IN)
    GPIO.setup(self.LIGHTBARRIER4_PIN, GPIO.IN)
    GPIO.setup(self.LIGHTBARRIER5_PIN, GPIO.IN)
    global ADC
    import Adafruit_BBIO.ADC as ADC
    ADC.setup()

  def get_input(self, pin):
    value = GPIO.input(pin)
    self._handle_input_change(pin, value)
    return value

  def set_output(self, pin, value):
    super(HAL, self).set_output(pin, value)
    GPIO.output(pin, value)

  def get_analog_input(self, pin):
    return ADC.read_raw(pin)


class HAL_simulated(HAL_base):
  def __init__(self, **kwargs):
    super(HAL_simulated, self).__init__(**kwargs)
    self._input_values = {}

  def set_input(self, pin, value):
    self._input_values[pin] = value

  def get_input(self, pin):
    value = self._input_values.get(pin, None)
    self._handle_input_change(pin, value)
    return value

  def set_analog_input(self, pin, value):
    self._analog_input_values[pin] = value

  def get_analog_input(self, pin):
    return self._analog_input_values.get(pin, None)
