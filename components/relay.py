import socket
import schedule
import datetime
import time
import RPi.GPIO as GPIO
import argparse

# The script as below using BCM GPIO 00..nn numbers
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

lamp_on_times = ["06:30"] # 6:30am
lamp_off_times = ["20:00"] # 8:00pm
pump_on_times = ["17:01","17:03"] # 6:00pm
pump_off_times = ["17:02","17:04"] # 6:01pm

class Relay:

    def __init__(self, label, pin, sched=None ):
        self.label = label
        self.pin = int(pin)
        self.sched = sched

    def _on(self):
        conn = socket.create_connection(("94a66475.carbon.hostedgraphite.com", 2003))
        GPIO.output(self.pin, GPIO.LOW)
        conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.%s 100\n" % self.label)
        conn.close()

    def _off(self):
        conn = socket.create_connection(("94a66475.carbon.hostedgraphite.com", 2003))
        GPIO.output(self.pin, GPIO.HIGH)
        conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.%s 0\n" % self.label)
        conn.close()

    def main(self):
        GPIO.setup( self.pin, GPIO.IN )
        GPIO.setup( self.pin, GPIO.OUT )

        input = GPIO.input( self.pin )

        #if self.toggle:
        #    if GPIO.input( self.pin ) == 0:
        #        self._off()
        #    else:
        #        self._on()

        # loop over times
        if self.sched:
            t = self.sched.split(",")
            start_time = t[0]
            end_time = t[1]
            schedule.every().day.at( start_time ).do( self._on )
            if end_time:
                schedule.every().day.at( end_time ).do( self._off )
            while 1:
                schedule.run_pending()
                time.sleep(1)

if __name__ == '__main__':

  parse = argparse.ArgumentParser()
  parse.add_argument('-l', '--label',
                    action="store", dest="label",
                    help="label")
  parse.add_argument('-p', '--pin',
                    action="store", dest="pin",
                    help="pin")
  parse.add_argument('-s', '--schedule',
                    action="store", dest="sched",
                    help="scheduled times")
  args = parse.parse_args()

  try:
    Relay( args.label, args.pin, args.sched ).main()
  except KeyboardInterrupt:
    pass