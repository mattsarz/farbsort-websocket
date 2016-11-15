from collections import deque
import Queue
import time
import unittest

from controller import Controller
from hal import HAL_simulated as HAL
from pru import PRU_simulated as PRU


class EventListener(object):
    def __init__(self):
        self.events = []
    def on_event_received(self, event):
        self.events.append(event)


class TestController(unittest.TestCase):
    def test_instance(self):
        c = Controller(hal=HAL(), pru=PRU())

    def test_after_init(self):
        hal = HAL()
        c = Controller(hal=hal, pru=PRU())
        event_listener = EventListener()
        c.register_event_listener(event_listener)
        c.on_poll()
        expected_events = []
        self.assertEqual(event_listener.events, [])

    def test_after_connect(self):
        hal = HAL()
        c = Controller(hal=hal, pru=PRU())
        event_listener = EventListener()
        c.register_event_listener(event_listener)
        c.connect()
        c.on_poll()
        expected_events = [
          "compressor=stop",
          "lightbarrier3=off",
          "lightbarrier4=off",
          "lightbarrier5=off",
          "motor=stop",
          "valve1=off",
          "valve2=off",
          "valve3=off",
          "mode=normal",
          "sort-order=blue-red-white",
          "controller=stopped",
          "conveyor=stopped",
          "lightbarrier1=off",
          "lightbarrier2=off",
          "emergency-stop=off",
          "connect",
        ]
        self.assertEqual(event_listener.events, expected_events)

    def test_normal_run(self):
        hal = HAL()
        c = Controller(hal=hal, pru=PRU())
        event_listener = EventListener()
        c.register_event_listener(event_listener)
        c.connect()
        c.on_poll()
        c.dispatch_command("compressor=start")
        c.on_poll()
        c.dispatch_command("start")
        c.on_poll()

        c._pru.test_post_event("lightbarrier1=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier1=off")
        c.on_poll()
        c._pru.test_post_event("color=red")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=off")
        c.on_poll()
        c._pru.test_post_event("valve2=on")
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER4, True)
        c.on_poll()
        c._pru.test_post_event("valve2=off")
        c.on_poll()

        c._pru.test_post_event("lightbarrier1=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier1=off")
        c.on_poll()
        c._pru.test_post_event("color=white")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=off")
        c.on_poll()
        c._pru.test_post_event("valve3=on")
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER5, True)
        c.on_poll()
        c._pru.test_post_event("valve3=off")
        c.on_poll()

        c._pru.test_post_event("lightbarrier1=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier1=off")
        c.on_poll()
        c._pru.test_post_event("color=blue")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=off")
        c.on_poll()
        c._pru.test_post_event("valve1=on")
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER3, True)
        c.on_poll()
        c._pru.test_post_event("emergency-stop=on")
        c.on_poll()
        c._pru.test_post_event("motor=stop")
        c.on_poll()
        c._pru.test_post_event("controller=stopped")
        c.on_poll()
        c._pru.test_post_event("valve1=off")
        c.on_poll()
        c._pru.test_post_event("conveyor=stopped")
        c.on_poll()

        expected_events = [
          # connect
          "compressor=stop",
          "lightbarrier3=off",
          "lightbarrier4=off",
          "lightbarrier5=off",
          "motor=stop",
          "valve1=off",
          "valve2=off",
          "valve3=off",
          "mode=normal",
          "sort-order=blue-red-white",
          "controller=stopped",
          "conveyor=stopped",
          "lightbarrier1=off",
          "lightbarrier2=off",
          "emergency-stop=off",
          "connect",
          # compressor start
          "compressor=start",
          # start
          "motor=start",
          "controller=started",
          "start",
          "conveyor=running",
          # put red object on conveyor
          "lightbarrier1=on",
          "lightbarrier1=off",
          "color=red",
          "lightbarrier2=on",
          "lightbarrier2=off",
          "valve2=on",
          "lightbarrier4=on",
          "valve2=off",
          # put white object on conveyor
          "lightbarrier1=on",
          "lightbarrier1=off",
          "color=white",
          "lightbarrier2=on",
          "lightbarrier2=off",
          "valve3=on",
          "lightbarrier5=on",
          "valve3=off",
          # put blue object on conveyor
          "lightbarrier1=on",
          "lightbarrier1=off",
          "color=blue",
          "lightbarrier2=on",
          "lightbarrier2=off",
          "valve1=on",
          "lightbarrier3=on",
          "emergency-stop=on",
          "motor=stop",
          "controller=stopped",
          "valve1=off",
          "conveyor=stopped",
        ]
        
        self.assertEqual(event_listener.events, expected_events)

    def test_diagnostic_run(self):
        hal = HAL()
        c = Controller(hal=hal, pru=PRU())
        event_listener = EventListener()
        c.register_event_listener(event_listener)
        c.connect()
        c.on_poll()
        c.dispatch_command("compressor=start")
        c.on_poll()
        c.dispatch_command("mode=diagnostic")
        c.on_poll()
        c.dispatch_command("motor=start")
        c.on_poll()
        c._pru.test_post_event("lightbarrier1=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier1=off")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=on")
        c.on_poll()
        c._pru.test_post_event("lightbarrier2=off")
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER3, True)
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER4, True)
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER5, True)
        c.on_poll()
        c._pru.test_post_event("emergency-stop=on")
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER3, False)
        c.on_poll()
        c._pru.test_post_event("emergency-stop=off")
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER4, False)
        c.on_poll()
        c._hal.set_input(c._hal.LIGHTBARRIER5, False)
        c.on_poll()
        c.dispatch_command("valve1=on")
        c.on_poll()
        c.dispatch_command("valve1=off")
        c.on_poll()
        c.dispatch_command("valve2=on")
        c.on_poll()
        c.dispatch_command("valve2=off")
        c.on_poll()
        c.dispatch_command("valve3=on")
        c.on_poll()
        c.dispatch_command("valve3=off")
        c.on_poll()
        c.dispatch_command("motor=stop")
        c.on_poll()
        c.dispatch_command("compressor=stop")
        c.on_poll()

        expected_events = [
          "compressor=stop",
          "lightbarrier3=off",
          "lightbarrier4=off",
          "lightbarrier5=off",
          "motor=stop",
          "valve1=off",
          "valve2=off",
          "valve3=off",
          "mode=normal",
          "sort-order=blue-red-white",
          "controller=stopped",
          "conveyor=stopped",
          "lightbarrier1=off",
          "lightbarrier2=off",
          "emergency-stop=off",
          "connect",
          "compressor=start",
          "mode=diagnostic",
          "motor=start",
          "lightbarrier1=on",
          "lightbarrier1=off",
          "lightbarrier2=on",
          "lightbarrier2=off",
          "lightbarrier3=on",
          "lightbarrier4=on",
          "lightbarrier5=on",
          "emergency-stop=on",
          "lightbarrier3=off",
          "emergency-stop=off",
          "lightbarrier4=off",
          "lightbarrier5=off",
          "valve1=on",
          "valve1=off",
          "valve2=on",
          "valve2=off",
          "valve3=on",
          "valve3=off",
          "motor=stop",
          "compressor=stop",
        ]
        self.assertEqual(event_listener.events, expected_events)
