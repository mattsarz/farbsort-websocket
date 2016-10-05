import datetime
import time

import Adafruit_BBIO.GPIO as GPIO
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web


CONVEYOR = "P8.11"
LIGHTBARRIER1 = "P8.16"
LIGHTBARRIER2 = "P9.24"

POLLING_INTERVAL_1000ms = 1000
WEBSOCKET_PORT = 8888


class Controller(object):
  def __init__(self):
    self._current_output_values = dict()
    self._last_input_values = dict()
    GPIO.setup(CONVEYOR, GPIO.OUT)
    self._set_output(CONVEYOR, False)
    GPIO.setup(LIGHTBARRIER1, GPIO.IN)
    GPIO.setup(LIGHTBARRIER2, GPIO.IN)

  def on_poll(self):
    print "polling..."
    self._get_input(LIGHTBARRIER1)
    self._get_input(LIGHTBARRIER2)

  @property
  def conveyor(self):
    return self._current_output_values[CONVEYOR]

  @conveyor.setter
  def conveyor(self, value):
    return self._set_output(CONVEYOR, value)

  def _set_output(self, pin, value):
    self._current_output_values[pin] = value
    output_value = GPIO.HIGH if value else GPIO.LOW
    GPIO.output(pin, output_value)

  @property
  def lightbarrier1(self):
    return self._get_input(LIGHTBARRIER1)

  @property
  def lightbarrier2(self):
    return self._get_input(LIGHTBARRIER2)

  def _get_input(self, pin):
    now = datetime.datetime.now()
    value = GPIO.input(pin)
    last_value = self._last_input_values.get(pin, None)
    if value != last_value:
      print "%s: pin %s changed: %s -> %s" % (now.isoformat(), pin, last_value, value)
      self._last_input_values[pin] = value
    return value

  def __del__(self):
    self._set_output(CONVEYOR, False)


class WSHandler(tornado.websocket.WebSocketHandler):
  def initialize(self, controller):
    self._controller = controller

  def open(self):
    print "new connection opened"
    self.write_message("Welcome to farbsort control!")

  def on_message(self, message):
    print "Got:", message

    if message == "start":
      if self._controller.conveyor:
        print "conveyor is already started"
      else:
        print "starting..."
        self.write_message("starting")
        self._controller.conveyor = GPIO.HIGH
      print "started"
      self.write_message("started")
    elif message == 'stop':
      if not self._controller.conveyor:
        print "conveyor is already stopped"
      else:
        print "stopping..."
        self.write_message("stopping")
        self._controller.conveyor = GPIO.LOW
      print "stopped"
      self.write_message("stopped")

  def on_close(self):
    print 'Connection was closed...'
    self._controller.conveyor = GPIO.LOW

  def check_origin(self, origin):
    return True


if __name__ == "__main__":
  controller = Controller()
  application = tornado.web.Application([
    (r'/ws', WSHandler, dict(controller=controller)),
  ])
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(WEBSOCKET_PORT)
  periodicOneSecTimer = tornado.ioloop.PeriodicCallback(controller.on_poll, POLLING_INTERVAL_1000ms)
  periodicOneSecTimer.start()
  tornado.ioloop.IOLoop.instance().start()
