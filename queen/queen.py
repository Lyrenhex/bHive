from microbit import *
import radio

primes = []
clients = []

#Enabling the display and radio.
display.on()
radio.on()

#Configuring the radio for group 1.
radio.config(group=1)

def received(input):
	id = str(input).split(" ")[0]
	if id not in clients:
		clients.append(id)
	

#Constantly sending worker_request.
while True:
    #Casting to check for clients.
    radio.send("worker_request")
    receive = radio.receive()
    if receive != None:
    	received(receive)