from microbit import *
import radio
import utime
import os

MAX_PRIME = 100
MIN_PRIME = 2

# List of IDs of all clients
clients = []

primes = []

isOccupied = False
global isPolling, pollTime
isPolling = False
pollTime = 0
spyActive = False

nextChannel = 7
channel7Sent = False

# Enabling the display and radio
display.on()
radio.on()

# Configuring the radio for group 1
radio.config(group=1)

def delegatePrimes():
    primesToCheck = MAX_PRIME - MIN_PRIME
    testsPerClient = primesToCheck // len(clients)
    delegatedPrimes = []
    i = MIN_PRIME
    for client in clients:
        primeRange = [i, testsPerClient]
        i += testsPerClient + 1
        delegatedPrimes.append(primeRange)
    diff = (delegatedPrimes[-1][0] + delegatedPrimes[-1][1]) - MAX_PRIME
    delegatedPrimes[-1][1] -= diff

    return delegatedPrimes

def getChannel():
    if nextChannel == 7 and not channel7Sent:
        nextChannel = 0
        channel7Sent = True
        return 7
    elif nextChannel == 7:
        nextChannel = 8
    nextChannel += 1
    return nextChannel - 1

# Parses errors sent through
def handleError(code, message):
    display.show("E"+str(code), wait=False)
    sleep(2000)
    display.scroll(message)

# Removes all clients
def releaseAllClients():
    for client in clients:
        radio.send(client + " release")


# Parsing received parameters
def parseReceived(input):
    # Extracting parameters from message
    params = str(input).split(" ")

    # Switching for different commands
    if params[0] == "pong":
        # Adding ID, if not already in the list
        if params[1] not in clients:
            clients.append(params[1])
            radio.send(params[1] + " hold")
    elif params[0] == "sum":
        # Sum response from a client
        display.show(params[2], wait=False)
        sleep(5000)

        # Remove client from list
        if (params[1] in clients):
            clients.remove(params[1])
    elif params[0] == "testPrime":
        isOccupied = False
        for prime in params[2:]:
            primes.append(int(prime))
    elif params[0] == "spyRSA":
        display.scroll(params[2:])
        if bool(params[2]):
            data = " ".join(params[3:])
            display.scroll(data)
        else:
            display.show('X')
            sleep(1000)
    # Handle error.
    elif params[0] == "err":
        handleError(params[1], " ".join(params[2:]))

# Constantly sending worker_request
while True:
    # Casting to check for clients
    if button_a.is_pressed() and not isPolling:
        radio.send("ping")
        isPolling = True
        spyActive = True
        pollTime = 0
        getWorkers()
    
    if isPolling:
        sleep(1) # sleep 1 ms
        pollTime += 1
        if pollTime >= 200:
            isPolling = False
            pollTime = 0
    
    if spyActive:
        if isReady():
            t = "A"
        display.show(t)

    if spyActive and isReady():
        display.scroll(" spyRSA " + str(getChannel()) + " 20")
        for client in clients:
            radio.send(client + " spyRSA " + str(getChannel()) + " 20000")
        spyActive = False

    if button_b.is_pressed() and not isOccupied:
        isOccupied = True
        if len(clients) > 0:
            primesToTest = delegatePrimes()
            for i, client in enumerate(clients):
                primesToTestList = [str(n) for n in primesToTest[i]]
                primesToTestStr = " ".join(primesToTestList)
                radio.send(client + " testPrime " + primesToTestStr)

    # Parsing any responses
    received = radio.receive()
    if received is not None:
        parseReceived(received)

    # Showing current number of clients
    display.clear()
    display.show(str(len(clients)), wait=False)
