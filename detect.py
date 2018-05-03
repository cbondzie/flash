
# External module imports
import RPi.GPIO as GPIO #this is needed for powering the GPIO pins
import time #this is needed for the temporizations
import sys #i don't remember what is this one for..
import math  #this is needed for the trigonometric functions
import os #this is needed to remove the file
import ephem #this is needed to find out if it is day or night
from time import ctime

# general settings for the program
lat_eolienne = float(50.604726) 
long_eolienne = float(3.155348)
R = 6371 #average earth radius in km
lat_eolienne_Rad = math.radians(lat_eolienne)
long_eolienne_Rad = math.radians(long_eolienne)
limit = 10  #radius of alert in km: a plane is IN --> the flash will light
loop =  0
cycle = 8
compteur_presence = 0
Liste = []
vettore = []
comparaison = 0

while 1:
    Liste = []
    # in the meantime, find out if it is day or night
    user = ephem.Observer()
    user.lat = repr(lat_eolienne) 
    user.lon = repr(long_eolienne)   
    user.elevation = 0        # if significant, update height here
    next_sunrise_datetime = user.next_rising(ephem.Sun()).datetime()
    next_sunset_datetime = user.next_setting(ephem.Sun()).datetime()
    # If it is nighttime, we will see a sunrise sooner than a sunset.
    it_is_night = next_sunrise_datetime < next_sunset_datetime
    #wait 30 seconds to buffer the file, then read it
    print ("scan du ciel, 30 secondes...")
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
                # Ajouter l avion a la liste a comparer
                Liste.append(repr(vettore[0]))
                # calculate distance and the altitude of the plane
                lati_Rad = math.radians(lati)
                longi_Rad = math.radians(longi)
                y = lati_Rad - lat_eolienne_Rad
                x = (longi_Rad - long_eolienne_Rad) * math.cos((lati_Rad + lat_eolienne_Rad)/2)
                distance = round(R * math.hypot(x,y), 2)
                altitude = round(alti/3208, 2)                
                # We pick a plane that fits the condition for being the reference and we lock it
                if loop == 0 and distance < limit :
                    comparaison = repr(vettore[0])
                    loop = 1
                    print (' l avion test est : ' +  repr(vettore[0])) 
                else :
                    pass        
            except IndexError:
                # if we miss altitude, name or coordinates in the message, we don't append anything to the array 'vector' and we skip to the next message
                print ("le message de l avion est incomplet")
        print (Liste)
        if loop >= 1 and loop < cycle : # we verify if there is a test running
            if comparaison in Liste : # If the plane is in the liste then we print the counter and reset it to 0
                print (';'),
                print (compteur_presence)
                compteur_presence = 0
                loop += 1
            else : # if the plane is NOT in the list then we increments the counter, We only print the counter when we see the plane or when the loop stops
                compteur_presence += 1
                loop += 1
                print (' l avion est perdu')
        else : # we print the counter and reset it to 0 cause it means that the loop as either ran off or their is no test going on at the moment
            print (';'),
            print (compteur_presence)
            compteur_presence = 0
            loop = 0
            print (' Nous cherchons un avion test dans la zone')        
        f.close()
        os.remove('/home/pi/log_avions.txt')      
    except IOError:        
       if loop >= 1 and loop < cycle :
            # Rechercher dans la liste la presence de l avion 
            if comparaison in Liste : # If the plane is in the liste then we print the counter and reset it to 0
                print (';'),
                print (compteur_presence)
                compteur_presence = 0
                loop += 1
            else : # if the plane is NOT in the list then we increments the counter, We only print the counter when we see the plane or when the loop stops
                compteur_presence += 1
                loop += 1
                print (' l avion est perdu ')
       else : # we print the counter and reset it to 0 cause it means that the loop as either ran off or their is no test going on at the moment
            print (';'),
            print (compteur_presence)
            compteur_presence = 0
            loop = 0
            print ('Nous cherchons un avion test, pas de message d avion recu')