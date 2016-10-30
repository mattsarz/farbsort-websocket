import datetime
import logging
import Queue

from color_detector import ColorDetector


class Controller(object):
  MODE_NORMAL = 0
  MODE_DIAGNOSTIC = 1
  VALID_CONTROLLER_MODES = (MODE_NORMAL, MODE_DIAGNOSTIC)
  PULSECOUNTER_LAST_CHANGE_TO_TIMEOUT_IN_SECONDS = 1.0

  def __init__(self, hal, verbose=False):
    self._setup_logging(verbose)
    self._logger.debug("init")
    self._hal = hal
    self.mode = self.MODE_DIAGNOSTIC
    self.motor = False
    self._conveyor_running = False
    print "conveyor=stopped"
    self.compressor = False
    self.valve1 = False
    self.valve2 = False
    self.valve3 = False
    self._pulsecounter = 0
    self._color_detector = ColorDetector(hal=hal)
    self._start_timestamps = []
    self._scheduled_colordetect_timestamps = []
    self._scheduled_pusher_actions = []
    self._hal.register_on_input_change_callback(self._on_input_change)
    self._status_queue = Queue.Queue()

  def _setup_logging(self, verbose):
    logging_level = logging.INFO
    if verbose:
      logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level)
    self._logger = logging.getLogger(self.__class__.__name__)

  def on_poll(self):
    self._hal.get_input(self._hal.PULSECOUNTER_PIN)
    if self._conveyor_running:
      seconds_since_last_change = datetime.datetime.now() - self._pulsecounter_last_change
      if seconds_since_last_change.total_seconds() > self.PULSECOUNTER_LAST_CHANGE_TO_TIMEOUT_IN_SECONDS:
        self._conveyor_running = False
        print "conveyor=stopped"
    self._hal.get_input(self._hal.LIGHTBARRIER1_PIN)
    self._hal.get_input(self._hal.LIGHTBARRIER2_PIN)
    self._hal.get_input(self._hal.LIGHTBARRIER3_PIN)
    self._hal.get_input(self._hal.LIGHTBARRIER4_PIN)
    self._hal.get_input(self._hal.LIGHTBARRIER5_PIN)

    self._check_scheduled_colordetector_actions()
    self._check_scheduled_pusher_actions()

  @property
  def mode(self):
    return self._mode

  @mode.setter
  def mode(self, value):
    if value not in self.VALID_CONTROLLER_MODES:
      raise ValueError("invalid mode")
    self._mode = value

  @property
  def motor(self):
    return self._hal.get_output(self._hal.MOTOR_PIN)

  @motor.setter
  def motor(self, value):
    return self._hal.set_output(self._hal.MOTOR_PIN, value)

  @property
  def compressor(self):
    return self._hal.get_output(self._hal.COMPRESSOR_PIN)

  @compressor.setter
  def compressor(self, value):
    return self._hal.set_output(self._hal.COMPRESSOR_PIN, value)

  @property
  def valve1(self):
    return self._hal.get_output(self._hal.VALVE1_PIN)

  @valve1.setter
  def valve1(self, value):
    return self._hal.set_output(self._hal.VALVE1_PIN, value)

  @property
  def valve2(self):
    return self._hal.get_output(self._hal.VALVE2_PIN)

  @valve2.setter
  def valve2(self, value):
    return self._hal.set_output(self._hal.VALVE2_PIN, value)

  @property
  def valve3(self):
    return self._hal.get_output(self._hal.VALVE3_PIN)

  @valve3.setter
  def valve3(self, value):
    return self._hal.set_output(self._hal.VALVE3_PIN, value)

  @property
  def pulsecounter(self):
    return self._pulsecounter

  @property
  def conveyor(self):
    return self._conveyor_running

  @property
  def lightbarrier1(self):
    return self._hal.get_input(self._hal.LIGHTBARRIER1_PIN)

  @property
  def lightbarrier2(self):
    return self._hal.get_input(self._hal.LIGHTBARRIER2_PIN)

  @property
  def lightbarrier3(self):
    return self._hal.get_input(self._hal.LIGHTBARRIER3_PIN)

  @property
  def lightbarrier4(self):
    return self._hal.get_input(self._hal.LIGHTBARRIER4_PIN)

  @property
  def lightbarrier5(self):
    return self._hal.get_input(self._hal.LIGHTBARRIER5_PIN)

  def _on_input_change(self, pin, value, last_value):
    now = datetime.datetime.now()
    if pin == self._hal.PULSECOUNTER_PIN:
      if last_value is None:
        return
      self._pulsecounter += 1
      self._logger.debug("pulsecounter=%u" % self.pulsecounter)
      self._pulsecounter_last_change = now
      if not self._conveyor_running:
        self._conveyor_running = True
        print "conveyor=running"
      return

    display_value = "off"
    if value:
      display_value = "on"
    print "%s=%s" % (pin, value)
    display_last_value = "off"
    if last_value:
      display_last_value = "on"
    print "%s=%s" % (pin, value)
    self._logger.debug("pin %s changed: %s -> %s" % (pin, last_value, value))

    if pin == self._hal.LIGHTBARRIER1_PIN:
      if last_value == False and value == True:
        self._start_timestamps.append(now)
      if last_value == True and value == False:
        color_detect_timestamp = now + datetime.timedelta(seconds=1.215)
        self._scheduled_colordetect_timestamps.append(color_detect_timestamp)
        self._scheduled_colordetect_timestamps.sort()
    elif pin == self._hal.LIGHTBARRIER2_PIN:
      if last_value == True and value == False:
        self._pulsecounter = 0
        print "pulsecounter=%u" % self.pulsecounter
      elif last_value == False and value == True:
        try:
          start_timestamp = self._start_timestamps.pop(0)
          duration = now - start_timestamp
          self._logger.debug("object took %s between LB1 and LB2" % duration)
        except IndexError:
          self._logger.exception(
            "Hoppla, no corresponding start timestamp found.")

        #push_begin_timestamp = now + datetime.timedelta(seconds=.690)
        #push_begin_timestamp = now + datetime.timedelta(seconds=1.662)
        push_begin_timestamp = now + datetime.timedelta(seconds=2.741)
        self._scheduled_pusher_actions.append((push_begin_timestamp, True))
        push_end_timestamp = push_begin_timestamp + datetime.timedelta(seconds=.3)
        self._scheduled_pusher_actions.append((push_end_timestamp, False))
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
    self._logger.debug("delete")
    self.motor = False
    self.compressor = False
    self.valve1 = False
    self.valve2 = False
    self.valve3 = False
