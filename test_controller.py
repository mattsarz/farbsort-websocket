from collections import deque
import Queue
import time
import unittest

from controller import Controller
from hal import HAL_simulated as HAL


class TestObserver(object):
  def __init__(self):
    self.updates = []

  def update(self, *args, **kwargs):
    self.updates.append((datetime.datetime.now(), args, kwargs))


class TestBasics(unittest.TestCase):
    def test_instance(self):
        c = Controller(hal=HAL())

    def test_mode_default(self):
        c = Controller(hal=HAL())
        self.assertEqual(c.mode, Controller.MODE_DIAGNOSTIC)

    def test_mode_set(self):
        c = Controller(hal=HAL())
        c.mode = Controller.MODE_NORMAL
        self.assertEqual(c.mode, Controller.MODE_NORMAL)
        c.mode = Controller.MODE_DIAGNOSTIC
        self.assertEqual(c.mode, Controller.MODE_DIAGNOSTIC)
        with self.assertRaises(ValueError):
            c.mode = max(Controller.VALID_CONTROLLER_MODES) + 1

    def test_motor_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(c.motor)
        self.assertFalse(hal.get_output(hal.MOTOR_PIN))

    def test_motor_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        c.motor = True
        self.assertTrue(c.motor)
        self.assertTrue(hal.get_output(hal.MOTOR_PIN))
        c.motor = False
        self.assertFalse(c.motor)
        self.assertFalse(hal.get_output(hal.MOTOR_PIN))

    def test_compressor_default(self):
        c = Controller(hal=HAL())
        self.assertFalse(c.compressor)

    def test_compressor_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        c.compressor = True
        self.assertTrue(c.compressor)
        self.assertTrue(hal.get_output(hal.COMPRESSOR_PIN))
        c.compressor = False
        self.assertFalse(c.compressor)
        self.assertFalse(hal.get_output(hal.COMPRESSOR_PIN))

    def test_valve1_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(c.valve1)
        self.assertFalse(hal.get_output(hal.VALVE1_PIN))

    def test_valve1_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        c.valve1 = True
        self.assertTrue(c.valve1)
        self.assertTrue(hal.get_output(hal.VALVE1_PIN))
        c.valve1 = False
        self.assertFalse(c.valve1)
        self.assertFalse(hal.get_output(hal.VALVE1_PIN))

    def test_valve2_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(c.valve2)
        self.assertFalse(hal.get_output(hal.VALVE2_PIN))

    def test_valve2_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        c.valve2 = True
        self.assertTrue(c.valve2)
        self.assertTrue(hal.get_output(hal.VALVE2_PIN))
        c.valve2 = False
        self.assertFalse(c.valve2)
        self.assertFalse(hal.get_output(hal.VALVE2_PIN))

    def test_valve3_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(c.valve3)
        self.assertFalse(hal.get_output(hal.VALVE3_PIN))

    def test_valve3_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        c.valve3 = True
        self.assertTrue(c.valve3)
        self.assertTrue(hal.get_output(hal.VALVE3_PIN))
        c.valve3 = False
        self.assertFalse(c.valve3)
        self.assertFalse(hal.get_output(hal.VALVE3_PIN))

    def test_pulsecounter_default(self):
        c = Controller(hal=HAL())
        self.assertEquals(c.pulsecounter, 0)

    def test_pulsecounter_increment(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.PULSECOUNTER_PIN, True)
        c.on_poll()
        hal.set_input(hal.PULSECOUNTER_PIN, False)
        c.on_poll()
        self.assertEquals(c.pulsecounter, 1)
        
    def test_pulsecounter_reset(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.PULSECOUNTER_PIN, True)
        c.on_poll()
        hal.set_input(hal.PULSECOUNTER_PIN, False)
        c.on_poll()
        self.assertEquals(c.pulsecounter, 1)
        hal.set_input(hal.LIGHTBARRIER2_PIN, True)
        c.on_poll()
        hal.set_input(hal.LIGHTBARRIER2_PIN, False)
        c.on_poll()
        self.assertEquals(c.pulsecounter, 0)

    def test_lightbarrier1_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(hal.get_input(hal.LIGHTBARRIER1_PIN))
        self.assertFalse(c.lightbarrier1)

    def test_lightbarrier1_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.LIGHTBARRIER1_PIN, True)
        self.assertTrue(c.lightbarrier1)

    def test_lightbarrier2_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(hal.get_input(hal.LIGHTBARRIER2_PIN))
        self.assertFalse(c.lightbarrier2)

    def test_lightbarrier2_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.LIGHTBARRIER2_PIN, True)
        self.assertTrue(c.lightbarrier2)

    def test_lightbarrier3_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(hal.get_input(hal.LIGHTBARRIER3_PIN))
        self.assertFalse(c.lightbarrier3)

    def test_lightbarrier3_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.LIGHTBARRIER3_PIN, True)
        self.assertTrue(c.lightbarrier3)

    def test_lightbarrier4_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(hal.get_input(hal.LIGHTBARRIER4_PIN))
        self.assertFalse(c.lightbarrier4)

    def test_lightbarrier4_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.LIGHTBARRIER4_PIN, True)
        self.assertTrue(c.lightbarrier4)

    def test_lightbarrier5_default(self):
        hal = HAL()
        c = Controller(hal=hal)
        self.assertFalse(hal.get_input(hal.LIGHTBARRIER5_PIN))
        self.assertFalse(c.lightbarrier5)

    def test_lightbarrier5_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.LIGHTBARRIER5_PIN, True)
        self.assertTrue(c.lightbarrier5)

    def test_conveyor_default(self):
        c = Controller(hal=HAL())
        self.assertFalse(c.conveyor)

    def test_conveyor_set(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.PULSECOUNTER_PIN, True)
        c.on_poll()
        hal.set_input(hal.PULSECOUNTER_PIN, False)
        c.on_poll()
        self.assertTrue(c.conveyor)

    def test_conveyor_reset(self):
        hal = HAL()
        c = Controller(hal=hal)
        hal.set_input(hal.PULSECOUNTER_PIN, True)
        c.on_poll()
        hal.set_input(hal.PULSECOUNTER_PIN, False)
        c.on_poll()
        self.assertTrue(c.conveyor)
        time.sleep(2 * Controller.PULSECOUNTER_LAST_CHANGE_TO_TIMEOUT_IN_SECONDS)
        c.on_poll()
        self.assertFalse(c.conveyor)

