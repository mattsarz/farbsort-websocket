import fcntl
import os
import time
import threading
import logging


class PRU(object):
     _infoMapping = {
          0x21: "color=blue",
          0x22: "color=red",
          0x23: "color=white",
          0x30: "conveyor=stopped",
          0x31: "conveyor=running",
          0x32: "lightbarrier1=off",
          0x33: "lightbarrier1=on",
          0x34: "lightbarrier2=off",
          0x35: "lightbarrier2=on",
          0x36: "valve1=on",
          0x37: "valve1=off",
          0x38: "valve2=on",
          0x39: "valve2=off",
          0x3a: "valve3=on",
          0x3b: "valve3=off",
          0x83: "verbose=on",
          0x84: "verbose=off",
          0x85: "mode=normal",
          0x86: "mode=diagnostic",
          0x07: "controller=started",
          0x08: "controller=stopped",
          0x89: "motor=start",
          0x8a: "motor=stop",
          0xa0: "emergency-stop=off",
          0xa1: "emergency-stop=on",
          0xa2: "conveyor=running",
          0xa3: "conveyor=stopped",
     }

     def __init__(self):
          self._logger = logging.getLogger(self.__class__.__name__)
          filename="/dev/rpmsg_pru30"
          self._logger.debug("init: opening '{}'...".format(filename))
          while True:
               try:
                    self._f = open(filename, "rb+")
               except IOError, err:
                    if str(err).startswith("[Errno 2] No such file or directory"):
                         self._logger.debug("No such file! Retrying...")
                         time.sleep(1)
                         continue
                    raise
               else:
                    break
          self._logger.debug("init: done")

          # enable non-blocking access
          fd = self._f.fileno()
          flag = fcntl.fcntl(fd, fcntl.F_GETFL)
          fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)

     def start(self):
          self._thread = threading.Thread()
          self._thread.run = self._run
          self._thread_exit = False
          self._thread.start()

     def _run(self):
          while not self._thread_exit:
               self.read()
               time.sleep(.001)

     def read(self):
          try:
               byte = self._f.read(1)
          except IOError, err:
               if str(err) != "[Errno 11] Resource temporarily unavailable":
                    raise
               value = ""
          else:
               info_code = ord(byte)
               value = self._infoMapping.get(info_code, "")
               if value:
                    self._logger.debug("Got {!r} (0x{:02x})".format(value, ord(byte)))
               else:
                    self._logger.warning("Got unexpected info: 0x{:02x}".format(info_code))
          return value

     def write(self, command):
          #command = command.rstrip("\n\r")
          #command = "{}\r".format(command)
          #self._logger.debug("Sending {}".format(ord(command[0])))
          #self._logger.debug("hurra")
          #self._f.write("Cmd({})".format(ord(command[0])))
          #self._f.write(command[0])
          self._f.write(command)

     def stop(self):
          self._thread_exit = True
          self._thread.join()


class PRU_simulated(object):
     def __init__(self):
          self._events_to_be_read = []

     def read(self):
          if self._events_to_be_read == []:
               return ""
          else:
               value = "\n".join(self._events_to_be_read)
               self._events_to_be_read = []
               return value

     def write(self, command):
          if command == "connect":
               self._events_to_be_read = [
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
          elif command == "start":
               self._events_to_be_read = [
                    "motor=start",
                    "controller=started",
                    "start",
                    "conveyor=running",
               ]
          elif command == "stop":
               self._events_to_be_read = [
                    "motor=stop",
                    "controller=stopped",
                    "stop",
                    "conveyor=stopped",
               ]
          else:
               self._events_to_be_read = [command]


     def test_post_event(self, event):
          self._events_to_be_read = [event]


if __name__ == "__main__":
     import time

     try:
          pru = PRU()
          pru.start()
          pru.write("connect")

          global GPIO
          import Adafruit_BBIO.GPIO as GPIO
          GPIO.setup("P8_13", GPIO.OUT)
          GPIO.output("P8_13", GPIO.HIGH)
          time.sleep(2)

          if False:
               pru.write("mode=diagnostic")
               time.sleep(.1)
               pru.write("motor=start")
               time.sleep(1)
               pru.write("valve1=on")
               time.sleep(.3)
               pru.write("valve1=off")
               time.sleep(1)
               pru.write("valve2=on")
               time.sleep(.3)
               pru.write("valve2=off")
               time.sleep(1)
               pru.write("valve3=on")
               time.sleep(.3)
               pru.write("valve3=off")
               time.sleep(1)
               pru.write("motor=stop")
               time.sleep(1000)
          else:
               pru.write("mode=normal")
               time.sleep(.1)
               pru.write("start")
               time.sleep(1000)
               pru.write("stop")

     except KeyboardInterrupt:
          logging.error("Terminating...")
     finally:
          time.sleep(2)
          GPIO.output("P8_13", GPIO.LOW)
          pru.write("disconnect")
          time.sleep(.1)
          pru.stop()
