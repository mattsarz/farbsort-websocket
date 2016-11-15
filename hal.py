import datetime
import logging


class Pin(object):
  DIRECTION_INPUT = "input"
  DIRECTION_OUTPUT = "output"
  def __init__(self, name, pad, direction=None):
    self._name = name
    self._pad = pad
    self._direction = direction

  @property
  def name(self):
    return self._name

  @property
  def pad(self):
    return self._pad

  @property
  def direction(self):
    return self._direction

  def __str__(self):
    return self._name

class InputPin(Pin):
  def __init__(self, name, pad):
    super(InputPin, self).__init__(name, pad, direction=Pin.DIRECTION_INPUT)


class OutputPin(Pin):
  def __init__(self, name, pad):
    super(OutputPin, self).__init__(name, pad, direction=Pin.DIRECTION_OUTPUT)


class HAL_base(object):
  MOTOR = OutputPin("motor", "P8_11")
  COMPRESSOR = OutputPin("compressor", "P8_13")
  VALVE1 = OutputPin("valve1", "P8_12")
  VALVE2 = OutputPin("valve2", "P9_25")
  VALVE3 = OutputPin("valve3", "P9_27")
  PULSECOUNTER = InputPin("pulsecounter", "P8_15")
  LIGHTBARRIER1 = InputPin("lightbarrier1", "P8_16")
  LIGHTBARRIER2 = InputPin("lightbarrier2", "P9_24")
  LIGHTBARRIER3 = InputPin("lightbarrier3", "P8_14")
  LIGHTBARRIER4 = InputPin("lightbarrier4", "P8_17")
  LIGHTBARRIER5 = InputPin("lightbarrier5", "P8_19")

  def __init__(self):
    self._logger = logging.getLogger(self.__class__.__name__)
    self._logger.debug("init")
    self._output_values = {}
    self._last_input_values = {}
    self._on_input_change_callback_func = None

  def _handle_input_change(self, pin, value):
    last_value = self._last_input_values.get(pin, None)
    self._last_input_values[pin] = value
    if value != last_value:
      self._logger.debug("input {} changed: {} -> {}...".format(pin, last_value, value))
      if self._on_input_change_callback_func:
        self._logger.debug("calling callback...")
        self._on_input_change_callback_func(pin, value, last_value)
      else:
        self._logger.debug("no callback")
    return value

  def register_on_input_change_callback(self, func):
    self._on_input_change_callback_func = func

  def set_output(self, pin, value):
    now = datetime.datetime.now()
    self._logger.debug("{}: setting {} to {}".format(now.isoformat(), pin, value))
    self._output_values[pin] = value

  def get_output(self, pin):
    return self._output_values.get(pin, None)


class HAL(HAL_base):
  def __init__(self, **kwargs):
    super(HAL, self).__init__(**kwargs)
    global GPIO
    import Adafruit_BBIO.GPIO as GPIO
    self._setup_pin(self.MOTOR)
    self._setup_pin(self.COMPRESSOR)
    self._setup_pin(self.VALVE1)
    self._setup_pin(self.VALVE2)
    self._setup_pin(self.VALVE3)
    self._setup_pin(self.PULSECOUNTER)
    self._setup_pin(self.LIGHTBARRIER1)
    self._setup_pin(self.LIGHTBARRIER2)
    self._setup_pin(self.LIGHTBARRIER3)
    self._setup_pin(self.LIGHTBARRIER4)
    self._setup_pin(self.LIGHTBARRIER5)

  def _setup_pin(self, pin):
    direction = GPIO.IN
    if pin.direction == Pin.DIRECTION_OUTPUT:
      direction = GPIO.OUT
    GPIO.setup(pin.pad, direction)

  def get_input(self, pin):
    value = GPIO.input(pin.pad)
    self._handle_input_change(pin, value)
    return value

  def set_output(self, pin, value):
    super(HAL, self).set_output(pin, value)
    GPIO.output(pin.pad, value)


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
