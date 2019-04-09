from microbit import *
import radio
import os

##########################
## PRIME DEMO FUNCTIONS ##
##########################

#Dictionary of numbers and whether or not they have been found
primes = {}
#Next number to be found
nextNum = 1
#Give a new number to be found
def getNum():
    nextNum += 1
    return(nextNum - 1)

#Split the list of primes into a list of a given number of lists
def splitPrimes(number):
    #Get all prime numbers
    primesTrue = [n for n in primes.keys() if primes[n]]

    #Get average length of the list
    avg = len(primesTrue) / float(number)
    #Start of each slice
    start = 0.0
    output = []

    #While you still can get more numbers
    while start < len(primesTrue):
        output.append(primesTrue[int(start):int(start + avg)])
        start += avg

    return(output)

primes = {2:True, 3:True, 4:False, 5:True}
splitPrimes(2)

### END OF PRIME DEMO FUNCTIONS ##

#List of IDs of all clients
clients = []

#Enabling the display and radio.
display.on()
radio.on()

#Configuring the radio for group 1.
radio.config(group=1)




#Parses errors sent through.
def handleError(code, message):
    display.show("E"+str(code), wait=False)
    sleep(2000)
    display.scroll(message)

#Parsing received parameters.
def parseReceived(input):
    #Extracting parameters from message.
    params = str(input).split(" ")

    #Switching for different commands.
    if params[0] == "pong":
        #Adding ID, if not already in the list.
        if params[1] not in clients:
            clients.append(params[1])

    elif params[0] == "prime":
        #Setting a prime to true if it is prime and false if it is not
        if params[2] not in primes.keys():
            primes[int(params[2])] = params[3]

        #Check for the next prime
        radio.send(params[1] + " check " + getNum())

    if params[0] == "sum":
        #Sum response from a client.
        display.show(params[2], wait=False)
        sleep(5000)
        
        #Remove client from list.
        if (params[1] in clients):
            clients.remove(params[1])

    #Handle error.
    elif params[0] == "err":
        handleError(params[1], " ".join(params[2:]))

#Constantly sending worker_request.
while True:
    #Casting to check for clients.
    if button_a.is_pressed():
        radio.send("ping")

    if button_b.is_pressed():
        if len(clients)>0:
            #clientToSend = clients.copy()[0]
            radio.send(clients[0] + " sum 2 3")

    #Parsing any responses.
    received = radio.receive()
    if received != None:
        parseReceived(received)

    #Showing current number of clients.
    display.clear()
    display.show(str(len(clients)), wait=False)