class TestEventQueue(unittest.TestCase):
    def test_after_init(self):
        event_queue = Queue.Queue()
        hal = HAL()
        c = Controller(hal=hal, event_queue=event_queue)
        self.assertEqual(list(event_queue.queue), ['conveyor=stopped'])

    def test_with_pulsecounter(self):
        event_queue = Queue.Queue()
        hal = HAL()
        c = Controller(hal=hal, event_queue=event_queue)
        hal.set_input(hal.PULSECOUNTER_PIN, True)
        c.on_poll()
        hal.set_input(hal.PULSECOUNTER_PIN, False)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'conveyor=running')
        time.sleep(2 * Controller.PULSECOUNTER_LAST_CHANGE_TO_TIMEOUT_IN_SECONDS)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'conveyor=stopped')

    def test_with_lightbarriers(self):
        event_queue = Queue.Queue()
        hal = HAL()
        c = Controller(hal=hal, event_queue=event_queue)
        hal.set_input(hal.LIGHTBARRIER1_PIN, True)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_16=True')
        hal.set_input(hal.LIGHTBARRIER1_PIN, False)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_16=False')
        hal.set_input(hal.LIGHTBARRIER2_PIN, True)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P9_24=True')
        hal.set_input(hal.LIGHTBARRIER2_PIN, False)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'pulsecounter=0')
        self.assertEqual(event_queue.queue[-2], 'P9_24=False')
        hal.set_input(hal.LIGHTBARRIER3_PIN, True)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_14=True')
        hal.set_input(hal.LIGHTBARRIER3_PIN, False)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_14=False')
        hal.set_input(hal.LIGHTBARRIER4_PIN, True)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_17=True')
        hal.set_input(hal.LIGHTBARRIER4_PIN, False)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_17=False')
        hal.set_input(hal.LIGHTBARRIER5_PIN, True)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_19=True')
        hal.set_input(hal.LIGHTBARRIER5_PIN, False)
        c.on_poll()
        self.assertEqual(event_queue.queue[-1], 'P8_19=False')
