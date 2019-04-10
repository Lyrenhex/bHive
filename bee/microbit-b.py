from microbit import *
import machine
import radio

# Define constants
GROUP = 1
ALLOWED_FUNCS = [
    "sum",
    "testPrime",
    "release",
    "hold"
]

# Set up mac address-based unique id
macAddr = machine.unique_id()
macAddr = '{:02x}{:02x}{:02x}{:02x}'.format(macAddr[0], macAddr[1], macAddr[2], macAddr[3])

# Flag denoting whether the worker is currently working for a queen or has been released and is available to pings
heldByQueen = False

# Create list of known prime numbers for this worker
primeNumList = []

# Enable BLE and Display
radio.on()
radio.config(group=GROUP)
display.on()


# Visual marker for when worker is busy computing
def startProcess():
    display.show(Image.SQUARE_SMALL)


# Clears the screen when worker is not computing
def endProcess():
    display.clear()


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


# Tests testNum based on prime factorisation
# If any prime is a factor, then the number is not
# a prime number, so we return False. Else, True.
def testPrime(testStr, *primeStrList):
    testNum = int(testStr)
    primeNumList = [int(n) for n in primeStrList]
    for prime in primeNumList:
        # If mod prime = 0, we aren't a prime
        if (testNum % prime) == 0:
            return (False, testStr)
    return (True, testStr)

# Main loop
while True:
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
                # Compute the task requested (and note that we're busy and haven't broken)
                startProcess()
                response = locals()[params[1]](*params[2:])
                endProcess()

                # If something goes wrong (error, etc), all computations should return None. DO NOT SEND RESULT TO SERVER IF RESULT IS NONE
                if response is not None:
                    sendResponse(params[1], response)
            else:
                sendError(2, "Invalid function '" + params[1] + "'")
