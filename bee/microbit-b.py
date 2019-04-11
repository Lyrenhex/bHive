from microbit import *
import machine
import random
import radio

GROUP = 1
ALLOWED_FUNCS = [
    "sum",
    "testPrime",
    "release",
    "hold",
    "spyRSA"
]

# Set up mac address-based unique id
macAddr = machine.unique_id()
macAddr = '{:02x}{:02x}{:02x}{:02x}'.format(macAddr[0], macAddr[1], macAddr[2], macAddr[3])

# Flag denoting whether the worker is currently working for a queen or has been released and is available to pings
heldByQueen = False

# Create list of known prime numbers for this worker
primeNumList = []

# Enable BLE and Display
def resetRadio():
    radio.on()
    radio.config(channel=7, group=GROUP)
resetRadio()
display.on()


# Visual marker for when worker is busy computing
def startProcess():
    display.show(Image.SQUARE_SMALL)


# Clears the screen when worker is not computing
def endProcess():
    display.clear()

############################
## CLIENT TO SERVER FUNCS ##
############################

# Eavesdrops on the selected channel for a given amount of time.
def spyRSA(channelNum, requestedRunTime):
    runtime = 0
    radio.config(channel=int(channelNum), group=0) 

    while True:
        received = radio.receive()
        if received is not None:
            resetRadio()
            return (True, received)
        if runtime >= int(requestedRunTime):
            resetRadio()
            return False

        runtime += 1
        sleep(1)

#def getQP_RSA(n, *primes):


# Function to send computed function response to Queen, using comms schema
def sendResponse(procName, *responses):
    resp = procName + " " + macAddr
    for val in responses:
        resp += " " + str(val)
    radio.send(resp)


# Sends an error
def sendError(errNum, errMessage):
    radio.send("err " + str(errNum) + " " + str(errMessage))


# Holds the worker
def hold(*args):
    heldByQueen = True
    return heldByQueen


# Releases the worker
def release(*args):
    heldByQueen = False
    return heldByQueen


# Exemplar computation function - sum a and b
def sum(*args):
    if len(args) > 1:
        total = 0
        try:
            for i in args:
                total += int(i)
        except TypeError:
            sendError(1, "Non-integer parameter supplied.")
            return None
        return total
    else:
        sendError(1, "Insufficient number of parameters.")
        return None

# Rabin Miller Primality Test
def rmTest(testStr, certainty):
    testNum = int(testStr)
    # filter out simple primes
    if testNum == 2 or testNum == 3:
        return True
    if testNum < 2 or testNum % 2 == 0 or testNum % 3 == 0:
        return False
    
    d = testNum - 1
    s = 0

    while d % 2 == 0:
        d /= 2
        s += 1
    
    d = int(d)
    
    for i in range(certainty):
        a = random.randint(2, testNum - 2)
        x = (a ** d) % testNum
        if x == 1 or x == testNum - 1:
            continue
        
        r = 1
        while r < s:
            x = (x ** 2) % testNum
            if x == 1:
                return False
            elif x == testNum - 1:
                break
            r += 1
        
        if x != testNum - 1:
            return False
    
    return True

def testPrime(start, numberOfIterations):
    verifiedPrimes = []
    start = int(start)
    for prime in range(int(numberOfIterations)):
        prime = int(prime) + start
        if rmTest(prime, 5):
            verifiedPrimes.append(prime)
    return verifiedPrimes

# Main loop :)
while True:
    if heldByQueen:
        display.show("H")
    else:
        display.clear()

    # Keep polling BLE for data
    recv = radio.receive()
    # If not empty
    if recv is not None:
        # Parse the radio data into something useful
        params = str(recv).split(" ")

        # Queen looking for available workers
        if params[0] == "ping":
            if not heldByQueen:
                # Let them know that we're free and our unique ID for future interaction
                radio.send("pong " + macAddr)
        # Check that the instruction is intended for us
        elif params[0] == macAddr:
            if (params[1] in locals()) and (params[1] in ALLOWED_FUNCS):
                sleep(1000)

                # Compute the task requested (and note that we're busy and haven't broken)
                startProcess()
                response = locals()[params[1]](*params[2:])
                endProcess()

                # If something goes wrong (error, etc), all computations should return None. DO NOT SEND RESULT TO SERVER IF RESULT IS NONE
                if response is not None:
                    if type(response) is tuple or type(response) is list:
                        response = [str(item) for item in response]
                        response = " ".join(response)
                    sendResponse(params[1], response)
                    sleep(10000)
            else:
                sendError(2, "Invalid function '" + params[1] + "'")
