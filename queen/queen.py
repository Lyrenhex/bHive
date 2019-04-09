from microbit import *
import radio

#Enabling the display and radio.
display.on()
radio.on()

#Configuring the radio for group 1.
radio.config(group=1)

#Constantly sending sum 3 4.
while True:
    #Casting to check for clients.
    radio.send("worker_request")