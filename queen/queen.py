from microbit import *
import radio
import os

MAX_PRIME = 100

# List of IDs of all clients
clients = []

primes = []

# Enabling the display and radio
display.on()
radio.on()

# Configuring the radio for group 1
radio.config(group=1)

def delegatePrimes(MAX_PRIME):
    primesPerWorker = (MAX_PRIME - 2) // len(clients)
    delegatedPrimes = [[n * primesPerWorker, primesPerWorker] for n in range(len(clients))]
    if primesPerWorker * len(clients) < MAX_PRIME:
        delegatedPrimes[-1][1] += MAX_PRIME - (primesPerWorker * len(clients))
    return delegatedPrimes

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
    elif params[0] == "prime":
        if bool(params[2]):
            primes.append(int(params[3]))
    # Handle error.
    elif params[0] == "err":
        handleError(params[1], " ".join(params[2:]))

# Constantly sending worker_request
while True:
    # Casting to check for clients
    if button_a.is_pressed():
        radio.send("ping")

    if button_b.is_pressed():
        if len(clients) > 0:
            primesToTest = delegatePrimes(MAX_PRIME)
            for i, client in enumerate(clients):
                primesToTestStr = [str(n) for n in primesToTest[i]]
                radio.send(client + " testPrime " + primesToTestStr)

    # Parsing any responses
    received = radio.receive()
    if received is not None:
        parseReceived(received)

    # Showing current number of clients
    display.clear()
    display.show(str(len(clients)), wait=False)
