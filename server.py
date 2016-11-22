import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

from controller import Controller
from hal import HAL
from hal import HAL_simulated
from pru import PRU
from pru import PRU_simulated


POLLING_INTERVAL_IN_MS = 1
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
    self._connected = False
    self.eventPostTimer = tornado.ioloop.PeriodicCallback(self.write_out_events, 100)
    self.eventPostTimer.start()

  def open(self):
    print "Connection opened..."
    self._connected = True
    self.write_message("log: Welcome to farbsort control!")
    self._controller.connect()

  def on_message(self, message):
    print ">", message
    self._controller.dispatch_command(message)

  def on_close(self):
    self._controller.disconnect()
    print "Connection closed."

  def check_origin(self, origin):
    return True

  def write_out_events(self):
    try:
      while True:
        event = self._event_listener.events.pop(0)
        print "<", event
        if self._connected:
          self.write_message(event)
    except IndexError:
      pass

  def __del__(self):
    self.eventPostTimer.stop
    print "WSHandler.__del__()..."


if __name__ == "__main__":
  import getpass
  import signal
  import sys

  if getpass.getuser() != "root":
    print >> sys.stderr, "run as root"
    sys.exit(1)

  if "--simulate" in sys.argv[1:]:
    hal = HAL_simulated()
    pru = PRU_simulated()
  else:
    hal = HAL()
    pru = PRU()
  controller = Controller(hal, pru)
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

  tornado.ioloop.IOLoop.instance().add_handler(sys.stdin, controller.on_stdin,
                                               tornado.ioloop.IOLoop.READ)

  def signal_handler(signum, frame):
    print "\nterminating IOLoop..."
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(
      tornado.ioloop.IOLoop.instance().stop)
  signal.signal(signal.SIGINT, signal_handler)

  tornado.ioloop.IOLoop.instance().start()

  # controller.__del__() is not called, so we cleanup here.
  controller.compressor = False
  controller.motor = False
  controller.valve1 = False
  print "done."
