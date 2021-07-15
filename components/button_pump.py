import RPi.GPIO as GPIO
import time
import argparse
import relay

class Button:

    def __init__(self, label):
        self.label = label
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def press(self):
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        while True:
            input_state = GPIO.input(23)
            if input_state == False:
                print('Button Pressed')
                relay.Relay( self.label, 3 ).main()
                time.sleep(10)

if __name__ == '__main__':

  parse = argparse.ArgumentParser()
  parse.add_argument('-l', '--label',
                    action="store", dest="label",
                    help="label", default="button pump")
  parse.add_argument('-p', '--pin',
                    action="store", dest="pin",
                    help="pin")
  args = parse.parse_args()

  try:
    Button( args.label ).press()
  except KeyboardInterrupt:
    pass