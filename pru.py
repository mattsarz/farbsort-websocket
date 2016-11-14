import fcntl
import os
import threading


class PRU(object):
     def __init__(self, verbose=False):
          self._verbose = verbose
          filename="/dev/rpmsg_pru30"
          if self._verbose:
               print "Opening '%s'..." % filename
          while True:
               try:
                    self._f = open(filename, "r+")
               except IOError, err:
                    if str(err).startswith("[Errno 2] No such file or directory"):
                         if self._verbose:
                              print "No such file! Retrying..."
                         time.sleep(1)
                         continue
                    raise
               else:
                    break
          if self._verbose:
               print "ok"

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
               value = self._f.read()
          except IOError, err:
               if str(err) != "[Errno 11] Resource temporarily unavailable":
                    raise
               value = ""
          else:
               if self._verbose:
                    print value.rstrip("\n\r")
          return value

     def write(self, command):
          command = command.rstrip("\n\r")
          command = "%s\r" % command
          if self._verbose:
               print "Sending %s" % repr(command)
          self._f.write(command)

     def stop(self):
          self._thread_exit = True
          self._thread.join()


if __name__ == "__main__":
     import time

     try:
          pru = PRU(verbose=True)
          pru.start()
          pru.write("connect")

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
          print "\nTerminating..."
     finally:
          time.sleep(2)
          GPIO.output("P8_13", GPIO.LOW)
          pru.write("disconnect")
          time.sleep(.1)
          pru.stop()
