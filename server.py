import time

import Adafruit_BBIO.GPIO as GPIO
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

from controller import Controller


POLLING_INTERVAL_IN_MS = 100
VALVE_ON_TIME_IN_SECS = .3
WEBSOCKET_PORT = 8888


class WSHandler(tornado.websocket.WebSocketHandler):
  def initialize(self, controller):
    self._controller = controller

  def open(self):
    print "new connection opened"
    self.write_message("Welcome to farbsort control!")

  def on_message(self, message):
    print "Got:", message

    if message == "conveyor.start":
      if self._controller.conveyor:
        print "conveyor is already started"
      else:
        print "starting..."
        self.write_message("starting")
        self._controller.conveyor = GPIO.HIGH
      print "started"
      self.write_message("started")
    elif message == "conveyor.stop":
      if not self._controller.conveyor:
        print "conveyor is already stopped"
      else:
        print "stopping..."
        self.write_message("stopping")
        self._controller.conveyor = GPIO.LOW
      print "stopped"
      self.write_message("stopped")
    elif message == "valve1":
        print "valve1.on..."
        self._controller.valve1 = GPIO.HIGH
        time.sleep(VALVE_ON_TIME_IN_SECS)
        print "valve1.off..."
        self._controller.valve1 = GPIO.LOW
    elif message == "valve2":
        print "valve1.on..."
        self._controller.valve2 = GPIO.HIGH
        time.sleep(VALVE_ON_TIME_IN_SECS)
        print "valve1.off..."
        self._controller.valve2 = GPIO.LOW
    elif message == "valve3":
        print "valve3.on..."
        self._controller.valve3 = GPIO.HIGH
        time.sleep(VALVE_ON_TIME_IN_SECS)
        print "valve3.off..."
        self._controller.valve3 = GPIO.LOW
    elif message == "compressor.start":
      if self._controller.compressor:
        print "compressor is already started"
      else:
        print "starting compressor..."
        self._controller.compressor = GPIO.HIGH
      print "compressor started"
    elif message == "compressor.stop":
      if not self._controller.compressor:
        print "compressor is already stopped"
      else:
        print "stopping compressor..."
        self._controller.compressor = GPIO.LOW
      print "compressor stopped"

  def on_close(self):
    print "Connection was closed..."

  def check_origin(self, origin):
    return True

  def __del__(self):
    print "WSHandler.__del__()..."


if __name__ == "__main__":
  import getpass
  import signal
  import sys

  if getpass.getuser() != "root":
    print >> sys.stderr, "run as root"
    sys.exit(1)

  controller = Controller()

  application = tornado.web.Application([
    (r"/ws", WSHandler, dict(controller=controller)),
  ])
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(WEBSOCKET_PORT)
  periodicOneSecTimer = tornado.ioloop.PeriodicCallback(controller.on_poll,
                                                        POLLING_INTERVAL_IN_MS)
  periodicOneSecTimer.start()

  def signal_handler(signum, frame):
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(
      tornado.ioloop.IOLoop.instance().stop)
  signal.signal(signal.SIGINT, signal_handler)

  tornado.ioloop.IOLoop.instance().start()

  # controller.__del__() is not called, so we cleanup here.
  controller.compressor = GPIO.LOW
  controller.conveyor = GPIO.LOW
  controller.valve1 = GPIO.LOW
  print "done."
