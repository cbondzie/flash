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
limit_alti = 3  #height of alert in km: a plane is IN --> the flash will light
# initialize compteur and tolerance
tolerance = 3
compteur_stop = 0

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
time.sleep(30)
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
    
                # calculate distance and the altitude of the plane
                lati_Rad = math.radians(lati)
                longi_Rad = math.radians(longi)
                y = lati_Rad - lat_eolienne_Rad
                x = (longi_Rad - long_eolienne_Rad) * math.cos((lati_Rad + lat_eolienne_Rad)/2)
                distance = round(R * math.hypot(x,y), 2)
                altitude = round(alti/3208, 2)
                # check if the plane we see is in the area
                if distance < limit and altitude < limit_alti :
                    match = 1
                    message = 'l avion suivant: ' + repr(vettore[0]) + ' est dans la zone, il se trouve à : ' + repr(distance) + ' km' + ',  son altitude est de' + repr(altitude) + ' km'
                else:
                    match = 0
                matches.append(match)

            except IndexError:
                # if we miss altitude, name or coordinates in the message, we don't append anything to the array 'vector' and we skip to the next message
                print "le message de l avion est incomplet"
                 
                
        # check if there is a plane in the area
        
        if max(matches) == 1:
            
            GPIO.output(21, GPIO.LOW) #put the pin21 at 0V
            GPIO.output(27, GPIO.HIGH) #put the pin17 at 3.3V --> the red LED lights on
            GPIO.output(17, GPIO.LOW) #relay at rest --> flash is powered ON
            compteur_stop = 0
            print " "
            print(";"),
            print ctime(),
	    print(";1;"),	
            print("Il fait nuit." if it_is_night else "Il fait jour."),
            print("###  avion dans la zone, fiat flash! ###"),
            print ";",
            print message,
            print ";",
            print matches,
            print("---------------------------------------")

        else:
            if compteur_stop > tolerance:
                
                GPIO.output(21, GPIO.HIGH) #put the pin21 at 3.3V
                GPIO.output(27, GPIO.LOW) #put the pin17 at 0V --> the red LED is off 
                GPIO.output(17, GPIO.HIGH) #relay at work --> flash is powered OFF
                print " "
                print ";",
                print ctime(),
                print(";0;"),
                print("Il fait nuit." if it_is_night else "Il fait jour."),
                print(" pas d'avion dans la zone, flash eteint."),
		print ";",
            	print matches,
                print("---------------------------------------")
            else:
                compteur_stop += 1
                print " "
                print ";",
                print ctime(),
                print(";1;"),
                print("Il fait nuit." if it_is_night else "Il fait jour."),
                print(" pas d'avion dans la zone le flash est allumé,on incremente le compteur")
                print("le compteur vaut : "),
                print compteur_stop,
		print ";",
            	print matches

        f.close()
        os.remove('/home/pi/log_avions.txt')

    except IOError:

        if GPIO.input(21) == 0 :

            if compteur_stop > tolerance :

                    print ";",
                    print ctime(),
                    print (";0;"),
                    print ("aucun message d'avion recu dans la zone depuis 90 secondes le flash s'eteint")
                    GPIO.output(21, GPIO.HIGH) #put the pin21 at 3.3V
                    GPIO.output(27, GPIO.LOW) #put the pin17 at 0V --> the red LED is off 
                    GPIO.output(17, GPIO.HIGH) #relay at work --> flash is powered OFF
            else:
                    print ";",
                    print ctime(),
                    print (";1;"),
                    print ("aucun message d'avion recu... le flash est allume ,incrementation du compteur")
                    compteur_stop += 1
                    print " Le compteur vaut : ",
                    print compteur_stop
        else :
            print ";",
            print ctime(),
            print (";0;"),
            print ("aucun message d'avion recu... le flash est eteint")
            
