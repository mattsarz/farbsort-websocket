import fcntl
import os
import time
import threading
import logging


class PRU(object):
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
               if byte == b'\x21':
                    value = "color=blue"
               elif byte == b'\x22':
                    value = "color=red"
               elif byte == b'\x23':
                    value = "color=white"
               elif byte == b'\x30':
                    value = "conveyor=stopped"
               elif byte == b'\x31':
                    value = "conveyor=running"                    
               self._logger.debug("Got {}".format(value.rstrip("\n\r")))
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
