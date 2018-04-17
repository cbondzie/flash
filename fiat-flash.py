# External module imports
import RPi.GPIO as GPIO #this is needed for powering the GPIO pins
import time #this is needed for the temporizations
import sys #i don't remember what is this one for..
import math  #this is needed for the trigonometric functions
import os #this is needed to remove the file
import ephem #this is needed to find out if it is day or night
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
# enter local receiver coordinates (haute borne= 50.604726, 3.155348) and fixed parameters
lat_eolienne = float(50.604726) 
long_eolienne = float(3.155348)
R = 6371 #average earth radius in km
lat_eolienne_Rad = math.radians(lat_eolienne)
long_eolienne_Rad = math.radians(long_eolienne)
limit = 15  #radius of alert in km: a plane is IN --> the flash will light
limit_alti = 0.5  #height of alert in km: a plane is IN --> the flash will light



# test sequence to check the flashes
print "--sequence de test--"
GPIO.output(21, GPIO.LOW) #put the pin21 at 0V
GPIO.output(27, GPIO.HIGH) #put the pin27 at 3.3V --> the red LED lights on
GPIO.output(17, GPIO.LOW) #relay at rest --> flash is powered ON
print "test: flash allume pour 30s..."
time.sleep(30)
GPIO.output(21, GPIO.HIGH) #put the pin21 at 3.3V
GPIO.output(27, GPIO.LOW) #put the pin27 at 0V --> the red LED lights on
GPIO.output(17, GPIO.HIGH) #relay at work --> flash is powered OFF
print "test: flash eteint pour 30s..."
time.sleep(30)
GPIO.output(21, GPIO.LOW) #put the pin21 at 0V
GPIO.output(27, GPIO.HIGH) #put the pin27 at 3.3V --> the red LED lights on
GPIO.output(17, GPIO.LOW) #relay at rest --> flash is powered ON
print "test: flash allume pour 30s..."
time.sleep(10)
GPIO.output(21, GPIO.HIGH) #put the pin21 at 3.3V
GPIO.output(27, GPIO.LOW) #put the pin27 at 0V --> the red LED lights on
GPIO.output(17, GPIO.HIGH) #relay at work --> flash is powered OFF
print "test: flash eteint pour 30s..."
time.sleep(30)
print "--fin du test--"



#general loop for the python program
while 1:

    # in the meantime, find out if it is day or night
    user = ephem.Observer()
    user.lat = repr(lat_eolienne) 
    user.lon = repr(long_eolienne)   
    user.elevation = 0        # if significant, update height here
    next_sunrise_datetime = user.next_rising(ephem.Sun()).datetime()
    next_sunset_datetime = user.next_setting(ephem.Sun()).datetime()
    # If it is nighttime, we will see a sunrise sooner than a sunset.
    it_is_night = next_sunrise_datetime < next_sunset_datetime

    #wait 10 seconds to buffer the file, then read it
    print "scan du ciel, 30 secondes..."
    time.sleep(30)

    try:
        f = open('/home/pi/log_avions.txt')
        distances = [] # we clear the table of the past detected distances
        altitudes = [] # we clear the table of the past detected altitudes
        matches = [] # we clear the table of the past calculated distance*altitude matches

        for linea in f:
            try:
                #split the lines in an array
                vettore = [x for x in linea.split()]
            
                # enter the coordinates and altitude of the detected plane
                lati = float(vettore[1])
                longi = float(vettore[2])
                alti = float(vettore[3])
    
                # calculate distance to the plane
                lati_Rad = math.radians(lati)
                longi_Rad = math.radians(longi)
                y = lati_Rad - lat_eolienne_Rad
                x = (longi_Rad - long_eolienne_Rad) * math.cos((lati_Rad + lat_eolienne_Rad)/2)
                distance = round(R * math.hypot(x,y), 2)
                altitude = round(alti/3208, 2)
                match = distance*altitude
                message = 'distance de l avion appele ' + repr(vettore[0]) + ' = ' + repr(distance) + ' km' + ',  son altitude = ' + repr(altitude) + ' km'
                print message
                distances.append(distance)
                altitudes.append(altitude)
                matches.append(match)

            except IndexError:
                # if we miss altitude, name or coordinates in the message, we don't append anything to the array 'vector' and we skip to the next message
                print "le message de l avion est incomplet"
                 
                
        # check the distance of the plane
        # and to check the altitude activate the alternative line below...
        #if min(matches) < limit*limit_alti:
        # and to check if it is night activate the alternative line below...
        #if min(distances) < limit and it_is_night:
        
        if min(distances) < limit:
            GPIO.output(21, GPIO.LOW) #put the pin21 at 0V
            GPIO.output(27, GPIO.HIGH) #put the pin27 at 3.3V --> the red LED lights on
            GPIO.output(17, GPIO.LOW) #relay at rest --> flash is powered ON
            message2 = 'l avion le plus proche est a ' + repr(min(distances)) + ' km'
            print " "
            print message2
            print ctime()
            print("Il fait nuit." if it_is_night else "Il fait jour.")
            print("#######################################")
            print("### avion dans la zone, fiat flash! ###")
            print("#######################################")
            print(" ")
            print("---------------------------------------")

        else:
            GPIO.output(21, GPIO.HIGH) #put the pin21 at 3.3V
            GPIO.output(27, GPIO.LOW) #put the pin27 at 0V --> the red LED is off 
            GPIO.output(17, GPIO.HIGH) #relay at work --> flash is powered OFF
            message2 = 'l avion le plus proche est a ' + repr(min(distances)) + ' km'
            print " "
            print message2
            print ctime()
            print("Il fait nuit." if it_is_night else "Il fait jour.")
            print("pas d'avion dans la zone, flash eteint.")
            print(" ")
            print("---------------------------------------")

        f.close()
        os.remove('/home/pi/log_avions.txt')

    except IOError:
        print ctime()
        print ("aucun message d'avion recu...")
                
