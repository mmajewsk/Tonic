import RPi.GPIO as GPIO  # import RPi.GPIO module
from time import sleep  # lets us have a delay

pin=3GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
GPIO.setup(pin, GPIO.OUT)  # set GPIOpin as an output

try:
	while True:
		GPIO.output(pin, 1)  # set GPIOpin to 1/GPIO.HIGH/True
		sleep(0.5)  # wait half a second
		GPIO.output(pin, 0)  # set GPIOpin to 0/GPIO.LOW/False
		sleep(0.5)  # wait half a second

except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
	GPIO.cleanup()