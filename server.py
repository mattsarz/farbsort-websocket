import time

import Adafruit_BBIO.GPIO as GPIO
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

from controller import Controller
from hal import HAL


POLLING_INTERVAL_IN_MS = 1
VALVE_ON_TIME_IN_SECS = .3
WEBSOCKET_PORT = 8888


class EventListener(object):
  def __init__(self):
    self.events = []

  def on_event_received(self, event):
    self.events.append(event)


class WSHandler(tornado.websocket.WebSocketHandler):
  def initialize(self, controller, event_listener):
    self._controller = controller
    self._event_listener = event_listener

  def open(self):
    print "new connection opened"
    self.eventPostTimer = tornado.ioloop.PeriodicCallback(self.write_out_events, 100)
    self.eventPostTimer.start()
    self.write_message("Welcome to farbsort control!")
    self.write_message("motor={}".format("started" if self._controller.motor else "stopped"))
    self.write_message("compressor={}".format("started" if self._controller.compressor else "stopped"))
    self.write_message("lightbarrier1={}".format("on" if self._controller.lightbarrier1 else "off"))
    self.write_message("lightbarrier2={}".format("on" if self._controller.lightbarrier2 else "off"))
    self.write_message("lightbarrier3={}".format("on" if self._controller.lightbarrier3 else "off"))
    self.write_message("lightbarrier4={}".format("on" if self._controller.lightbarrier4 else "off"))
    self.write_message("lightbarrier5={}".format("on" if self._controller.lightbarrier5 else "off"))


  def on_message(self, message):
    print "Got:", message

    if message == "motor.start":
      if self._controller.motor:
        print "motor is already started"
      else:
        print "starting..."
        self.write_message("starting")
        self._controller.motor = GPIO.HIGH
      print "motor.started"
      self.write_message("motor.started")
    elif message == "motor.stop":
      if not self._controller.motor:
        print "motor is already stopped"
      else:
        print "stopping..."
        self.write_message("stopping")
        self._controller.motor = GPIO.LOW
      print "motor.stopped"
      self.write_message("motor.stopped")
    elif message == "valve1.eject":
        print "valve1.on..."
        self._controller.valve1 = GPIO.HIGH
        self.write_message("valve1.ejected")
        time.sleep(VALVE_ON_TIME_IN_SECS)
        print "valve1.off..."
        self._controller.valve1 = GPIO.LOW
    elif message == "valve2.eject":
        print "valve1.on..."
        self._controller.valve2 = GPIO.HIGH
        self.write_message("valve2.ejected")
        time.sleep(VALVE_ON_TIME_IN_SECS)
        print "valve1.off..."
        self._controller.valve2 = GPIO.LOW
    elif message == "valve3.eject":
        print "valve3.on..."
        self._controller.valve3 = GPIO.HIGH
        self.write_message("valve3.ejected")
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
      self.write_message("compressor.started")
    elif message == "compressor.stop":
      if not self._controller.compressor:
        print "compressor is already stopped"
      else:
        print "stopping compressor..."
        self._controller.compressor = GPIO.LOW
      print "compressor stopped"
      self.write_message("compressor.stopped")

  def on_close(self):
    self.eventPostTimer.stop
    print "Connection was closed..."

  def check_origin(self, origin):
    return True

  def write_out_events(self):
    try:
      while True:
        event = self._event_listener.events.pop(0)
        print "posting %s..." % repr(event)
        self.write_message(event)
    except IndexError:
      pass

  def __del__(self):
    print "WSHandler.__del__()..."


if __name__ == "__main__":
  import getpass
  import Queue
  import signal
  import sys

  if getpass.getuser() != "root":
    print >> sys.stderr, "run as root"
    sys.exit(1)

  hal = HAL()
  controller = Controller(hal)
  print "controller initialized"

  event_listener = EventListener()
  controller.register_event_listener(event_listener)
  print "event listener connected"

  application = tornado.web.Application([
    (r"/ws", WSHandler, dict(controller=controller, event_listener=event_listener)),
  ])
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(WEBSOCKET_PORT)
  pollingTimer = tornado.ioloop.PeriodicCallback(controller.on_poll,
                                                 POLLING_INTERVAL_IN_MS)
  pollingTimer.start()

  def signal_handler(signum, frame):
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(
      tornado.ioloop.IOLoop.instance().stop)
  signal.signal(signal.SIGINT, signal_handler)

  tornado.ioloop.IOLoop.instance().start()

  # controller.__del__() is not called, so we cleanup here.
  controller.compressor = GPIO.LOW
  controller.motor = GPIO.LOW
  controller.valve1 = GPIO.LOW
  print "done."
