# External module imports
import RPi.GPIO as GPIO #this is needed for powering the GPIO pins
import time #this is needed for the temporizations
import sys #i don't remember what is this one for..
import os #this is needed to remove the file
from time import ctime

# general settings for the program
# Silent the warnings
GPIO.setwarnings(False)
# Setup pins 21 and 17 as output
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT) # this pin is on when the board is working and receiving 24V (green led)
GPIO.setup(17, GPIO.OUT) # this pin is on when we detect no planes (relais AC)
GPIO.setup(27, GPIO.OUT) # this pin is on when the Flash is ON  (red led)
# Initialize pin21 as normally HIGH (--> Flash is OFF, green led ON)
GPIO.output(21, GPIO.HIGH)
# Initialize pin27 as normally LOW (--> Flash is OFF, red led OFF)
GPIO.output(27, GPIO.LOW)
# Initialize pin17 as normally HIGH (--> relay is at rest, flash is ON)
GPIO.output(17, GPIO.HIGH)

GPIO.output(21, GPIO.LOW) #put the pin21 at 0V
GPIO.output(27, GPIO.HIGH)#put the pin27 at 3.3V --> the red LED lights on
GPIO.output(17, GPIO.LOW) #relay at rest --> flash is powered ON

print "test: flash allume"
